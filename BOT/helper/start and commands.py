import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.defs import *
from FUNC.usersdb_func import *


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Lynix Core — Premium Command Menu
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@Client.on_message(filters.command("cmds", [".", "/"]))
async def cmd_scr(client, message):
    try:
        WELCOME_TEXT = f"""
╔══════════════════════════╗
        ⚡ <b>LYNIX CORE</b> ⚡
╚══════════════════════════╝

<b>Hey <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>!</b> 👋

Your all-in-one CC toolkit.
Select a module below to explore ↴
"""
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("⚔ Auth Gates", callback_data="AUTH"),
                InlineKeyboardButton("💰 Charge Gates", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("🛠 Toolkit", callback_data="TOOLS"),
                InlineKeyboardButton("🎯 Auto Hitter", callback_data="AUTOHITTER")
            ],
            [
                InlineKeyboardButton("📡 Helper", callback_data="HELPER"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await message.reply(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS))

    except Exception:
        await log_cmd_error(message)


async def callback_command(client, message):
    try:
        WELCOME_TEXT = """
╔══════════════════════════╗
        ⚡ <b>LYNIX CORE</b> ⚡
╚══════════════════════════╝

Select a module below to explore ↴
"""
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("⚔ Auth Gates", callback_data="AUTH"),
                InlineKeyboardButton("💰 Charge Gates", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("🛠 Toolkit", callback_data="TOOLS"),
                InlineKeyboardButton("🎯 Auto Hitter", callback_data="AUTOHITTER")
            ],
            [
                InlineKeyboardButton("📡 Helper", callback_data="HELPER"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await message.reply(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS))

    except Exception:
        await log_cmd_error(message)


@Client.on_message(filters.command("start", [".", "/"]))
async def cmd_start(Client, message):
    try:
        text = """<b>
⚡ Lynix Core — Initializing ░░░░░
      </b>"""
        edit = await message.reply_text(text, message.id)
        await asyncio.sleep(0.5)

        text = """<b>
⚡ Lynix Core — Initializing █████
     </b> """
        edit = await Client.edit_message_text(message.chat.id, edit.id, text)
        await asyncio.sleep(0.5)

        text = f"""
╔══════════════════════════╗
        ⚡ <b>LYNIX CORE</b> ⚡
╚══════════════════════════╝

<b>Hey <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>!</b> 👋

<b>Welcome to Lynix Core — your powerful
CC checking & charging toolkit.</b>

<b>⤷ Tap <i>Register</i> to unlock all features
⤷ Tap <i>Commands</i> to see what I can do</b>
"""
        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("📝 Register", callback_data="register"),
                InlineKeyboardButton("📋 Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await Client.edit_message_text(message.chat.id, edit.id, text, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except:
        await log_cmd_error(message)


async def register_user(user_id, username, antispam_time, reg_at):
    info = {
        "id": f"{user_id}",
        "username": f"{username}",
        "user_proxy":f"N/A",
        "dcr": "N/A",
        "dpk": "N/A",
        "dsk": "N/A",
        "amt": "N/A",
        "status": "FREE",
        "plan": f"N/A",
        "expiry": "N/A",
        "credit": "100",
        "antispam_time": f"{antispam_time}",
        "totalkey": "0",
        "reg_at": f"{reg_at}",
    }
    usersdb.insert_one(info)


@Client.on_message(filters.command("register", [".", "/"]))
async def cmd_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("📋 Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""
╔══════════════════════════╗
     ✅ <b>Registration Complete</b>
╚══════════════════════════╝

┌ <b>Name:</b> {message.from_user.first_name}
├ <b>User ID:</b> <code>{message.from_user.id}</code>
├ <b>Role:</b> Free
└ <b>Credits:</b> 50

<i>🎁 You received 50 credits as a welcome bonus!
Use /howcrd to learn about the credits system.</i>
"""

        else:
            resp = f"""
╔══════════════════════════╗
     ⚠️ <b>Already Registered</b>
╚══════════════════════════╝

<i>You're already in the system. No need
to register again.</i>

<i>Tap Commands to explore what I can do.</i>
"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        await log_cmd_error(message)


async def callback_register(Client, message):
    try:
        user_id = str(message.reply_to_message.from_user.id)
        username = str(message.reply_to_message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("📋 Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""
╔══════════════════════════╗
     ✅ <b>Registration Complete</b>
╚══════════════════════════╝

┌ <b>Name:</b> {message.reply_to_message.from_user.first_name}
├ <b>User ID:</b> <code>{user_id}</code>
├ <b>Role:</b> Free
└ <b>Credits:</b> 50

<i>🎁 You received 50 credits as a welcome bonus!
Use /howcrd to learn about the credits system.</i>
"""

        else:
            resp = f"""
╔══════════════════════════╗
     ⚠️ <b>Already Registered</b>
╚══════════════════════════╝

<i>You're already in the system. No need
to register again.</i>

<i>Tap Commands to explore what I can do.</i>
"""

        await message.reply_text(resp, message.id, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        await log_cmd_error(message)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Callback Query Handler
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_callback_query()
async def callback_query(Client, CallbackQuery):

    # ── Navigation ──
    if CallbackQuery.data == "cmds":
        await callback_command(Client, CallbackQuery.message)

    if CallbackQuery.data == "register":
        await callback_register(Client, CallbackQuery.message)

    if CallbackQuery.data == "close":
        await CallbackQuery.message.delete()

    if CallbackQuery.data == "HOME":
        WELCOME_TEXT = """
╔══════════════════════════╗
        ⚡ <b>LYNIX CORE</b> ⚡
╚══════════════════════════╝

Select a module below to explore ↴
"""
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("⚔ Auth Gates", callback_data="AUTH"),
                InlineKeyboardButton("💰 Charge Gates", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("🛠 Toolkit", callback_data="TOOLS"),
                InlineKeyboardButton("🎯 Auto Hitter", callback_data="AUTOHITTER")
            ],
            [
                InlineKeyboardButton("📡 Helper", callback_data="HELPER"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS))


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  ⚔ AUTH GATES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if CallbackQuery.data == "AUTH":
        AUTH_TEXT = """
╔══════════════════════════╗
       ⚔ <b>AUTH GATES</b>
╚══════════════════════════╝

<b>Verify cards without charging.</b>
Select a gate below ↴
"""
        AUTH_BUTTONS = [
            [
                InlineKeyboardButton("⚡ Stripe Auth", callback_data="Auth2"),
                InlineKeyboardButton("🔷 Adyen Auth", callback_data="Adyen2"),
            ],
            [
                InlineKeyboardButton("🌿 Braintree B3", callback_data="BRAINTREEB3"),
                InlineKeyboardButton("🛡 Braintree VBV", callback_data="BRAINTREEVBV"),
            ],
            [
                InlineKeyboardButton("◀ Back", callback_data="HOME"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=AUTH_TEXT,
            reply_markup=InlineKeyboardMarkup(AUTH_BUTTONS))

    if CallbackQuery.data == "Auth2":
        TEXT = """
╔══════════════════════════╗
     ⚡ <b>STRIPE AUTH</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Commands</b>
├ <code>/au</code> cc|mm|yy|cvv — Single ✅
└ <code>/mass</code> cc|mm|yy|cvv — Mass ✅

<i>Total: 2 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="AUTH"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "Adyen2":
        TEXT = """
╔══════════════════════════╗
      🔷 <b>ADYEN AUTH</b>
╚══════════════════════════╝

<b>Status:</b> ❌ Inactive

┌ <b>Commands</b>
├ <code>/ad</code> cc|mm|yy|cvv — Single ❌
└ <code>/massad</code> cc|mm|yy|cvv — Mass ❌

<i>Total: 2 commands (offline)</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="AUTH"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "BRAINTREEVBV":
        TEXT = """
╔══════════════════════════╗
    🛡 <b>BRAINTREE VBV</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Commands</b>
├ <code>/vbv</code> cc|mm|yy|cvv — Single ✅
└ <code>/mvbv</code> cc|mm|yy|cvv — Mass (25) ✅

<i>Total: 2 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="AUTH"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "BRAINTREEB3":
        TEXT = """
╔══════════════════════════╗
     🌿 <b>BRAINTREE B3</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Commands</b>
├ <code>/b3</code> cc|mm|yy|cvv — Single ✅
└ <code>/mb3</code> cc|mm|yy|cvv — Mass (5) ✅

<i>Total: 2 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="AUTH"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  💰 CHARGE GATES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if CallbackQuery.data == "CHARGE":
        CHARGE_TEXT = """
╔══════════════════════════╗
      💰 <b>CHARGE GATES</b>
╚══════════════════════════╝

<b>Charge cards through live gateways.</b>
Select a gate below ↴
"""
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("⚡ SK Based", callback_data="SKBASED"),
                InlineKeyboardButton("🌿 Braintree", callback_data="BRAINTREE"),
            ],
            [
                InlineKeyboardButton("🔗 Stripe API", callback_data="SITE"),
                InlineKeyboardButton("🛒 Shopify", callback_data="SHOPIFY"),
            ],
            [
                InlineKeyboardButton("🅿️ PayPal", callback_data="PAYPAL"),
            ],
            [
                InlineKeyboardButton("◀ Back", callback_data="HOME"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTONS))

    if CallbackQuery.data == "PAYPAL":
        TEXT = """
╔══════════════════════════╗
     🅿️ <b>PAYPAL CHARGE</b>
╚══════════════════════════╝

<b>Status:</b> ❌ Inactive

┌ <b>PayPal $0.1</b>
├ <code>/pp</code> cc|mm|yy|cvv — Single ❌
└ <code>/mpp</code> cc|mm|yy|cvv — Mass ❌

┌ <b>PayPal $1.50</b>
├ <code>/py</code> cc|mm|yy|cvv — Single ❌
└ <code>/mpy</code> cc|mm|yy|cvv — Mass ❌

<i>Total: 4 commands (offline)</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="CHARGE"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "SKBASED":
        TEXT = """
╔══════════════════════════╗
    ⚡ <b>SK BASED CHARGE</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>SK CVV $0.5</b>
├ <code>/svv</code> — Single ✅
├ <code>/msvv</code> — Mass ✅
├ <code>/svvtxt</code> — File (3K) ✅
└ Self SK: /selfcmd ✅

┌ <b>SK CCN $0.5</b>
├ <code>/ccn</code> — Single ✅
├ <code>/mccn</code> — Mass ✅
├ <code>/ccntxt</code> — File (3K) ✅
└ Self SK: /selfcmd ✅

┌ <b>SK CVV $0.5</b>
├ <code>/cvv</code> — Single ✅
├ <code>/mcvv</code> — Mass ✅
├ <code>/cvvtxt</code> — File (3K) ✅
└ Self SK: /selfcmd ✅

<i>Total: 9 commands + self SK</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="CHARGE"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "SITE":
        TEXT = """
╔══════════════════════════╗
    🔗 <b>STRIPE API CHARGE</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Site-Based $1 CVV</b>
├ <code>/chk</code> cc|mm|yy|cvv — Single ✅
└ <code>/mchk</code> cc|mm|yy|cvv — Mass ✅

<i>Total: 2 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="CHARGE"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "BRAINTREE":
        TEXT = """
╔══════════════════════════╗
   🌿 <b>BRAINTREE CHARGE</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Braintree £1</b>
├ <code>/br</code> cc|mm|yy|cvv — Single ✅
└ <code>/mbr</code> cc|mm|yy|cvv — Mass ✅

<i>Total: 2 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="CHARGE"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "SHOPIFY":
        TEXT = """
╔══════════════════════════╗
     🛒 <b>SHOPIFY CHARGE</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Shopify $10</b>
├ <code>/sh</code> cc|mm|yy|cvv — Single ✅
└ <code>/msh</code> cc|mm|yy|cvv — Mass ✅

┌ <b>Shopify $1</b>
├ <code>/so</code> cc|mm|yy|cvv — Single ✅
└ <code>/mso</code> cc|mm|yy|cvv — Mass ✅

┌ <b>Shopify $25</b>
├ <code>/sho</code> cc|mm|yy|cvv — Single ✅
└ <code>/msho</code> cc|mm|yy|cvv — Mass ✅

┌ <b>Shopify $1</b>
├ <code>/sg</code> cc|mm|yy|cvv — Single ✅
└ <code>/msg</code> cc|mm|yy|cvv — Mass ✅

<i>Total: 8 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="CHARGE"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  🛠 TOOLKIT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if CallbackQuery.data == "TOOLS":
        TOOLS_TEXT = """
╔══════════════════════════╗
         🛠 <b>TOOLKIT</b>
╚══════════════════════════╝

<b>Utilities, scrapers, and generators.</b>
Select a category below ↴
"""
        TOOLS_BUTTONS = [
            [
                InlineKeyboardButton("📥 Scrapper", callback_data="SCRAPPER"),
                InlineKeyboardButton("🔑 SK Tools", callback_data="SKSTOOL"),
            ],
            [
                InlineKeyboardButton("🎲 Generator", callback_data="GENARATORTOOLS"),
                InlineKeyboardButton("🔍 Bin & Others", callback_data="BINANDOTHERS"),
            ],
            [
                InlineKeyboardButton("◀ Back", callback_data="HOME"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TOOLS_TEXT,
            reply_markup=InlineKeyboardMarkup(TOOLS_BUTTONS))

    if CallbackQuery.data == "SKSTOOL":
        TEXT = """
╔══════════════════════════╗
       🔑 <b>SK TOOLS</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Commands</b>
├ <code>/sk</code> sk_live_xxx — Key Checker ✅
├ <code>/pk</code> sk_live_xxx — SK→PK Gen ✅
├ <code>/skuser</code> sk_live_xxx — User Checker ✅
└ <code>/skinfo</code> sk_live_xxx — Info Checker ✅

<i>Total: 4 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="TOOLS"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "SCRAPPER":
        TEXT = """
╔══════════════════════════╗
      📥 <b>SCRAPPER</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Commands</b>
├ <code>/scr</code> @channel 100 — CC Scraper (5K) ✅
├ <code>/scrbin</code> 440393 @ch 100 — BIN Scraper (5K) ✅
└ <code>/scrsk</code> @channel 100 — SK Scraper (5K) ✅

<i>Total: 3 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="TOOLS"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "GENARATORTOOLS":
        TEXT = """
╔══════════════════════════╗
      🎲 <b>GENERATORS</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Commands</b>
├ <code>/gen</code> 440393 500 — CC Generator (10K) ✅
└ <code>/fake</code> us — Fake Address Generator ✅

<i>Total: 2 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="TOOLS"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "BINANDOTHERS":
        TEXT = """
╔══════════════════════════╗
    🔍 <b>BIN & OTHER TOOLS</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>BIN Lookup</b>
├ <code>/bin</code> 440393 — BIN Info ✅
├ <code>/fl</code> [reply to text] — CC Filter ✅
└ <code>/massbin</code> 440393 — Mass BIN (30) ❌

┌ <b>Utilities</b>
├ <code>/ip</code> 8.8.8.8 — IP Lookup ✅
├ <code>/url</code> website_url — Gateway Hunter (20) ✅
└ <code>/gpt</code> prompt — GPT-4 ❌

<i>Total: 6 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="TOOLS"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  🎯 AUTO HITTER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if CallbackQuery.data == "AUTOHITTER":
        TEXT = """
╔══════════════════════════╗
      🎯 <b>AUTO HITTER</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

<i>Hit Stripe checkout links directly.
Supports single CC and BIN auto-gen mode.</i>

┌ <b>Commands</b>
├ <code>/hit</code> &lt;url&gt; cc|mm|yy|cvv — Single ✅
└ <code>/hit</code> &lt;url&gt; &lt;BIN&gt; — BIN Mode (10 cards) ✅

┌ <b>Usage</b>
├ URL must be a Stripe checkout link
├ BIN mode generates 10 Luhn-valid cards
└ Shows merchant, price & receipt on hit

<i>Total: 1 command (2 modes)</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="HOME"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  📡 HELPER
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if CallbackQuery.data == "HELPER":
        HELPER_TEXT = """
╔══════════════════════════╗
        📡 <b>HELPER</b>
╚══════════════════════════╝

<b>Account management & info.</b>
Select a category below ↴
"""
        HELPER_BUTTONS = [
            [
                InlineKeyboardButton("👤 Account & Info", callback_data="INFO"),
                InlineKeyboardButton("⚙ Self Config", callback_data="SELFCONFIG"),
            ],
            [
                InlineKeyboardButton("◀ Back", callback_data="HOME"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=HELPER_TEXT,
            reply_markup=InlineKeyboardMarkup(HELPER_BUTTONS))

    if CallbackQuery.data == "INFO":
        TEXT = """
╔══════════════════════════╗
     👤 <b>ACCOUNT & INFO</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Account</b>
├ <code>/start</code> — Start Bot
├ <code>/register</code> — Register
├ <code>/id</code> — Your User ID
├ <code>/info</code> — User Info
└ <code>/credits</code> — Credits Balance

┌ <b>Plans & Credits</b>
├ <code>/howcrd</code> — Credits System
├ <code>/howpm</code> — Premium Privileges
└ <code>/buy</code> — Buy Premium

┌ <b>Community</b>
├ <code>/howgp</code> — Add to Group
└ <code>/ping</code> — Ping Status

<i>Total: 10 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="HELPER"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))

    if CallbackQuery.data == "SELFCONFIG":
        TEXT = """
╔══════════════════════════╗
      ⚙ <b>SELF CONFIG</b>
╚══════════════════════════╝

<b>Status:</b> ✅ Active

┌ <b>Proxy Setup</b>
├ <code>/setproxy</code> ip:port:user:pass ✅
├ <code>/rmproxy</code> — Remove Proxy ✅
└ <code>/viewproxy</code> — View Proxy ✅

┌ <b>Self SK Setup</b>
├ <code>/setsk</code> sk_live_xxx — Set Your SK ✅
├ <code>/mysk</code> — View Your SK ✅
├ <code>/rmsk</code> — Remove Your SK ✅
└ <code>/setamt</code> 5 — Set Charge Amount ✅

┌ <b>Quick Info</b>
├ <code>/selfcmd</code> — Full Self-Cmd Guide ✅
└ Use your own SK for SVV gate

<i>Total: 7 commands</i>
"""
        BUTTONS = [
            [
                InlineKeyboardButton("◀ Back", callback_data="HELPER"),
                InlineKeyboardButton("✖ Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TEXT,
            reply_markup=InlineKeyboardMarkup(BUTTONS))
