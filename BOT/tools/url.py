import httpx
import re
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from TOOLS.check_all_func import *

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Gateway Signatures Database
# Each entry: ("Display Name", "Emoji", [list of detection patterns])
# Patterns are matched case-insensitively against page HTML source
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GATEWAY_SIGNATURES = [
    # ─── Card Processors ───
    ("Stripe", "💳", [
        "js.stripe.com", "stripe.com/v3", "stripe-js",
        "Stripe.publishableKey", "stripe_publishable_key",
        "pk_live_", "pk_test_", "stripe-button",
        "checkout.stripe.com", "stripeTokenHandler",
        "stripe-payment", "data-stripe",
    ]),
    ("Braintree", "💳", [
        "js.braintreegateway.com", "braintree-web",
        "braintree.setup", "braintree-hosted-fields",
        "client.braintreegateway.com", "braintree-paypal",
        "braintree-dropin", "BraintreeData",
        "braintree_merchant_id", "braintree-badge",
    ]),
    ("Square", "💳", [
        "squareup.com", "square.com/payments",
        "sq-payment-form", "square-payment",
        "squarecdn.com", "web.squarecdn.com/v1/square.js",
        "SqPaymentForm", "square-marketplace",
    ]),
    ("Adyen", "💳", [
        "checkoutshopper-live.adyen.com", "adyen.com",
        "adyen-encrypted-data", "adyen.encrypt",
        "adyen-checkout", "checkoutshopper-test.adyen.com",
        "adyenjs", "adyen-dropin",
    ]),
    ("Authorize.net", "💳", [
        "accept.authorize.net", "authorize.net",
        "AcceptUI", "authorizenet", "anetseal",
        "js.authorize.net", "Accept.dispatchData",
        "authorize-net-badge",
    ]),
    ("Cybersource", "💳", [
        "cybersource.com", "flex.cybersource.com",
        "secureacceptance.cybersource.com", "cybersource-flex",
        "CyberSource", "cybersource-token",
    ]),
    ("Worldpay", "💳", [
        "worldpay.com", "secure.worldpay.com",
        "worldpay-cse", "worldpay-hosted",
        "Worldpay.useTemplateForm", "worldpaytotal",
        "online.worldpay.com",
    ]),
    ("NMI", "💳", [
        "secure.networkmerchants.com",
        "secure.nmi.com", "CollectJS",
        "gateway.merchantsecure.com",
        "collectjs", "nmi-payment",
    ]),
    ("Payeezy", "💳", [
        "payeezy.com", "api.payeezy.com",
        "payeezy-js", "Payeezy.init",
    ]),
    ("BlueSnap", "💳", [
        "bluesnap.com", "sandbox.bluesnap.com",
        "web-sdk.bluesnap.com", "bluesnapCheckout",
        "bsToken", "bluesnap-hosted",
    ]),
    ("Checkout.com", "💳", [
        "checkout.com", "js.checkout.com",
        "cko-payment", "Frames.init",
        "checkout-frames", "checkout-sdk",
    ]),
    ("Mollie", "💳", [
        "mollie.com", "js.mollie.com",
        "mollie-components", "Mollie(",
        "mollie-payment",
    ]),
    ("Payflow", "💳", [
        "payflowlink.paypal.com", "payflow",
        "payflowpro", "payflow-transparent",
    ]),
    ("USAePay", "💳", [
        "usaepay.com", "sandbox.usaepay.com",
        "usaepay-payment",
    ]),
    ("Eway", "💳", [
        "eway.com.au", "eWAY",
        "eway-payment", "ewaypayment",
        "secure.ewaypayments.com",
    ]),
    ("Moneris", "💳", [
        "moneris.com", "esqa.moneris.com",
        "moneris-checkout", "monerisCheckout",
    ]),
    ("Opayo (SagePay)", "💳", [
        "opayo.co.uk", "sagepay.com",
        "pi-live.sagepay.com", "sagepay-dropin",
        "opayo-dropin",
    ]),
    ("Paysafe", "💳", [
        "paysafe.com", "hosted.paysafe.com",
        "paysafe-checkout", "paysafecard",
    ]),
    ("CardConnect", "💳", [
        "cardconnect.com", "cardpointe",
        "fts.cardconnect.com",
    ]),
    ("Heartland", "💳", [
        "heartlandpaymentsystems.com", "hps.heartlandpaymentsystems.com",
        "globalpayments.com", "heartland-payment",
    ]),
    ("2Checkout (Verifone)", "💳", [
        "2checkout.com", "2co.com",
        "avangate.com", "2checkout-inline",
    ]),
    ("Recurly", "💳", [
        "recurly.com", "js.recurly.com",
        "recurly-element", "Recurly.configure",
    ]),
    ("ChargeOver", "💳", [
        "chargeover.com", "ChargeOver",
    ]),
    ("PayTrace", "💳", [
        "paytrace.com", "PayTrace",
    ]),
    ("Windcave (PaymentExpress)", "💳", [
        "windcave.com", "paymentexpress.com",
        "sec.windcave.com",
    ]),
    ("FastSpring", "💳", [
        "fastspring.com", "fsc.js",
        "fastspring-builder",
    ]),
    ("Paddle", "💳", [
        "paddle.com", "cdn.paddle.com",
        "Paddle.Setup", "paddle-js",
    ]),

    # ─── Digital Wallets & BNPL ───
    ("PayPal", "🅿️", [
        "paypal.com/sdk", "paypal.com/v1",
        "paypalobjects.com", "paypal-button",
        "paypal-checkout", "paypal-express",
        "paypal-smart-button", "paypal-js",
        "paypal.Buttons", "data-paypal",
    ]),
    ("Apple Pay", "🍎", [
        "apple-pay", "ApplePaySession",
        "apple-pay-button", "applepay",
        "canMakePaymentsWithActiveCard",
    ]),
    ("Google Pay", "🔵", [
        "google-pay", "googlepay",
        "pay.google.com", "gpay-button",
        "GooglePayButton", "google.payments.api",
        "buyflow/gPay",
    ]),
    ("Amazon Pay", "📦", [
        "amazonpay", "amazon-pay",
        "static-na.payments-amazon.com",
        "pay.amazon.com", "OffAmazonPayments",
    ]),
    ("Shop Pay", "🛍️", [
        "shop-pay", "shopPay",
        "shop-pay-button", "shopify-payment-button",
    ]),
    ("Venmo", "💙", [
        "venmo.com", "venmo-button",
        "venmo-payment",
    ]),
    ("Klarna", "🩷", [
        "klarna.com", "klarnacheckout",
        "klarna-payments", "Klarna.Payments",
        "x-klarnacdn.net", "klarna-badge",
        "klarna-placement",
    ]),
    ("Afterpay", "💚", [
        "afterpay.com", "afterpay-badge",
        "afterpay.js", "afterpay-payment",
        "js.afterpay.com", "afterpay-button",
    ]),
    ("Affirm", "💜", [
        "affirm.com", "cdn1.affirm.com",
        "affirm-js", "affirm-badge",
        "affirm-as-low-as",
    ]),
    ("Sezzle", "🟢", [
        "sezzle.com", "widget.sezzle.com",
        "sezzle-payment", "sezzle-widget",
        "sezzle-smart-widget",
    ]),
    ("Zip (QuadPay)", "🟣", [
        "zip.co", "quadpay.com",
        "zip-payment", "quadpay-widget",
        "widget.quadpay.com",
    ]),
    ("Clearpay", "🩵", [
        "clearpay.com", "clearpay.co.uk",
        "clearpay-badge",
    ]),
    ("Laybuy", "🔶", [
        "laybuy.com", "laybuy-badge",
        "laybuy-payment",
    ]),
    ("Splitit", "🔷", [
        "splitit.com", "splitit-payment",
        "Splitit.FlexFields",
    ]),
    ("Atome", "💛", [
        "atome.sg", "atome-payment",
    ]),
    ("Tabby", "🧡", [
        "tabby.ai", "checkout.tabby.ai",
        "tabby-checkout", "TabbyPromo",
    ]),
    ("Tamara", "🩶", [
        "tamara.co", "cdn.tamara.co",
        "tamara-widget", "tamara-product-widget",
    ]),

    # ─── E-commerce Platforms ───
    ("Shopify Payments", "🛒", [
        "checkout.shopify.com", "cdn.shopify.com",
        "shopify-payment", "Shopify.Checkout",
        "myshopify.com",
    ]),
    ("WooCommerce", "🟠", [
        "woocommerce", "wc-checkout",
        "wc-ajax", "woocommerce-checkout",
        "wp-content/plugins/woocommerce",
    ]),
    ("Magento", "🔴", [
        "magento", "Magento_Checkout",
        "mage/cookies", "checkout/onepage",
        "magento2", "Magento_Payment",
    ]),
    ("BigCommerce", "🟤", [
        "bigcommerce.com", "bigcommerce",
        "stencil-utils",
    ]),
    ("PrestaShop", "🩵", [
        "prestashop", "PrestaShop",
        "modules/ps_checkout",
    ]),
    ("OpenCart", "🔵", [
        "opencart", "route=checkout",
        "catalog/view",
    ]),
    ("Squarespace Commerce", "⬛", [
        "squarespace.com", "squarespace-checkout",
        "static1.squarespace.com",
    ]),
    ("Wix Payments", "🟡", [
        "wix.com", "wixpay",
        "static.parastorage.com",
    ]),
    ("Ecwid", "🟩", [
        "ecwid.com", "app.ecwid.com",
        "ecwid-shopping",
    ]),

    # ─── Regional / Alternative ───
    ("Razorpay", "💙", [
        "razorpay.com", "checkout.razorpay.com",
        "razorpay-payment", "Razorpay(",
    ]),
    ("Paytm", "🔵", [
        "paytm.com", "securegw.paytm.in",
        "merchantpgpui.paytm.com",
    ]),
    ("PayU", "🟢", [
        "payu.com", "payu.in",
        "secure.payu.com",
    ]),
    ("Mercado Pago", "💙", [
        "mercadopago.com", "sdk.mercadopago.com",
        "MercadoPago", "mp-checkout",
    ]),
    ("iDEAL", "🟣", [
        "ideal-payment", "ideal.nl",
        "idealcheckout",
    ]),
    ("Bancontact", "🔵", [
        "bancontact", "payconiq",
    ]),
    ("Sofort", "🩷", [
        "sofort.com", "sofort-payment",
        "klarna-sofort",
    ]),
    ("Giropay", "🔵", [
        "giropay.de", "giropay-payment",
    ]),
    ("Przelewy24", "🔴", [
        "przelewy24.pl", "p24-payment",
    ]),
    ("Boleto", "📄", [
        "boleto", "boleto-bancario",
    ]),
    ("PIX", "💚", [
        "pix-payment", "pix.bcb.gov.br",
        "pix-qrcode",
    ]),
    ("Alipay", "🔵", [
        "alipay.com", "intl.alipay.com",
        "alipay-payment",
    ]),
    ("WeChat Pay", "🟢", [
        "wechat-pay", "wechatpay",
        "pay.weixin.qq.com",
    ]),

    # ─── Crypto ───
    ("Coinbase Commerce", "🪙", [
        "commerce.coinbase.com", "coinbase-commerce",
        "CoinbaseCommerce",
    ]),
    ("BitPay", "🟠", [
        "bitpay.com", "bitpay-invoice",
        "bitpay-widget",
    ]),
    ("CoinGate", "🔶", [
        "coingate.com", "coingate-payment",
    ]),
    ("NOWPayments", "🟡", [
        "nowpayments.io", "nowpayments-widget",
    ]),

    # ─── 3D Secure ───
    ("Cardinal Commerce (3DS)", "🔒", [
        "cardinalcommerce.com", "songbird.js",
        "songbirdstag.cardinalcommerce.com",
        "Cardinal.setup",
    ]),
    ("Verifi (3DS)", "🛡️", [
        "verifi.com", "verifi-3ds",
    ]),
]


