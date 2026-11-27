"""Telegram bot handlers and main entry point."""
import os
import time
import logging
from typing import Optional

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from fastapi import FastAPI, Request, Response
import uvicorn

from .ai import ask_ai, ask_ai_with_provider
from .memory import init_db, add_message, get_history, create_video_task, get_latest_task
from .intent import classify_intent
from .dispatcher import VideoDispatcher

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# FastAPI app for webhooks and health checks
app = FastAPI()
dispatcher = VideoDispatcher()

@app.get("/health")
def health():
    """Health check for UptimeRobot."""
    return {"status": "alive", "time": time.time()}

@app.post("/webhook")
async def webhook(request: Request):
    """Entry point for Telegram webhooks."""
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return Response(status_code=200)

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    msg = f"Hello {user_name}! I am your What-If Animation Agent.\n\n" \
          f"You can talk to me about anything, or ask me to create a video.\n" \
          f"Example: 'Hey, can you make a video about what if we lived on Mars?'"
    
    add_message(chat_id, "bot", msg)
    await update.message.reply_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle natural language messages."""
    chat_id = update.effective_chat.id
    text = update.message.text
    
    # Store user message
    add_message(chat_id, "user", text)
    
    # Send typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Classify intent
    intent_data = classify_intent(text)
    intent = intent_data.get("intent", "chat")
    
    if intent == "generate":
        topic = intent_data.get("topic")
        slug = intent_data.get("slug")
        title = intent_data.get("title")
        
        await update.message.reply_text(f"🎬 That sounds like a great idea! Starting video generation for: '{topic}'...")
        
        # Dispatch to GitHub
        res = dispatcher.start(slug, topic, title, chat_id)
        if res["success"]:
            create_video_task(chat_id, slug, topic, title)
            await update.message.reply_text("✅ Workflow dispatched! I'll keep you updated on the progress.")
        else:
            err = res.get("error", "Unknown error")
            await update.message.reply_text(f"❌ Failed to start generation: {err}")
            
    elif intent == "control":
        action = intent_data.get("action")
        if action == "cancel":
            await update.message.reply_text("🛑 Cancelling the current operation...")
            # Note: Implement actual GitHub Action cancellation if needed
        elif action == "status":
            task = get_latest_task(chat_id)
            if task:
                status_msg = f"📺 Latest Task: {task['topic']}\nStatus: {task['status']}\nUpdated: {task['updated_at']}"
                await update.message.reply_text(status_msg)
            else:
                await update.message.reply_text("No active tasks found.")
                
    else: # Default: chat
        history = get_history(chat_id)
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-5:]])
        
        prompt = f"Previous conversation:\n{history_str}\n\nUser: {text}\nBot:"
        system = "You are a helpful and creative What-If Animation Agent. You help the user brainstorm ideas for videos and control the video generation bot."
        
        ai_msg, provider = ask_ai_with_provider(prompt, system=system)
        add_message(chat_id, "bot", ai_msg, metadata={"provider": provider})
        await update.message.reply_text(ai_msg)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    chat_id = update.effective_chat.id
    task = get_latest_task(chat_id)
    if task:
        msg = f"📺 Status for: {task['topic']}\n" \
              f"Current phase: {task['status']}\n" \
              f"Last updated: {task['updated_at']}"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("No active or recent video tasks found.")

# Setup bot application
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set")
    bot_app = None
else:
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("status", status))
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

if __name__ == "__main__":
    # Initialize DB
    try:
        init_db()
    except Exception as e:
        logger.error(f"DB init failed: {e}")
        
    # Start bot
    if bot_app:
        # Note: In production on Railway, we use Webhooks. For local test, use polling.
        if os.getenv("RAILWAY_ENVIRONMENT"):
            # Setup Webhook in Railway
            PORT = int(os.getenv("PORT", 8080))
            DOMAIN = os.getenv("RAILWAY_STATIC_URL", "localhost")
            # bot_app.run_webhook(...) handled via FastAPI entry point in Railway
            uvicorn.run(app, host="0.0.0.0", port=PORT)
        else:
            logger.info("Starting bot polling...")
            bot_app.run_polling()
