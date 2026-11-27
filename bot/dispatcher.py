"""Dispatch GitHub Actions workflow for video generation."""
import os
import time
import logging
import hashlib
import requests

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("BOT_GITHUB_PAT")


def dispatch_workflow(repo: str, event_type: str, client_payload: dict) -> dict:
    """
    Dispatch a repository_dispatch event to GitHub.
    Returns dict with 'success' bool and 'workflow_run_id' or 'error'.
    """
    if not GITHUB_TOKEN:
        return {"success": False, "error": "GITHUB_TOKEN not set"}

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.everest-preview+json",
        "Content-Type": "application/json",
    }

    payload = {
        "event_type": event_type,
        "client_payload": client_payload
    }

    url = f"{GITHUB_API}/repos/{repo}/dispatches"
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 204:
            return {"success": True, "workflow_run_id": time.time()}
        return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}", "status_code": resp.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_workflow_status(repo: str, run_id: float) -> dict:
    """Get workflow run status from GitHub."""
    if not GITHUB_TOKEN:
        return {"success": False, "error": "GITHUB_TOKEN not set"}

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    url = f"{GITHUB_API}/repos/{repo}/actions/runs?per_page=5"
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            runs = data.get("workflow_runs", [])
            return {"success": True, "runs": runs, "count": len(runs)}
        return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


class VideoDispatcher:
    """Handles video workflow dispatch with retry logic."""

    def __init__(self, repo: str = None):
        self.repo = repo or os.getenv("GITHUB_REPO", "Nurnazar-python/what-if-animation-bot")

    def start(self, slug: str, topic: str, title: str, chat_id: int) -> dict:
        """Start video generation workflow."""
        payload = {
            "slug": slug,
            "topic": topic,
            "title": title,
            "chat_id": str(chat_id),
        }

        result = dispatch_workflow(self.repo, "render-video", payload)
        if result["success"]:
            logger.info(f"Workflow dispatched for {slug}")
        else:
            logger.error(f"Failed to dispatch workflow: {result.get('error')}")
        return result

    def check_status(self) -> dict:
        """Check recent workflow runs."""
        return get_workflow_status(self.repo, None)