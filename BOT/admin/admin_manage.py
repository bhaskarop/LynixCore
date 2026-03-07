import json
from pyrogram import Client, filters
from FUNC.admin_auth import is_owner, is_admin_or_owner, add_admin, remove_admin, get_all_admins
from FUNC.defs import log_cmd_error


@Client.on_message(filters.command("adminadd", [".", "/"]))
async def cmd_adminadd(Client, message):
    """Owner-only: Add a new admin."""
    try:
        user_id = str(message.from_user.id)

        if not is_owner(user_id):
            resp = """<b>⛔ Owner-Only Command
Only the bot owner can manage admins.</b>"""
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        # Parse target user
        try:
            if message.reply_to_message:
                target_id = str(message.reply_to_message.from_user.id)
                target_name = message.reply_to_message.from_user.first_name
            else:
                target_id = str(message.text.split(" ")[1])
                target_name = target_id
        except (IndexError, AttributeError):
            resp = """<b>⚠️ Invalid Usage
━━━━━━━━━━━━━━
Usage: <code>/adminadd user_id</code>
Or reply to a user's message.</b>"""
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        if is_owner(target_id):
            resp = "<b>⚠️ The owner cannot be added as an admin.</b>"
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        added = await add_admin(target_id, user_id)

        if added:
            resp = f"""
╔══════════════════════════╗
     ✅ <b>Admin Added</b>
╚══════════════════════════╝

┌ <b>User:</b> <a href="tg://user?id={target_id}">{target_name}</a>
├ <b>User ID:</b> <code>{target_id}</code>
└ <b>Role:</b> Admin

<i>This user can now use all admin commands
except admin management.</i>
"""
        else:
            resp = f"""<b>⚠️ User <code>{target_id}</code> is already an admin.</b>"""

        await message.reply_text(resp, reply_to_message_id=message.id)

    except Exception:
        await log_cmd_error(message)


@Client.on_message(filters.command("adminrm", [".", "/"]))
async def cmd_adminrm(Client, message):
    """Owner-only: Remove an admin."""
    try:
        user_id = str(message.from_user.id)

        if not is_owner(user_id):
            resp = """<b>⛔ Owner-Only Command
Only the bot owner can manage admins.</b>"""
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        # Parse target user
        try:
            if message.reply_to_message:
                target_id = str(message.reply_to_message.from_user.id)
                target_name = message.reply_to_message.from_user.first_name
            else:
                target_id = str(message.text.split(" ")[1])
                target_name = target_id
        except (IndexError, AttributeError):
            resp = """<b>⚠️ Invalid Usage
━━━━━━━━━━━━━━
Usage: <code>/adminrm user_id</code>
Or reply to a user's message.</b>"""
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        removed = await remove_admin(target_id)

        if removed:
            resp = f"""
╔══════════════════════════╗
     ✅ <b>Admin Removed</b>
╚══════════════════════════╝

┌ <b>User:</b> <a href="tg://user?id={target_id}">{target_name}</a>
├ <b>User ID:</b> <code>{target_id}</code>
└ <b>Role:</b> Revoked

<i>This user no longer has admin access.</i>
"""
        else:
            resp = f"""<b>⚠️ User <code>{target_id}</code> is not an admin.</b>"""

        await message.reply_text(resp, reply_to_message_id=message.id)

    except Exception:
        await log_cmd_error(message)


@Client.on_message(filters.command("admin", [".", "/"]))
async def cmd_admin_list(Client, message):
    """Owner-only: List all admins."""
    try:
        user_id = str(message.from_user.id)

        if not is_owner(user_id):
            resp = """<b>⛔ Owner-Only Command
Only the bot owner can view the admin list.</b>"""
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        admins = await get_all_admins()

        if admins:
            admin_lines = "\n".join(
                f'├ <a href="tg://user?id={a["id"]}">{a["id"]}</a>'
                for a in admins
            )
            # Replace last ├ with └
            lines = admin_lines.rsplit("├", 1)
            admin_lines = "└".join(lines)

            resp = f"""
╔══════════════════════════╗
      👑 <b>ADMIN LIST</b>
╚══════════════════════════╝

<b>Total Admins:</b> {len(admins)}

┌ <b>Admins</b>
{admin_lines}
"""
        else:
            resp = """
╔══════════════════════════╗
      👑 <b>ADMIN LIST</b>
╚══════════════════════════╝

<i>No admins added yet.
Use /adminadd to add one.</i>
"""

        await message.reply_text(resp, reply_to_message_id=message.id)

    except Exception:
        await log_cmd_error(message)
