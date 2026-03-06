# Crafted With <3 By Bhaskar
from FUNC.defs import forward_resp, refundcredit


async def get_hit_resp(result_tuple, user_id, fullcc):
    """
    Parse the (status, msg, extra) tuple from stripe_gate
    and return a dict with status/response/hits for the /hit command.
    """
    try:
        gate_status, gate_msg, extra = result_tuple
        merchant = extra.get("merchant", "N/A")
        price = extra.get("price", "N/A")
        product = extra.get("product", "N/A")

        if gate_status == "Charged":
            status = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            response = f"Charged Successfully"
            hits = "YES"
            await forward_resp(fullcc, "Stripe Hit [MO]", response)

        elif gate_status == "Live":
            status = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ❎"
            response = gate_msg
            hits = "YES"
            await forward_resp(fullcc, "Stripe Hit [MO]", response)

        elif gate_status == "3DS":
            status = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ❎"
            response = "OTP Required"
            hits = "YES"
            await forward_resp(fullcc, "Stripe Hit [MO]", response)

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
        }
