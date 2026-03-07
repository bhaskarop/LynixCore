from .func import *
from pyrogram import Client, filters
from FUNC.defs import error_log
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("getplan2", [".", "/"]))
async def cmd_getplan2(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return 
        try:
            amt = int(message.text.split(" ")[1])
        except:
            amt = 10

        text = f"""<b>Giftcode Genarated ✅
Amount: {amt}\n</b>"""
        
        for _ in range(amt):
            GC = f"GRAND-{gcgenfunc()}-{gcgenfunc()}-{gcgenfunc()}-PAA"
            await insert_plan2(GC)
            text += f"""
➔ <code>{GC}</code>
<b>Value : Silver Plan 15 Days</b>\n"""

        text += f"""
<b>For Redeemtion 
Type /redeem GRAND-XXXX-XXXX-XXXX-PAA</b>"""
        
        await message.reply_text(text, message.id)
    except:
        await log_cmd_error(message)
