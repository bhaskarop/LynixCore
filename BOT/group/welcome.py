from pyrogram import Client, filters
import random
import httpx

# API for random anime girl images (SFW)
WAIFU_API_URL = "https://api.waifu.pics/sfw/waifu"

# Fallback images in case API is down
FALLBACK_IMAGES = [
    "https://telegra.ph/file/a5a2bb456bf3eecdbbb99.mp4",
    "https://telegra.ph/file/03c6e49bea9ce6c908b87.mp4",
    "https://telegra.ph/file/9ebf412f09cd7d2ceaaef.mp4",
    "https://telegra.ph/file/293cc10710e57530404f8.mp4",
    "https://telegra.ph/file/506898de518534ff68ba0.mp4",
]

MESSAGE = """<b>
👋 Hey {name}!
Welcome to our group ❤️

📜 Please follow some rules:
1. 🚫 Don't send unwanted links.
2. 🚫 Don't spam.
3. 🚫 Promotion of your channel is prohibited.

✅ Just press /register once to continue using me 🥰
</b>"""

@Client.on_message(filters.new_chat_members)
async def welcome(client, message):
    try:
        new_members = [u.mention for u in message.new_chat_members]
        names = ", ".join(new_members)
        text = MESSAGE.format(name=names)

        img_url = None

        # Try getting a random anime girl image from API
        try:
            async with httpx.AsyncClient(timeout=10) as session:
                resp = await session.get(WAIFU_API_URL)
                data = resp.json()
                img_url = data.get("url")
        except Exception:
            img_url = None

        # Fallback to static list if API fails
        if not img_url:
            img_url = random.choice(FALLBACK_IMAGES)

        # waifu.pics returns images, so send as photo
        await message.reply_photo(photo=img_url, caption=text, quote=True)
    except Exception:
        pass
