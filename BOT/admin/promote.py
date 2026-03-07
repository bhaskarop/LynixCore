from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("pm", [".", "/"]))
async def cmd_pm(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        try:
            if message.reply_to_message:
                user_id = str(message.reply_to_message.from_user.id)
            else:
                user_id = str(message.text.split(" ")[1])
        except:
            user_id = message.reply_to_message.from_user.id

        pm_chk = await getuserinfo(user_id)
        status = str(pm_chk["status"])

        if status != "FREE":
            resp = f"""<b>
Already Promoted ⚠️

User ID: <a href="tg://user?id={user_id}">{user_id}</a> 
Status: Premium

Message: This user is already Premium User . No Need To Promot
e Again .
    </b> """
            await message.reply_text(resp, message.id)

        else:
            await premiumuser(user_id)
            resp = f"""<b>
Premium Activated Successfully ✅ 
━━━━━━━━━━━━━━
User ID : <a href="tg://user?id={user_id}"> {user_id}</a> 
Role :  Premium

Status : Successfull
    </b> """
            await message.reply_text(resp, message.id)

            user_resp = f"""<b>
Account Promoted Successfully ✅ 
━━━━━━━━━━━━━━ 
User ID: {user_id} 
Role: Premium 

Message: Congratz ! Your Account Successfully Promoted To "Premium" User . Enjoy Yourself on the Bot .
    </b> """
            await Client.send_message(user_id, user_resp)

    except:
        await log_cmd_error(message)
