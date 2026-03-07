from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("ac", [".", "/"]))
async def cmd_ac(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        amt             = int(message.text.split(" ")[1])
        user_id         = message.text.split(" ")[2]
        get_info        = await getuserinfo(user_id)
        previous_credit = int(get_info["credit"])
        if previous_credit < 0:
            value = amt
        else:
            value = previous_credit + amt

        await directcredit(user_id, value)

        resp = f"""<b>
Credit Added Successfully ✅ 
━━━━━━━━━━━━━━
Amount : {amt}
User ID: <a href="tg://user?id={user_id}">{user_id}</a> 
Previous Credit: {previous_credit} 
After Credit: {value} 

Message: Credit Added to this User Successfully.
</b>"""
        await message.reply_text(resp, message.id)

    except:
        await log_cmd_error(message)
