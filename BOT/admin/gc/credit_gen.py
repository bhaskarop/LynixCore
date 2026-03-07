from .func import *
from pyrogram import Client, filters
from FUNC.admin_auth import is_admin_or_owner


@Client.on_message(filters.command("gc", [".", "/"]))
async def generate_gift_codes(client, message):
    """
    Unified gift code generator.
    Usage: /gc {days} {amount}
    Example: /gc 7 5  → generates 5 codes for 7-day plan
    """
    try:
        user_id = str(message.from_user.id)
        if not await is_admin_or_owner(user_id):
            resp = "<b>⛔ Access Denied — Admin only.</b>"
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        args = message.text.split()

        # Parse days
        try:
            days = int(args[1])
        except (IndexError, ValueError):
            resp = """
╔══════════════════════════╗
     🎟️ <b>GIFT CODE GEN</b>
╚══════════════════════════╝

<b>⚠️ Invalid Usage</b>

┌ <b>Format:</b>
├ <code>/gc {days} {amount}</code>
└ <code>/gc {days}</code> (default: 10 codes)

┌ <b>Examples:</b>
├ <code>/gc 7 5</code> → 5 codes for 7 days
├ <code>/gc 15 10</code> → 10 codes for 15 days
└ <code>/gc 30</code> → 10 codes for 30 days
"""
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        if days < 1 or days > 365:
            resp = "<b>⚠️ Days must be between 1 and 365.</b>"
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        # Parse amount
        try:
            amount = int(args[2])
        except (IndexError, ValueError):
            amount = 10

        if amount < 1 or amount > 50:
            resp = "<b>⚠️ Amount must be between 1 and 50.</b>"
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        # Generate codes
        resp = f"""
╔══════════════════════════╗
     🎟️ <b>GIFT CODES</b>
╚══════════════════════════╝

<b>Plan:</b> {days} Days Premium
<b>Amount:</b> {amount} codes

"""
        for i in range(amount):
            code = f"LYNIX-{gcgenfunc()}-{gcgenfunc()}-{gcgenfunc()}"
            await insert_plan_days(code, days)
            resp += f"┌ <code>{code}</code>\n└ <i>{days}-Day Plan</i>\n\n"

        resp += f"""━━━━━━━━━━━━━━━━━━━━━━
<b>How to Redeem:</b>
<code>/redeem LYNIX-XXXXX-XXXXX-XXXXX</code>

<i>Share these codes with users.
Each code can only be redeemed once.</i>
"""
        await message.reply_text(resp, reply_to_message_id=message.id)

    except Exception:
        await log_cmd_error(message)
