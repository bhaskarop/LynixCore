from pyrogram import Client, filters
from FUNC.admin_auth import is_admin_or_owner
from FUNC.defs import log_cmd_error


@Client.on_message(filters.command("lynix", [".", "/"]))
async def cmd_lynix(Client, message):
    """Secret command — shows all admin commands to owner/admins."""
    try:
        user_id = str(message.from_user.id)

        if not await is_admin_or_owner(user_id):
            return  # Silent — secret command, no error message

        resp = """
╔══════════════════════════╗
     🔐 <b>LYNIX ADMIN PANEL</b>
╚══════════════════════════╝

┌ <b>👑 User Management</b>
├ <code>/pm</code> user_id — Promote to Premium
├ <code>/dm</code> user_id — Demote to Free
├ <code>/getuser</code> user_id — Get User Info
├ <code>/deluser</code> user_id — Delete User
└ <code>/dcredit</code> user_id amt — Direct Credit

┌ <b>📢 Broadcast</b>
└ <code>/brod</code> [reply to msg] — Broadcast

┌ <b>💎 Premium Plans</b>
├ <code>/plan1</code> — Generate Plan 1
├ <code>/plan2</code> — Generate Plan 2
├ <code>/plan3</code> — Generate Plan 3
└ <code>/custom</code> — Custom Plan

┌ <b>🎟️ Gift Codes</b>
├ <code>/gcgen</code> — Generate Gift Code
└ <code>/gcredit</code> — Generate Credit Code

┌ <b>💬 Chat Management</b>
├ <code>/add</code> chat_id — Authorize Chat
├ <code>/delchat</code> chat_id — Remove Chat
└ <code>/filter</code> — Filter Settings

┌ <b>📊 Statistics</b>
├ <code>/stats</code> — Bot Statistics
└ <code>/vps</code> — VPS/Server Stats

┌ <b>🔑 Token Management</b>
├ <code>/updatetoken</code> — Update Tokens
└ <code>/errorlogs</code> — View Error Logs

┌ <b>🔧 System</b>
└ <code>/restart</code> — Restart Bot

┌ <b>👑 Admin Management (Owner Only)</b>
├ <code>/adminadd</code> user_id — Add Admin
├ <code>/adminrm</code> user_id — Remove Admin
└ <code>/admin</code> — List All Admins

<i>⚡ Powered by Lynix Core</i>
"""
        await message.reply_text(resp, reply_to_message_id=message.id)

    except Exception:
        await log_cmd_error(message)
