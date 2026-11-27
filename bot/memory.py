"""PostgreSQL conversation memory for the Telegram bot."""
import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

import psycopg2
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger(__name__)

_pool: Optional[SimpleConnectionPool] = None


def get_pool() -> SimpleConnectionPool:
    """Get or create connection pool."""
    global _pool
    if _pool is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL not set")
        _pool = SimpleConnectionPool(1, 5, db_url)
        logger.info("Database pool created")
    return _pool


@contextmanager
def get_conn():
    """Context manager for database connections."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def init_db() -> None:
    """Initialize database tables."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id BIGSERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_conversations_chat_id 
                ON conversations(chat_id);
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS video_tasks (
                    id BIGSERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    slug TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    title TEXT,
                    status TEXT DEFAULT 'pending',
                    workflow_run_id BIGINT,
                    github_run_url TEXT,
                    error TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_video_tasks_chat_id 
                ON video_tasks(chat_id);
            """)
        conn.commit()
    logger.info("Database initialized")


def add_message(chat_id: int, role: str, content: str, metadata: Dict = None) -> None:
    """Store a message in conversation history."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO conversations (chat_id, role, content, metadata) VALUES (%s, %s, %s, %s)",
                (chat_id, role, content, json.dumps(metadata or {}))
            )
        conn.commit()


def get_history(chat_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve recent conversation history."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT role, content, metadata, created_at 
                   FROM conversations 
                   WHERE chat_id = %s 
                   ORDER BY created_at DESC LIMIT %s""",
                (chat_id, limit)
            )
            rows = cur.fetchall()
    return [
        {"role": r[0], "content": r[1], "metadata": r[2], "created_at": r[3]}
        for r in reversed(rows)
    ]


def create_video_task(chat_id: int, slug: str, topic: str, title: str = None) -> int:
    """Create a new video generation task record."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO video_tasks (chat_id, slug, topic, title) 
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (chat_id, slug, topic, title)
            )
            task_id = cur.fetchone()[0]
        conn.commit()
    return task_id


def update_video_task(task_id: int, **fields) -> None:
    """Update video task fields."""
    if not fields:
        return
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [task_id]
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE video_tasks SET {set_clause}, updated_at = NOW() WHERE id = %s",
                values
            )
        conn.commit()


def get_video_task(task_id: int) -> Optional[Dict]:
    """Get video task by ID."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, chat_id, slug, topic, title, status, workflow_run_id, 
                          github_run_url, error, created_at, updated_at
                   FROM video_tasks WHERE id = %s""",
                (task_id,)
            )
            row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row[0], "chat_id": row[1], "slug": row[2], "topic": row[3],
        "title": row[4], "status": row[5], "workflow_run_id": row[6],
        "github_run_url": row[7], "error": row[8], "created_at": row[9], "updated_at": row[10]
    }


def get_latest_task(chat_id: int) -> Optional[Dict]:
    """Get most recent video task for a chat."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, chat_id, slug, topic, title, status, workflow_run_id, 
                          github_run_url, error, created_at, updated_at
                   FROM video_tasks WHERE chat_id = %s 
                   ORDER BY created_at DESC LIMIT 1""",
                (chat_id,)
            )
            row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row[0], "chat_id": row[1], "slug": row[2], "topic": row[3],
        "title": row[4], "status": row[5], "workflow_run_id": row[6],
        "github_run_url": row[7], "error": row[8], "created_at": row[9], "updated_at": row[10]
    }