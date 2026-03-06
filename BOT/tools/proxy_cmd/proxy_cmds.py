# Crafted With <3 By Bhaskar
from pyrogram import Client, filters
from FUNC.proxydb_func import (
    get_user_proxies,
    add_user_proxies,
    remove_user_proxy,
    remove_all_user_proxies,
)
from TOOLS.check_all_func import check_some_thing
from FUNC.defs import log_cmd_error


@Client.on_message(filters.command("proxy", [".", "/"]))
async def proxy_list_cmd(Client, message):
    try:
        checkall = await check_some_thing(Client, message)
        if checkall[0] is False:
            return

        user_id = str(message.from_user.id)
        proxies = await get_user_proxies(user_id)

        if not proxies:
            await message.reply_text(f"""<b>
𝐏𝐫𝐨𝐱𝐲 𝐌𝐚𝐧𝐚𝐠𝐞𝐫 🌐

No proxies found in your list.

𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:
/addpxy - Add proxies
/rmpxy - Remove proxies
/proxy  - View your proxy list

𝐅𝐨𝐫𝐦𝐚𝐭𝐬 𝐒𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝:
• host:port:user:pass
• user:pass@host:port
• http://user:pass@host:port
• host:port
</b>""", message.id)
            return

        lines = []
        for i, p in enumerate(proxies, 1):
            masked = _mask_proxy(p)
            lines.append(f"<code>{i}</code>. {masked}")

        proxy_list = "\n".join(lines)
        await message.reply_text(f"""<b>
𝐏𝐫𝐨𝐱𝐲 𝐋𝐢𝐬𝐭 🌐 — {len(proxies)} proxies

{proxy_list}

𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:
/addpxy &lt;proxies&gt; - Add more
/rmpxy &lt;index/all&gt; - Remove
</b>""", message.id)

    except Exception:
        await log_cmd_error(message)


@Client.on_message(filters.command("addpxy", [".", "/"]))
async def addpxy_cmd(Client, message):
    try:
        checkall = await check_some_thing(Client, message)
        if checkall[0] is False:
            return

        user_id = str(message.from_user.id)

        raw_text = None
        parts = message.text.split(None, 1)
        if len(parts) > 1:
            raw_text = parts[1]
        if not raw_text:
            try:
                raw_text = message.reply_to_message.text.strip()
            except Exception:
                pass

        if not raw_text:
            await message.reply_text(f"""<b>
𝐀𝐝𝐝 𝐏𝐫𝐨𝐱𝐢𝐞𝐬 🌐

Usage: /addpxy &lt;proxy_lines&gt;
Or reply to a message with proxies.

One proxy per line. Supported formats:
• host:port:user:pass
• user:pass@host:port
• http://user:pass@host:port
• host:port
</b>""", message.id)
            return

        raw_lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        if not raw_lines:
            await message.reply_text("<b>No valid proxy lines found ❌</b>", message.id)
            return

        added, skipped = await add_user_proxies(user_id, raw_lines)
        total = len(await get_user_proxies(user_id))

        await message.reply_text(f"""<b>
𝐏𝐫𝐨𝐱𝐢𝐞𝐬 𝐀𝐝𝐝𝐞𝐝 ✅

Added: {added}
Skipped (invalid/duplicate): {skipped}
Total Proxies: {total}
</b>""", message.id)

    except Exception:
        await log_cmd_error(message)


@Client.on_message(filters.command("rmpxy", [".", "/"]))
async def rmpxy_cmd(Client, message):
    try:
        checkall = await check_some_thing(Client, message)
        if checkall[0] is False:
            return

        user_id = str(message.from_user.id)
        parts = message.text.split()

        if len(parts) < 2:
            await message.reply_text(f"""<b>
𝐑𝐞𝐦𝐨𝐯𝐞 𝐏𝐫𝐨𝐱𝐢𝐞𝐬 🌐

Usage:
/rmpxy all - Remove all proxies
/rmpxy &lt;index&gt; - Remove proxy by index

Use /proxy to see your list with indices.
</b>""", message.id)
            return

        arg = parts[1].strip().lower()

        if arg == "all":
            count = await remove_all_user_proxies(user_id)
            await message.reply_text(
                f"<b>Removed all {count} proxies ✅</b>", message.id
            )
            return

        try:
            idx = int(arg)
        except ValueError:
            await message.reply_text(
                "<b>Invalid index. Use /proxy to see your list ❌</b>", message.id
            )
            return

        removed = await remove_user_proxy(user_id, idx)
        if removed:
            total = len(await get_user_proxies(user_id))
            await message.reply_text(
                f"<b>Proxy #{idx} removed ✅\nRemaining: {total}</b>", message.id
            )
        else:
            await message.reply_text(
                f"<b>Index {idx} out of range. Use /proxy to see your list ❌</b>",
                message.id,
            )

    except Exception:
        await log_cmd_error(message)


def _mask_proxy(url: str) -> str:
    """Mask credentials in proxy URL for display."""
    if "@" in url:
        scheme_rest = url.split("://", 1)
        if len(scheme_rest) == 2:
            scheme, rest = scheme_rest
            creds, host = rest.split("@", 1)
            return f"{scheme}://***:***@{host}"
    return url
