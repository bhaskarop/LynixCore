import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.defs import *
from FUNC.usersdb_func import *


@Client.on_message(filters.command("cmds", [".", "/"]))
async def cmd_scr(client, message):
    try:
        WELCOME_TEXT = f"""
<b>Hello <a href="tg://user?id={message.from_user.id}"> {message.from_user.first_name}</a> !

Lynix Core Bot  Has plenty of Commands . We Have Auth Gates , Charge Gates , Tools And Other Things .

Click Each of Them Below to Know Them Better .</b>
        """
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("AUTH/B3/VBV", callback_data="AUTH"),
                InlineKeyboardButton("CHARGE", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("TOOLS", callback_data="TOOLS"),
                InlineKeyboardButton("HELPER", callback_data="HELPER")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await message.reply(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS))

    except Exception:
        await log_cmd_error(message)


async def callback_command(client, message):
    try:
        WELCOME_TEXT = f"""
<b>Hello User !

Lynix Core  Has plenty of Commands . We Have Auth Gates , Charge Gates , Tools And Other Things .

Click Each of Them Below to Know Them Better .</b>
        """
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("AUTH/B3/VBV", callback_data="AUTH"),
                InlineKeyboardButton("CHARGE", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("TOOLS", callback_data="TOOLS"),
                InlineKeyboardButton("HELPER", callback_data="HELPER")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
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
Lynix Core Getting Info  ■□□
      </b>"""
        edit = await message.reply_text(text, message.id)
        await asyncio.sleep(0.5)

        text = """<b>
Lynix Core Getiing Info ■■■
     </b> """
        edit = await Client.edit_message_text(message.chat.id, edit.id, text)
        await asyncio.sleep(0.5)

        text = f"""
<b>🌟 Hello <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>!</b>

<b>Welcome aboard the Lynix Core! 🚀</b>

<b>I am your go-to bot, packed with a variety of gates, tools, and commands to enhance your experience. Excited to see what I can do?</b>

<b>👇 Tap the <i>Register</i> button to begin your journey.</b>
<b>👇 Discover my full capabilities by tapping the <i>Commands</i> button.</b>

"""
        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Register", callback_data="register"),
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
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
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
Registration Successfull ♻️
━━━━━━━━━━━━━━
● Name: {message.from_user.first_name}
● User ID: {message.from_user.id}
● Role: Free
● Credits: 50

Message: You Got 50 Credits as a registration bonus . To Know Credits System /howcrd .

Explore My Various Commands And Abilities By Tapping on Commands Button .  
            </b>"""

        else:
            resp = f"""<b>
Already Registered ⚠️

Message: You are already registered in our bot . No need to register now .

Explore My Various Commands And Abilities By Tapping on Commands Button .  
            </b>"""

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
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
Registration Successfull ♻️
━━━━━━━━━━━━━━
● Name: {message.reply_to_message.from_user.first_name}
● User ID: {user_id}
● Role: Free
● Credits: 50

Message: You Got 50 Credits as a registration bonus . To Know Credits System /howcrd .

Explore My Various Commands And Abilities By Tapping on Commands Button .  
            </b>"""

        else:
            resp = f"""<b>
Already Registered ⚠️

Message: You are already registered in our bot . No need to register now .

Explore My Various Commands And Abilities By Tapping on Commands Button .  
            </b>"""

        await message.reply_text(resp, message.id, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        await log_cmd_error(message)


@Client.on_callback_query()
async def callback_query(Client, CallbackQuery):
    if CallbackQuery.data == "cmds":
        await callback_command(Client, CallbackQuery.message)

    if CallbackQuery.data == "register":
        await callback_register(Client, CallbackQuery.message)

    if CallbackQuery.data == "HOME":
        WELCOME_TEXT = f"""
<b>Hello User!

Lynix Core Has plenty of Commands. We Have Auth Gates, Charge Gates, Tools, And Other Things.

Click Each of Them Below to Know Them Better.</b>
    """
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("AUTH/B3/VBV", callback_data="AUTH"),
                InlineKeyboardButton("CHARGE", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("TOOLS", callback_data="TOOLS"),
                InlineKeyboardButton("HELPER", callback_data="HELPER")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS))

    if CallbackQuery.data == "close":
        await CallbackQuery.message.delete()
        await CallbackQuery.message.reply_text("Enjoy Bro, ")


    if CallbackQuery.data == "AUTH":
        AUTH_TEXT = f"""
<b>Hello User!

Lynix Core  Auth Gates.

Click on each one below to get to know them better. .</b>
    """
        AUTH_BUTTONS = [
            [
                InlineKeyboardButton("Stripe Auth", callback_data="Auth2"),
                InlineKeyboardButton("Adyen Auth", callback_data="Adyen2"),
            ],
            [
                InlineKeyboardButton(
                    "Braintree B3", callback_data="BRAINTREEB3"),

                InlineKeyboardButton(
                    "Braintree VBV", callback_data="BRAINTREEVBV"),
            ],
            [
                InlineKeyboardButton("Back", callback_data="HOME"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=AUTH_TEXT,
            reply_markup=InlineKeyboardMarkup(AUTH_BUTTONS))
    if CallbackQuery.data == "Auth2":
        CHARGE_TEXT = """
🔹 Stripe Auth Gates of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Stripe Auth Options:
   1. Site-Based Auth:
      ➜ Single: /au cc|mm|yy|cvv ✅
      ➜ Mass: /mass cc|mm|yy|cvv ✅

Total Auth Commands: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "Adyen2":
        CHARGE_TEXT = """
🔹 Adyen Auth Gates of Lynix Core
🔹 Status: Inactive ❌

🚀 Quick Commands Overview:

👤 Adyen Auth Options:
   1. Adyen Auth:
      ➜ Single: /ad cc|mm|yy|cvv ❌
      ➜ Mass: /massad cc|mm|yy|cvv ❌

Total Auth Commands: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "BRAINTREEVBV":
        CHARGE_TEXT = """
🔹 Braintree Gates of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Braintree VBV Options:
   1. VBV Lookup Gate:
      ➜ Single: /vbv cc|mm|yy|cvv ✅
      ➜ Mass (Limit=25): /mvbv cc|mm|yy|cvv ✅

Total Auth Commands: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )

    if CallbackQuery.data == "BRAINTREEB3":
        CHARGE_TEXT = """
🔹 Braintree B3 of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Braintree B3 Options:
   1. Braintree B3 Gate:
      ➜ Single: /b3 cc|mm|yy|cvv ✅
      ➜ Mass (Limit=5): /mb3 cc|mm|yy|cvv ✅

Total Commands: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )





    if CallbackQuery.data == "CHARGE":
        CHARGE_TEXT = f"""
