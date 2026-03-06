import asyncio
import sys, os

# Force UTF-8 output on Windows console
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Fix for Python 3.12+ where get_event_loop() raises RuntimeError
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client 
import json
from FUNC.server_stats import *

plugins = dict(root="BOT")

with open("FILES/config.json", "r", encoding="utf-8") as f:
    DATA      = json.load(f)
    API_ID    = DATA["API_ID"]
    API_HASH  = DATA["API_HASH"]
    BOT_TOKEN = DATA["BOT_TOKEN"]

user = Client( 
            "Scrapper", 
             api_id   = API_ID, 
             api_hash = API_HASH
              )

bot = Client(
    "MY_BOT", 
    api_id    = API_ID, 
    api_hash  = API_HASH, 
    bot_token = BOT_TOKEN, 
    plugins   = plugins 
)



if __name__ == "__main__":
    # send_server_alert()
    print("Done Bot Active ✅")
    print("NOW START BOT ONCE MY MASTER")
    print("Press Ctrl+C to stop the bot\n")

    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user (Ctrl+C) 🛑")
    finally:
        print("Crafted With <3 By Bhaskar")
