from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("get", [".", "/"]))
async def cmd_add(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        info     = await getuserinfo(message.text.split(" ")[1])
        status   = info["status"]
        plan     = info["plan"]
        expiry   = info["expiry"]
        credit   = info["credit"]
        totalkey = info["totalkey"]
        reg_at   = info["reg_at"]

        send_info = f"""<b>
<b>{message.text.split(" ")[1]}</b> Info on Lynix Core ⚡
━━━━━━━━━━━━━━
● ID: <code>{message.text.split(" ")[1]}</code>
● Profile Link: <a href="tg://user?id={message.text.split(" ")[1]}">Profile Link</a>
● Status: {status}
● Credit: {credit}
● Plan: {plan}
● Plan Expiry: {expiry}
● Key Redeemed : {totalkey}
● Registered at: {reg_at}</b>
"""
        await message.reply_text(send_info, message.id)

    except:
        await log_cmd_error(message)