<b>Hello User!

Lynix Core Charge Gates.

Click on each one below to get to know them better. .</b>
    """
        
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("SK Based", callback_data="SKBASED"),
                InlineKeyboardButton("Braintree", callback_data="BRAINTREE"),
            ],
            [
                InlineKeyboardButton("Stripe Api", callback_data="SITE"),
                InlineKeyboardButton("Shopify", callback_data="SHOPIFY"),
            ],
            [
                InlineKeyboardButton("Paypal", callback_data="PAYPAL"),
            ],
            [
                InlineKeyboardButton("Back", callback_data="HOME"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTONS))
    if CallbackQuery.data == "PAYPAL":
        CHARGE_TEXT = """
🔹 PayPal Charge Gates of Lynix Core
🔹 Status: ❌ Inactive

🚀 Quick Commands Overview:

👤 PayPal Charge Options:
   1. PayPal Charge 0.1$:
      ➜ Single: /pp cc|mm|yy|cvv [ON] ❌
      ➜ Mass: /mpp cc|mm|yy|cvv [ON] ❌

   2. PayPal Charge 1.50$:
      ➜ Single: /py cc|mm|yy|cvv [OFF] ❌
      ➜ Mass: /mpy cc|mm|yy|cvv [OFF] ❌

Total Auth Commands: 2

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )  


    if CallbackQuery.data == "SKBASED":
        CHARGE_TEXT = """
🔹 Stripe Charge Gates of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Stripe Charge Options:
   1. SK BASED CHARGE 0.5$ CVV:
      ➜ Single: /svv cc|mm|yy|cvv ✅
      ➜ Mass: /msvv cc|mm|yy|cvv ✅
      ➜ Mass txt (Limit=3k): /svvtxt [in reply to file] ✅
      ➜ Self SK also added, check: /selfcmd ✅

   2. SK BASED 0.5$ CCN CHARGE:
      ➜ Single: /ccn cc|mm|yy|cvv ✅
      ➜ Mass: /mccn cc|mm|yy|cvv ✅
      ➜ Mass txt (Limit=3k): /ccntxt [in reply to file] ✅
      ➜ Self SK also added, check: /selfcmd ✅

   3. SK BASED 0.5$ CVV CHARGE:
      ➜ Single: /cvv cc|mm|yy|cvv ✅
      ➜ Mass: /mcvv cc|mm|yy|cvv ✅
      ➜ Mass txt (Limit=3k): /cvvtxt [in reply to file] ✅
      ➜ Self SK also added, check: /selfcmd ✅

Total Charge Commands: 3

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "SITE":
        CHARGE_TEXT = """
🔹 Site Charge Gates of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Site Charge Options:
   1. SITEBASE 1$ CVV CHARGE:
      ➜ Single: /chk cc|mm|yy|cvv ✅
      ➜ Mass: /mchk cc|mm|yy|cvv ✅

