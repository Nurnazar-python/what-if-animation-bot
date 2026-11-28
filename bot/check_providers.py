import os, sys, logging
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from bot.ai import get_client

client = get_client()
health = client.health()
for p in health:
    print(f'{p["provider"]}: ready={p["ready"]} disabled={p["disabled"]} key={p["key"]}')