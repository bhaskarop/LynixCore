from pyrogram import Client, filters
from FUNC.usersdb_func import *


@Client.on_message(filters.command("gethits", [".", "/"]))
async def cmd_buy(Client, message):
    try:
        try:
            user_id = str(message.from_user.id)
            key = message.text.split(" ")[1]
            file = f"HITS/{key}.txt"
            text = f"""<b>HITS File Successfully Retrieved ✅</b>
━━━━━━━━━━━━━━
🆔 <b>Your User ID:</b> <code>{user_id}</code>
🔑 <b>Hits Key:</b> <code>{key}</code>
📄 <b>Status:</b> <code>Successful</code>
━━━━━━━━━━━━━━
"""
            await message.reply_document(
                document=file,
                caption=text,
                reply_to_message_id=message.id
            )
        except Exception:
            await message.reply_text(f"""<b>
File Fetch Failed ❌
━━━━━━━━━━━━━━
Reason: Invalid or Incorrect Secret Key
━━━━━━━━━━━━━━</b>""",
                                    reply_to_message_id=message.id)
    except Exception:
        await log_cmd_error(message)