Total Charge Commands: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "BRAINTREE":
        CHARGE_TEXT = """
🔹 Braintree Charge Gates of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Braintree Charge Options:
   1. Braintree Charge 1£:
      ➜ Single: /br cc|mm|yy|cvv ✅
      ➜ Mass: /mbr cc|mm|yy|cvv ✅

Total Auth Commands: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "SHOPIFY":
        CHARGE_TEXT = """

🔹 Shopify Charge Gates of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Shopify Charge Options:
   1. Shopify Charge 10$:
      ➜ Single: /sh cc|mm|yy|cvv ✅
      ➜ Mass: /msh cc|mm|yy|cvv ✅

   2. Shopify Charge 1$:
      ➜ Single: /so cc|mm|yy|cvv ✅
      ➜ Mass: /mso cc|mm|yy|cvv ✅

   3. Shopify Charge 25$:
      ➜ Single: /sho cc|mm|yy|cvv ✅
      ➜ Mass: /msho cc|mm|yy|cvv ✅

   4. Shopify Charge 1$:
      ➜ Single: /sg cc|mm|yy|cvv ✅
      ➜ Mass: /msg cc|mm|yy|cvv ✅

Total Auth Commands: 4

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "TOOLS":
        TOOLS_TEXT = f"""
<b>Hello User!

Lynix Core Tools.

Click on each one below to get to know them better..</b>
    """
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("Scrapper", callback_data="SCRAPPER"),
                InlineKeyboardButton("SK TOOLS", callback_data="SKSTOOL"),
            ],
            [
                InlineKeyboardButton(
                    "Genarator", callback_data="GENARATORTOOLS"),
                InlineKeyboardButton(
                    "Bin & Others", callback_data="BINANDOTHERS"),
            ],
            [
                InlineKeyboardButton("Back", callback_data="HOME"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TOOLS_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTONS))

    if CallbackQuery.data == "SKSTOOL":
        CHARGE_TEXT = """
🔹 SK Tools of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 SK Tools:
   1. SK Key Checker Gate: /sk sk_live_xxxxxx ✅ (Limit: Single)
   2. SK To PK Generator Gate: /pk sk_live_xxxxxx ✅ (Limit: Single)
   3. SK User Checker Gate: /skuser sk_live_xxxxxx ✅ (Limit: Single)
   4. SK Info Checker Gate: /skinfo sk_live_xxxxxx ✅ (Limit: Single)

Total Auth Commands: 4

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="TOOLS"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "SCRAPPER":
        CHARGE_TEXT = """
🔹 Scrapper Tools Gates of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Scraper Tools:
   1. CC Scraper Gate: /scr channel_username 100 ✅ (Limit: 5K)
   2. Bin Based CC Scraper Gate: /scrbin 440393 channel_username 100 ✅ (Limit: 5K)
   3. SK Scraper Gate: /scrsk channel_username 100 ✅ (Limit: 5K)

Total Auth Commands: 3

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="TOOLS"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "GENARATORTOOLS":
        CHARGE_TEXT = """
🔹 Generator Tools of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Generator Tools:
   1. Random CC Generator Gate: /gen 440393 500 ✅ (Limit: 10k)
   2. Fake Address Generator Gate: /fake us ✅

Total Auth Commands: 2

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="TOOLS"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "BINANDOTHERS":
        CHARGE_TEXT = """
🔹 Bin and Other Tools Of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 BIN Information:
   1. BIN Info Checker Gate: /bin 440393 ✅ (Single Limit)
   2. Text To CC Filter Gate: /fl [in reply to text] ✅
   3. Mass BIN Info Checker Gate: /massbin 440393 ❌ (Limit: 30)

💡 Additional Tools:
   4. IP Lookup Gate: /ip your_ip ✅
   5. Gateways Hunter: /url website_url ✅ (Limit: 20)
   6. GPT-4: /gpt Promote ❌

Total Auth Commands: 6


"""

        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="TOOLS"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )

    if CallbackQuery.data == "HELPER":
        HELPER_TEXT = f"""
<b>Hello User!

Lynix Core  Helper.

Click on each one below to get to know them better.</b>
    """
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("Helper", callback_data="INFO"),
                # InlineKeyboardButton("SK TOOLS", callback_data="SKTOOLS"),
            ],
            [
                InlineKeyboardButton("Back", callback_data="HOME"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=HELPER_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTONS))
    if CallbackQuery.data == "INFO":
        CHARGE_TEXT = """
🔹 Helper Gates of Lynix Core
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Account Management:
   1. Start Bot: /start
   2. Register: /register
   3. User ID: /id
   4. User Info: /info
   5. Credits Balance: /credits

💡 Credits & Premiums:
   6. Credits System: /howcrd
   7. Premium Privileges: /howpm
   8. Buy Premium: /buy

👥 Community Tools:
   9. Add to Group: /howgp

📡 Tech Support:
   10. Ping Status: /ping

Total Commands: 10

        """

        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="HELPER"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
