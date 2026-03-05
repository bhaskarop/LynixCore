from FUNC.defs import *
from pyrogram import Client, filters
import time


@Client.on_message(filters.command("ping", [".", "/"]))
async def cmd_ping(client, message):
    try:
        start = time.perf_counter()
        resp  = """<b>
🤖 Checking Lynix Core ⚡ Ping...
        </b>"""
        edit  = await message.reply_text(resp, quote=True)
        end   = time.perf_counter()
        
        textb = f"""<b>
🤖 Bot Name: Lynix Core ⚡
✅ Bot Status: Running
📶 Ping: {(end-start)*1000:.2f} ms
        </b>"""
        await client.edit_message_text(message.chat.id, edit.id, textb)

    except Exception:
        await log_cmd_error(message)
