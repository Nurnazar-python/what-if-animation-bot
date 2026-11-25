#!/usr/bin/env python3
"""
Get YouTube refresh token for GitHub Actions.
Run once locally, copy the refresh_token to GitHub Secrets.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    # Download client_secret.json from Google Cloud Console
    # and place it in this directory
    if not os.path.exists("client_secret.json"):
        print("❌ Download client_secret.json from Google Cloud Console")
        print("   https://console.cloud.google.com/apis/credentials")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", SCOPES
    )
    creds = flow.run_local_server(port=0)

    print("\n✅ Add these to GitHub Secrets:")
    print(f"YOUTUBE_CLIENT_ID={creds.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={creds.client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")

    # Save for reference
    with open("youtube_tokens.json", "w") as f:
        json.dump({
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "refresh_token": creds.refresh_token
        }, f, indent=2)

if __name__ == "__main__":
    main()