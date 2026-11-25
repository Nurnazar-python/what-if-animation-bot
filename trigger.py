#!/usr/bin/env python3
"""
Trigger the GitHub Actions workflow from local machine.
Run: python trigger.py "What if you could rewind time?"
"""

import os
import sys
import requests
import slugify

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("GITHUB_REPO")  # e.g., "username/what-if-animation-bot"
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not all([GITHUB_TOKEN, REPO, TELEGRAM_CHAT_ID]):
    print("Set GITHUB_TOKEN, GITHUB_REPO, TELEGRAM_CHAT_ID env vars")
    sys.exit(1)

topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What if you could rewind 10 seconds?"
slug = slugify.slugify(topic)[:50]
title = f"What If: {topic}"

payload = {
    "event_type": "render-video",
    "client_payload": {
        "topic": topic,
        "slug": slug,
        "title": title,
        "chat_id": TELEGRAM_CHAT_ID
    }
}

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.everest-preview+json"
}

response = requests.post(
    f"https://api.github.com/repos/{REPO}/dispatches",
    headers=headers,
    json=payload
)

if response.status_code == 204:
    print(f"✅ Triggered workflow for: {topic}")
    print(f"📺 Watch at: https://github.com/{REPO}/actions")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")