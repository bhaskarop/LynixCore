from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.admin_auth import is_admin_or_owner

@Client.on_message(filters.command("add", [".", "/"]))
async def cmd_add(client, message):
    try:
        user_id = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, quote=True)
            return

        try:
            chat_id = str(message.text.split(" ")[1])
        except IndexError:
            chat_id = str(message.chat.id)

        getchat = await getchatinfo(chat_id)
        getchat = str(getchat)
        
        if getchat == "None":
            await addchat(chat_id)
            resp = (
                "<b>✅ Group Authorized</b>\n\n"
                f"<b>Group Chat ID:</b> <code>{chat_id}</code>\n\n"
                "<i>This group is now authorized to use the bot.</i>"
            )
            await message.reply_text(resp, quote=True)
            
            chat_resp = (
                "<b>✅ Authorized</b>\n\n"
                f"<b>Group Chat ID:</b> <code>{chat_id}</code>\n\n"
                "<i>This group is now authorized to use our bot. Authorized by @bhaskargg.</i>"
            )
            try:
                await client.send_message(chat_id, chat_resp)
            except Exception:
                pass

        else:
            find = await getchatinfo(chat_id)
            find = str(find)
            if find != "None":
                resp = (
                    "<b>⚠️ Already Authorized</b>\n\n"
                    f"<b>Group Chat ID:</b> <code>{chat_id}</code>\n\n"
                    "<i>This group is already authorized to use the bot.</i>"
                )
                await message.reply_text(resp, quote=True)

    except Exception as e:
        await log_cmd_error(message)
