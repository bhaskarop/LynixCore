# Crafted With <3 By Bhaskar
from FUNC.defs import refundcredit


async def get_hit_resp(result_tuple, user_id, fullcc):
    """
    Parse the (status, msg, extra) tuple from stripe_gate
    and return a dict with status/response/hits for the /hit command.
    Logging is handled by the caller (single.py) for full context.
    """
    try:
        gate_status, gate_msg, extra = result_tuple
        merchant = extra.get("merchant", "N/A")
        price = extra.get("price", "N/A")
        product = extra.get("product", "N/A")
        receipt = extra.get("receipt", "N/A")
        gs = gate_status.lower()

        if "charged" in gs:
            status = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            response = "Charged Successfully"
            hits = "YES"

        elif "live" in gs:
            status = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ❎"
            response = gate_msg
            hits = "YES"

        elif "3ds" in gs or "🔐" in gate_status:
            status = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ❎"
            response = gate_msg
            hits = "YES"

        else:
            status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
            response = gate_msg
            hits = "NO"

            if "proxy" in gate_msg.lower():
                await refundcredit(user_id)

        return {
            "status": status,
            "response": response,
            "hits": hits,
            "fullz": fullcc,
            "merchant": merchant,
            "price": price,
            "product": product,
            "receipt": receipt,
        }

    except Exception as e:
        return {
            "status": "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌",
            "response": str(e)[:120] + " ❌",
            "hits": "NO",
            "fullz": fullcc,
            "merchant": "N/A",
            "price": "N/A",
            "product": "N/A",
            "receipt": "N/A",
        }
