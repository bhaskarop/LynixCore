from FUNC.usersdb_func import *
import time
from FUNC.defs import *

gate_active    = json.loads(open("FILES/deadsk.json", "r" , encoding="utf-8").read())["gate_active"]

REQUIRED_CHANNEL_ID = -1003762736789
REQUIRED_CHANNEL_LINK = "https://t.me/LynixCheckouter"


async def is_channel_member(client, user_id):
    """Check if user has joined the required channel."""
    try:
        member = await client.get_chat_member(REQUIRED_CHANNEL_ID, int(user_id))
        return member.status.name in ("MEMBER", "ADMINISTRATOR", "OWNER")
    except Exception:
        return False

async def check_all_thing(Client , message):
    try:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        user_id   = str(message.from_user.id)
        chat_type = str(message.chat.type)
        chat_id   = str(message.chat.id)
        regdata   = await getuserinfo(user_id)
        regdata   = str(regdata)
        if regdata == "None":
            resp = f"""<b>
Unregistered Users ⚠️

Message: You Can't Use Me Unless You Register First .

Type /register to Continue
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False , False

        if any(command in message.text for command in gate_active):
            resp = "<b>This gate not available now, please try later 👍</b>"
            await message.reply_text(resp, reply_to_message_id=message.id)
            return False, False, False

        getuser        = await getuserinfo(user_id)
        status         = getuser["status"]
        credit         = int(getuser["credit"])
        antispam_time  = int(getuser["antispam_time"])
        now            = int(time.time())
        count_antispam = now - antispam_time
        checkgroup     = await getchatinfo(chat_id)
        checkgroup     = str(checkgroup)
        await plan_expirychk(user_id)

        if chat_type == "ChatType.PRIVATE" and status == "FREE":
            if not await is_channel_member(Client, user_id):
                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                resp = f"""<b>
⚠️ Join Our Channel First!

To use bot in DMs for free, join our channel:
</b>"""
                btn = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Join Channel", url=REQUIRED_CHANNEL_LINK)],
                ])
                await message.reply_text(resp, reply_to_message_id=message.id, reply_markup=btn)
                return False, False, False

        if (
            chat_type == "ChatType.GROUP"
            or chat_type == "ChatType.SUPERGROUP"
            and checkgroup == "None"
        ):
            resp = f"""<b>
Unauthorized Chats ⚠️

Message: Only Chats Approved By My Lynix Can Only Use Me . To Get Approved Your Chats Follow The Steps .

Type /howgp to Know The Step
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if credit < 5:
            resp = f"""<b>
Insufficient Credits ⚠️

Message: You Have Insufficient Credits to Use Me . Recharge Credit For Using Me

Type /buy to Recharge
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if status == "PREMIUM" and count_antispam < 5:
            after = 5 - count_antispam
            resp = f"""<b>
Antispam Detected ⚠️

Message: You Are Doing things Very Fast . Try After {after}s to Use Me Again .

Reduce Antispam Time /buy Using Paid Plan
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if status == "FREE" and count_antispam < 20:
            after = 20 - count_antispam
            resp = f"""<b>
Antispam Detected ⚠️

Message: You Are Doing things Very Fast . Try After {after}s to Use Me Again .

Reduce Antispam Time /buy Using Paid Plan
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        return True , status
    

    except:
        await log_cmd_error(message)
        return False , False 


async def check_some_thing(Client , message):
    try:
        user_id   = str(message.from_user.id)
        chat_type = str(message.chat.type)
        chat_id   = str(message.chat.id)
        regdata   = await getuserinfo(user_id)
        regdata   = str(regdata)
        if regdata == "None":
            resp = f"""<b>
Unregistered Users ⚠️

Message: You Can't Use Me Unless You Register First .

Type /register to Continue
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        getuser    = await getuserinfo(user_id)
        status     = getuser["status"]
        checkgroup = await getchatinfo(chat_id)
        checkgroup = str(checkgroup)
        await plan_expirychk(user_id)

        if chat_type == "ChatType.PRIVATE" and status == "FREE":
            if await is_channel_member(Client, user_id):
                return True, status
            from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            resp = f"""<b>
⚠️ Join Our Channel First!

To use bot in DMs for free, join our channel:
</b>"""
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=REQUIRED_CHANNEL_LINK)],
            ])
            await message.reply_text(resp, reply_to_message_id=message.id, reply_markup=btn)
            return False, False

        if (
            chat_type == "ChatType.GROUP"
            or chat_type == "ChatType.SUPERGROUP"
            and checkgroup == "None"
        ):
            resp = f"""<b>
Unauthorized Chats ⚠️

Message: Only Chats Approved By My Lynix Can Only Use Me . To Get Approved Your Chats Follow The Steps .

Type /howgp to Know The Step
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        return True , status

    except:
        await log_cmd_error(message)
        return False , False

