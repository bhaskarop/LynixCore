from pyrogram import Client, filters
from FUNC.usersdb_func import *


@Client.on_message(filters.command("howpm", [".", "/"]))
async def cmd_howgp(client, message):
    try:
        user_id = str(message.from_user.id)
        texta = f"""<b>
📊 FREE VS PREMIUM VS PAID
━━━━━━━━━━━━━━
➔ <u>STRIPE AUTH GATE (/au)</u>
  ● ANTISPAM:
    FREE - 30s
    PREMIUM - 5s
    PAID - 5s

➔ <u>STRIPE MASS AUTH GATE (/mass)</u>
  ● ANTISPAM:
    FREE - 120s
    PREMIUM - 80s
    PAID - 30s
  ● CHECKING LIMIT:
    FREE - 8
    PREMIUM - 15
    PAID - 25

➔ <u>STRIPE CHARGE GATE (/chk)</u>
  ● ANTISPAM:
    FREE - 30s
    PREMIUM - 5s
    PAID - 5s

➔ <u>STRIPE MASS CHARGE GATE (/mchk)</u>
  ● ANTISPAM:
    FREE - 120s
    PREMIUM - 80s
    PAID - 30s
  ● CHECKING LIMIT:
    FREE - 8
    PREMIUM - 15
    PAID - 25

➔ <u>STRIPE SK BASED CHARGE GATE WITH TXT FILE CHECKING (/cvv sk)</u>
  ● ANTISPAM:
    FREE - 120s
    PREMIUM - 80s
    PAID - 50s
  ● CHECKING LIMIT:
    FREE - 200
    PREMIUM - 1000
    PAID - 1500

➔ <u>CC SCRAPER GATE (/scr)</u>
  ● SCRAPING LIMIT:
    FREE - 3000
    PREMIUM - 6000
    PAID - 12000

➔ <u>CC GENERATOR WITH LUHN ALGO AND CUSTOM AMOUNT GATE (/gen)</u>
  ● GENERATING LIMIT:
    FREE - 2000
    PREMIUM - 4000
    PAID - 10000

➔ <u>STRIPE AUTH GATE (/au)</u>
  ● ANTISPAM:
    FREE - 3
    PREMIUM - 3
    PAID - 3
</b>"""
        await message.reply_text(texta, quote=True)
        await plan_expirychk(user_id)

    except Exception:
        await log_cmd_error(message)
