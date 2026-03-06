import asyncio
import os
import time

# Fix for Python 3.12+ where get_event_loop() raises RuntimeError
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client
from pyrogram.errors import FloodWait
import json
from FUNC.server_stats import *

# Persistent session dir: survives Render redeploys when a disk is mounted
SESSION_DIR = "/app/sessions" if os.path.isdir("/app/sessions") else "."
os.makedirs(SESSION_DIR, exist_ok=True)

plugins = dict(root="BOT")

with open("FILES/config.json", "r", encoding="utf-8") as f:
    DATA      = json.load(f)
    API_ID    = DATA["API_ID"]
    API_HASH  = DATA["API_HASH"]
    BOT_TOKEN = DATA["BOT_TOKEN"]

user = Client(
    os.path.join(SESSION_DIR, "Scrapper"),
    api_id   = API_ID,
    api_hash = API_HASH
)

bot = Client(
    os.path.join(SESSION_DIR, "MY_BOT"),
    api_id    = API_ID,
    api_hash  = API_HASH,
    bot_token = BOT_TOKEN,
    plugins   = plugins
)


if __name__ == "__main__":
    print("Done Bot Active ✅")
    print("NOW START BOT ONCE MY MASTER")

    while True:
        try:
            bot.run()
            break
        except FloodWait as e:
            wait = e.value + 5
            print(f"⚠️ FloodWait: Telegram requires a {e.value}s cooldown. Sleeping {wait}s then retrying...")
            time.sleep(wait)
