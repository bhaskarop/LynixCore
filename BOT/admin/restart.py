import os
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.admin_auth import is_admin_or_owner

@Client.on_message(filters.command("restart", [".", "/"]))
async def cmd_reboot(client, message):
    try:
        user_id = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, message.id)
            return

        await message.reply_text("Clearing cache files and rebooting the system...")
        
        os.system("python3 /root/new/cache_clear.py")
        
        os.system("sudo reboot")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
        await log_cmd_error(message)
