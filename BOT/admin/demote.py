from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("fr", [".", "/"]))
async def cmd_fr(Client, message):
    try:
        user_id     = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        try:
            user_id = str(message.text.split(" ")[1])
        except:
            user_id = message.reply_to_message.from_user.id

        check_premium = await getuserinfo(user_id)
        status        = str(check_premium["status"])
        if status != "PREMIUM":
            resp = f"""<b>
Already Demoted ⚠️

User ID: {user_id}
Status: Free

Message: This user is already Free User . No Need To Demote Again .
        </b>"""
            await message.reply_text(resp, message.id)

        else:
            await freeuser(user_id)
            resp = f"""
Account Demoted ✅

User ID: {user_id}

Message: Account Demoted to "Free" User Successfully .
        """
            await message.reply_text(resp, message.id)

            user_resp = f"""<b>
Account Demoted ❌
━━━━━━━━━━━━━━
● User ID: {user_id}
● Role: Free

Message: Sorry ! Due to Some Suspicious or Wrong Behavior Your Account got Demoted to "Free" User .
            </b>"""
            await Client.send_message(user_id, user_resp)

    except Exception:
        await log_cmd_error(message)
