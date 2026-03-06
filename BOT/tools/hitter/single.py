# Crafted With <3 By Bhaskar
import time
import asyncio
import re
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from .response import get_hit_resp
from .gate import hit_gate


def _parse_cc(text):
    """Extract (cc, month, year, cvv) from text, or None."""
    pattern = r'(\d{15,18})[\/\s:|-]*?(\d{1,2})[\/\s:|-]*?(\d{2,4})[\/\s:|-]*?(\d{3,4})'
    m = re.search(pattern, text)
    return m.groups() if m else None


@Client.on_message(filters.command("hit", [".", "/"]))
async def hit_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)

        gateway = "Stripe Hit [MO]"
        cmd = "/hit"

        if checkall[0] == False:
            return

        role = checkall[1]

        parts = message.text.split()

        # ── Parse checkout URL ──
        if len(parts) < 2:
            usage = f"""<b>
Gate Name: {gateway} ♻️
CMD: {cmd}

Message: Provide a Stripe checkout URL ❌

Usage: {cmd} &lt;checkout_url&gt; cc|mm|yy|cvv
Or reply to a CC with: {cmd} &lt;checkout_url&gt;</b>"""
            await message.reply_text(usage, message.id)
            return

        checkout_url = parts[1]

        if "checkout.stripe.com" not in checkout_url and "cs_live" not in checkout_url and "cs_test" not in checkout_url:
            await message.reply_text(
                f"<b>Gate Name: {gateway} ♻️\nCMD: {cmd}\n\nMessage: Invalid Stripe checkout URL ❌</b>",
                message.id,
            )
            return

        # ── Parse CC: from 3rd arg, or from reply ──
        cc_tuple = None
        if len(parts) >= 3:
            cc_tuple = _parse_cc(parts[2])
        if not cc_tuple:
            try:
                cc_tuple = _parse_cc(message.reply_to_message.text)
            except Exception:
                pass
        if not cc_tuple:
            usage = f"""<b>
Gate Name: {gateway} ♻️
CMD: {cmd}

Message: No CC Found in your input ❌

Usage: {cmd} &lt;checkout_url&gt; cc|mm|yy|cvv
Or reply to a CC with: {cmd} &lt;checkout_url&gt;</b>"""
            await message.reply_text(usage, message.id)
            return

        cc, mes, ano, cvv = cc_tuple
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"

        # ── Progress messages ──
        firstresp = f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
</b>
"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, message.id)

        secondresp = f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)

        # ── Run gate ──
        start = time.perf_counter()
        proxies = await get_proxy_format()
        result = await hit_gate(cc, mes, ano, cvv, checkout_url, proxy=proxies)

        getbin = await get_bin_details(cc)
        getresp = await get_hit_resp(result, user_id, fullcc)
        status = getresp["status"]
        response = getresp["response"]
        merchant = getresp["merchant"]
        price = getresp["price"]

        thirdresp = f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        brand = getbin[0]
        typee = getbin[1]
        level = getbin[2]
        bank = getbin[3]
        country = getbin[4]
        flag = getbin[5]
        currency = getbin[6]

        finalresp = f"""
{status}

𝗖𝗮𝗿𝗱- <code>{fullcc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲- <i>{gateway}</i>
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞- ⤿ <i>{response}</i> ⤾

𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭- {merchant}
𝐏𝐫𝐢𝐜𝐞- {price}

𝗜𝗻𝗳𝗼- {brand} - {typee} - {level}
𝐁𝐚𝐧𝐤- {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲- {country} - {flag} - {currency}

𝗧𝗶𝗺𝗲- {time.perf_counter() - start:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
</b>
"""
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        await log_cmd_error(message)
