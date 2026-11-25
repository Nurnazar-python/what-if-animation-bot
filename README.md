# What-If Animation Bot

Automated Telegram → GitHub Actions → YouTube pipeline for What-If animations.

## Architecture

```
Telegram Bot (Activepieces) → GitHub Actions (Cloud) → YouTube
```

## Setup (One-time)

### 1. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `what-if-animation-bot`
3. **Public** (for unlimited free Actions minutes)
4. Don't initialize with README

### 2. Push This Code
```bash
cd what-if-animation-bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/what-if-animation-bot.git
git push -u origin main
```

### 3. Add GitHub Secrets
Go to Settings → Secrets and variables → Actions → New repository secret:

| Secret Name | Value |
|-------------|-------|
| `ELEVENLABS_API_KEY` | From https://elevenlabs.io (free tier: 10k chars/month) |
| `TELEGRAM_BOT_TOKEN` | From @BotFather on Telegram |
| `YOUTUBE_CLIENT_ID` | From Google Cloud Console → OAuth 2.0 Client ID |
| `YOUTUBE_CLIENT_SECRET` | From Google Cloud Console |
| `YOUTUBE_REFRESH_TOKEN` | Run `python get_youtube_token.py` (see below) |

### 4. Get YouTube Refresh Token
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
python get_youtube_token.py
```
Follow the browser auth flow, copy the printed refresh token.

### 5. Create Telegram Bot (Activepieces)
1. In Activepieces: Create flow → Telegram Bot trigger (`new_telegram_message`)
2. Add **AI Text Classifier** piece: Check if message starts with `/what-if`
3. If YES → **HTTP Request** piece: POST to GitHub API
   ```
   POST https://api.github.com/repos/YOUR_USERNAME/what-if-animation-bot/dispatches
   Headers: Authorization: Bearer YOUR_GITHUB_PAT
   Body: {
     "event_type": "render-video",
     "client_payload": {
       "topic": "{{trigger.body.message.text}}",
       "slug": "{{trigger.body.message.text | slugify}}",
       "title": "What If: {{trigger.body.message.text}}",
       "chat_id": "{{trigger.body.message.chat.id}}"
     }
   }
   ```
4. If NO → **AI Chat** piece: Respond as helpful agent
5. Enable flow

### 6. Test
Message your bot on Telegram:
```
/what-if What if you could copy-paste anything?
```

Bot replies:
- 🎬 Starting video creation...
- ✅ voice.mp3 ready (78 credits)
- ✅ Storyboard rendered, animating...
- ✅ Animation complete, uploading to YouTube...
- 🎉 Done! https://youtu.be/abc123

## Local Trigger (Optional)
```bash
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_xxx
export GITHUB_REPO=username/what-if-animation-bot
export TELEGRAM_CHAT_ID=123456789
python trigger.py "What if you could fly?"
```

## Costs (All Free)
- GitHub Actions: 2,000 min/mo (private) / Unlimited (public)
- ElevenLabs: 10,000 chars/mo (~15 videos)
- YouTube API: 10,000 units/day (~6 uploads)
- Activepieces Cloud: Free tier