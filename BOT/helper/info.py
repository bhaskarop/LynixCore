from pyrogram import Client, filters
from FUNC.usersdb_func import *

@Client.on_message(filters.command("info", [".", "/"]))
async def cmd_info(client, message):
    try:
        user_id = str(message.from_user.id)
        regdata = await getuserinfo(user_id)
        results = str(regdata)

        if results == "None":
            resp = """<b>
⚠️ Unregistered User ⚠️

Message: You can't use me unless you register first.

Type /register to continue.
</b>"""
            await message.reply_text(resp)
            return

        if message.reply_to_message:
            user_info = message.reply_to_message.from_user
        else:
            user_info = message.from_user

        user_id = str(user_info.id)
        username = str(user_info.username)
        first_name = str(user_info.first_name)
        results = await getuserinfo(user_id)

        status = results["status"]
        plan = results["plan"]
        expiry = results["expiry"]
        credit = results["credit"]
        totalkey = results["totalkey"]
        reg_at = results["reg_at"]

        send_info = f"""<b>
🔍 Your Info on Lynix Core ⚡
━━━━━━━━━━━━━━
👤 First Name: {first_name}
🆔 ID: <code>{user_id}</code>
📛 Username: @{username}
🔗 Profile Link: <a href="tg://user?id={user_info.id}">Profile Link</a>
🔒 TG Restrictions: {user_info.is_restricted}
🚨 TG Scamtag: {user_info.is_scam}
🌟 TG Premium: {user_info.is_premium}
📋 Status: {status}
💳 Credit: {credit}
💼 Plan: {plan}
📅 Plan Expiry: {expiry}
🔑 Keys Redeemed: {totalkey}
🗓 Registered At: {reg_at}
</b>"""
        await message.reply_text(send_info)

    except Exception as e:
        await log_cmd_error(message)
