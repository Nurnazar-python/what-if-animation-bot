# Railway Dockerfile for Telegram Bot
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot/ ./bot/

# Expose port (Railway sets PORT env var)
EXPOSE 8080

# Run the bot
CMD ["python", "-m", "bot.main"]