from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("cs", [".", "/"]))
async def cmd_cs(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        user_id , module , value = message.text.split(" ")
        await updateuserinfo(user_id, module, value)

        resp = f"""<b>
Custom Info Changed ✅
━━━━━━━━━━━━━━
User_ID : {user_id}
Key_Name : {module}
Key_Value : {value}

Status: Successfull
</b> """
        await message.reply_text(resp, message.id)

    except:
        await log_cmd_error(message)