def detect_gateways(html_source):
    """Scan HTML source for gateway signatures. Returns list of (name, emoji)."""
    found = []
    html_lower = html_source.lower()
    for name, emoji, patterns in GATEWAY_SIGNATURES:
        for pattern in patterns:
            if pattern.lower() in html_lower:
                found.append((name, emoji))
                break  # One match is enough per gateway
    return found


@Client.on_message(filters.command("url", [".", "/"]))
async def cmd_url(Client, message):
    try:
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return

        role = checkall[1]

        # ── Parse URL ──
        try:
            if message.reply_to_message:
                url = str(message.reply_to_message.text).strip()
            else:
                url = str(message.text.split(" ", 1)[1]).strip()
        except (IndexError, AttributeError):
            resp = """\
<b>Invalid Usage ⚠️
━━━━━━━━━━━━━━
Usage: <code>/url https://example.com</code>

Please provide a valid website URL.</b>"""
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        # Auto-prepend https:// if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # ── Loading message ──
        loading = await message.reply_text(
            "<b>🔍 Scanning website for gateways...\nPlease wait ⏳</b>",
            reply_to_message_id=message.id
        )

        # ── Fetch page ──
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
            }
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=20,
                verify=False
            ) as session:
                response = await session.get(url, headers=headers)
                html_source = response.text

        except httpx.TimeoutException:
            await Client.edit_message_text(
                message.chat.id, loading.id,
                "<b>Timeout Error ⚠️\n\nThe website took too long to respond. Try again later.</b>"
            )
            return
        except httpx.ConnectError:
            await Client.edit_message_text(
                message.chat.id, loading.id,
                "<b>Connection Error ⚠️\n\nCould not connect to the website. Check the URL and try again.</b>"
            )
            return
        except Exception as e:
            await Client.edit_message_text(
                message.chat.id, loading.id,
                f"<b>Error Fetching URL ⚠️\n\nMessage: {str(e)[:200]}</b>"
            )
            return

        # ── Detect gateways ──
        gateways = detect_gateways(html_source)

        if gateways:
            gateway_list = "\n".join(
                f"   {i}. {emoji} <code>{name}</code>"
                for i, (name, emoji) in enumerate(gateways, 1)
            )
            resp = f"""\
<b>Gateway Hunter Results ✅</b>
━━━━━━━━━━━━━━
🌐 <b>URL:</b> <code>{url}</code>
🔍 <b>Gateways Found:</b> <code>{len(gateways)}</code>

{gateway_list}
━━━━━━━━━━━━━━
<b>Checked By:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> [ {role} ]
<b>Owned by:</b> <a href="tg://user?id=8239967579">KaiZen﹒ ⁺</a> [ @bhaskargg ]
"""
        else:
            resp = f"""\
<b>Gateway Hunter Results ❌</b>
━━━━━━━━━━━━━━
🌐 <b>URL:</b> <code>{url}</code>
🔍 <b>Gateways Found:</b> <code>0</code>

<i>No payment gateways detected on this page.
Try the checkout or payment page directly.</i>
━━━━━━━━━━━━━━
<b>Checked By:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> [ {role} ]
<b>Owned by:</b> <a href="tg://user?id=8239967579">KaiZen﹒ ⁺</a> [ @bhaskargg ]
"""
        await Client.edit_message_text(message.chat.id, loading.id, resp)

    except Exception:
        await log_cmd_error(message)
