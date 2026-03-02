import httpx
import os
import threading
import asyncio
import time
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.cc_gen import *
from TOOLS.check_all_func import *


def generate_code_blocks(all_cards):
    code_blocks = ""
    cards = all_cards.split('\n')
    for card in cards:
        code_blocks += f"<code>{card}</code>\n"
    return code_blocks


@Client.on_message(filters.command("gen", [".", "/"]))
def multi(client, message):
    t1 = threading.Thread(target=bcall, args=(client, message))
    t1.start()


def bcall(client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(gen_cmd(client, message))
    loop.close()

async def gen_cmd(client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return

        role = checkall[1]

        try:
            ccsdata = message.text.split()[1]
            cc_parts = ccsdata.split("|")
            cc = cc_parts[0]
            mes = cc_parts[1] if len(cc_parts) > 1 else None
            ano = cc_parts[2] if len(cc_parts) > 2 else None
            cvv = cc_parts[3] if len(cc_parts) > 3 else None
        except IndexError:
            resp = f"""
Wrong Format ❌

Usage:
Only Bin
<code>/gen 447697</code>

With Expiration
<code>/gen 447697|12</code>
<code>/gen 447697|12|23</code>

With CVV
<code>/gen 447697|12|23|000</code>

With Custom Amount
<code>/gen 447697 100</code>
"""
            await message.reply_text(resp, message.id)
            return

        amount = 10  # Default amount
        try:
            amount = int(message.text.split()[2])
        except (IndexError, ValueError):
            pass

        delete = await message.reply_text("<b>Generating...</b>", message.id)
        start = time.perf_counter()
        session = httpx.AsyncClient(timeout=30)
        getbin = await get_bin_details(cc[:6])
        await session.aclose()

        brand, type_, level, bank, country, flag, currency = getbin

        if amount > 10000:
            resp = """<b>Limit Reached ⚠️

Message: Maximum Generated Amount is 10K.</b>"""
            await message.reply_text(resp, message.id)
            return

        all_cards = await luhn_card_genarator(cc, mes, ano, cvv, amount)
        if amount == 10:
            resp = (
                f"- 𝐂𝐂 𝐆𝐞𝐧𝐚𝐫𝐚𝐭𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲\n"
                f"- 𝐁𝐢𝐧 - <code>{cc}</code>\n"
                f"- 𝐀𝐦𝐨𝐮𝐧𝐭 - {amount}\n\n"
                f"{generate_code_blocks(all_cards)}"
                f"- 𝗜𝗻𝗳𝗼 - {brand} - {type_} - {level}\n"
                f"- 𝐁𝐚𝐧𝐤 - {bank} 🏛\n"
                f"- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 - {country} - {flag}\n\n"
                f"- 𝐓𝐢𝐦𝐞: - {time.perf_counter() - start:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬\n"
                f"- 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]"
            )
            await client.delete_messages(message.chat.id, delete.id)
            await message.reply_text(resp, message.id)
        else:
            filename = f"downloads/{amount}x_CC_Generated_By_{user_id}.txt"
            with open(filename, "a") as f:
                f.write(f"{all_cards}\n")

            caption = f"""
- 𝐁𝐢𝐧: <code>{cc}</code> 
- 𝐀𝐦𝐨𝐮𝐧𝐭: {amount}

- 𝗜𝗻𝗳𝗼 - {brand} - {type_} - {level}
- 𝐁𝐚𝐧𝐤 - {bank} 🏛  
- 𝐂𝐨𝐮𝐧𝐭𝐫𝐲 - {country} - {flag} - {currency}

- 𝐓𝐢𝐦𝐞 - {time.perf_counter() - start:0.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
- 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - <a href="tg://user?id={message.from_user.id}"> {message.from_user.first_name}</a> ⤿ {role} ⤾
"""
            await client.delete_messages(message.chat.id, delete.id)
            await message.reply_document(document=filename, caption=caption, reply_to_message_id=message.id)
            os.remove(filename)

    except Exception as e:
        await log_cmd_error(message)
