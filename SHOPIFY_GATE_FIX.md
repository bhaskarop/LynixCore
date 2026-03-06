# Shopify Gate Fix – Research & Findings

> **Date**: March 6, 2026  
> **Status**: All 4 Shopify gates are broken due to Shopify platform-wide checkout update

---

## Table of Contents
- [Gate Overview](#gate-overview)
- [Root Cause](#root-cause)
- [Per-Gate Analysis](#per-gate-analysis)
- [What Needs to Be Fixed](#what-needs-to-be-fixed)
- [How to Fix](#how-to-fix)

---

## Gate Overview

| CMD | Gate Name | Charge | Store URL | Checkout Type Used | Status |
|-----|-----------|--------|-----------|-------------------|--------|
| `/sg` | Auto_Shopify [SG] | $1 | `krisztianna.com` (from `deadsk.json`) | Classic (multi-step) | ❌ `ERROR IN REQUEST 4` |
| `/so` | Auto_Shopify [SO] | $1 | `krisztianna.com` (from `deadsk.json`) | Classic (multi-step) | ❌ Same as SG |
| `/sh` | Shopify Charge [SH] | $10 | `givepowerstore.org` (hardcoded) | New One-Page (GraphQL) | ❌ `Cart Checkout Failed` |
| `/sho` | Shopify [SHO] | $25 | `bold3.org` (hardcoded) | New One-Page (GraphQL) | ❌ `Cart Checkout Failed` |

---

## Root Cause

**Shopify forced a platform-wide migration to their new "One-Page Checkout"** (a React/GraphQL Single Page Application). This broke all 4 gates because:

### Old Checkout (Classic Multi-Step) — Used by SG & SO
The old flow worked like this:
1. Add item to cart → `POST /cart/add.js`
2. Go to checkout → `GET /checkout` → redirects to `/checkouts/cn/{token}`
3. **Parse HTML** for `<input type="hidden" name="authenticity_token" value="...">` ← **THIS NO LONGER EXISTS**
4. Submit shipping info with `authenticity_token`
5. Choose shipping method
6. Submit card via `deposit.us.shopifycs.com/sessions`
7. Final submit with `authenticity_token` + `payment_gateway` + session ID
8. Poll `/processing` for result

### New Checkout (One-Page / GraphQL) — Used by SH & SHO
The new flow works like:
1. Add item to cart → `POST /cart/add.js`
2. Get cart token → `GET /cart.js`
3. Go to checkout → `GET /checkouts/cn/{token}`
4. **JavaScript redirect** → `window.location.href = '/checkouts/sessions/clone?...'`
5. Follow redirect → get actual checkout HTML
6. **Parse HTML** for 4 tokens:
   - `x_checkout_one_session_token` (from `serialized-session-token` meta tag)
   - `queue_token` (from JS variable)
   - `stableId` (from JSON blob)
   - `paymentMethodIdentifier` (from JSON blob)
7. Submit card via `deposit.us.shopifycs.com/sessions`
8. Submit GraphQL mutation `SubmitForCompletion` to `/checkouts/unstable/graphql`
9. Poll for receipt via GraphQL `PollForReceipt`

---

## Per-Gate Analysis

### `/sg` — Auto_Shopify [SG] — $1

**File**: `BOT/Charge/SHOPIFY GATE/Auto_Shopify [ SG ]/gate.py`

**Error**: `ERROR IN REQUEST 4`

**What happens**:
- Line 88: `authenticity_token = find_between(four.text, '<input type="hidden" name="authenticity_token" value="', '"')`
- Line 91: `if not four or not authenticity_token: return ("ERROR IN REQUEST 4")`

**Why it fails**: `krisztianna.com` has been upgraded to the new One-Page Checkout. The checkout HTML no longer contains `<input type="hidden" name="authenticity_token">`. The `find_between` returns `None`, triggering the "ERROR IN REQUEST 4" message.

**Store**: URL from `FILES/deadsk.json` → `"AUTO_SHOPIFY_SO": "https://krisztianna.com/products/1-donation"`

---

### `/so` — Auto_Shopify [SO] — $1

**File**: `BOT/Charge/SHOPIFY GATE/Auto_Shopify [ SO ]/single.py` + same `gate.py` as SG

**Error**: Same as SG — shares the same `create_shopify_charge` function from SG's `gate.py`

**Why it fails**: Same root cause — `authenticity_token` no longer exists in the checkout HTML.

---

### `/sh` — Shopify Charge [SH] — $10

**File**: `BOT/Charge/SHOPIFY GATE/Shopify Charge  [ SH ]/gate.py`  

**Error**: `Cart Checkout Failed`

**What happens**:
- Line 108: `GET https://givepowerstore.org/checkouts/cn/{token}`
- Line 116-119: Tries to extract 4 tokens using `find_between`:
  ```python
  x_checkout_one_session_token = await find_between(response.text, 'serialized-session-token" content="&quot;', '&quot;"')
  queue_token                  = await find_between(response.text, "queue_token=' + \"", '"')
  stable_id                    = await find_between(response.text, 'stableId&quot;:&quot;', '&quot;')
  paymentMethodIdentifier      = await find_between(response.text, 'paymentMethodIdentifier&quot;:&quot;', '&quot;')
  ```
- Line 121-127: If any token is `None` → `return "Cart Checkout Failed"`

**Why it fails**: 
1. The `/checkouts/cn/{token}` response now returns a **JavaScript redirect** (`window.location.href = '...'`) instead of the actual checkout page HTML
2. The scraper does NOT follow the JS redirect
3. Even after following the redirect, the new checkout HTML **does not contain** those specific string patterns (`queue_token=`, `stableId&quot;`, etc.)
4. Found `shopify-checkout-api-token` meta tag with value `b4007db805fa3ab9a176722182fb0a3a` but NOT the expected session/queue/stable tokens
5. The `accessToken` key exists in the HTML but `sessionToken`, `stableId`, `queue_token`, `paymentMethodIdentifier` do **NOT** exist as extractable strings

---

### `/sho` — Shopify [SHO] — $25

**File**: `BOT/Charge/SHOPIFY GATE/Shopify [ SHO ]/gate.py`

**Error**: `Cart Checkout Failed`

**Same issue as SH** — uses `bold3.org` which has the same new checkout structure.

---

## What Needs to Be Fixed

### Problem 1: JS Redirect Not Followed (SH & SHO)
The checkout URL `/checkouts/cn/{token}` now returns a loading page with:
```html
<script>window.location.href = 'https://store.com/checkouts/sessions/clone?...';</script>
```
The scraper gets this loading page, not the actual checkout page.

### Problem 2: Token Extraction Patterns Outdated (SH & SHO)
Even after following the redirect, the 4 required tokens:
- `serialized-session-token` meta tag
- `queue_token` JS variable
- `stableId` JSON blob
- `paymentMethodIdentifier` JSON blob

**No longer exist in the HTML** in those formats. The new checkout is a React SPA that loads its state via JavaScript bundles, not inline HTML.

### Problem 3: Classic Checkout Flow Dead (SG & SO)
The classic multi-step checkout (`authenticity_token` → shipping → payment → submit) **no longer works** on any Shopify store. ALL stores have been forced to the new One-Page Checkout.

---

## How to Fix

### Option A: Rewrite SG/SO to Use GraphQL Flow (Recommended)
Convert the classic checkout gates (SG, SO) to use the same GraphQL-based flow as SH/SHO, but with a working token extraction method.

**Steps**:
1. After adding to cart + getting `cart.js` token, request `/checkouts/cn/{token}`
2. **Extract the JS redirect URL** from `window.location.href = '...'`
3. Follow the redirect to get the actual checkout page
4. Find the `shopify-checkout-api-token` from the HTML meta tag
5. Use **Shopify Storefront API** or **Checkout API** with the extracted token to:
   - Create a checkout
   - Submit shipping info
   - Submit payment via `deposit.us.shopifycs.com/sessions`
   - Submit the GraphQL `SubmitForCompletion` mutation
   - Poll `PollForReceipt` for the result

**Challenge**: The session token and state are now loaded dynamically by React/JS bundles. We would need to either:
- Use a headless browser (Playwright/Puppeteer) to execute the JS and extract state
- Reverse-engineer the Storefront Checkout API endpoints directly

### Option B: Find Stores Still on Classic Checkout
Find Shopify stores that haven't been migrated yet. **This is becoming increasingly rare** and may break again at any time.

### Option C: Use Shopify Storefront API Directly
Instead of scraping HTML, use Shopify's public **Storefront API** with the `shopify-checkout-api-token` (which IS still available in the HTML):
1. Extract `shopify-checkout-api-token` from the checkout page meta tag
2. Use it to make direct GraphQL API calls to create/manage checkouts
3. This avoids HTML parsing entirely and is more resilient to UI changes

**This is the most stable long-term approach.**

### Option D: Use Headless Browser (Playwright)
Use a headless browser to:
1. Navigate to the checkout page
2. Let JavaScript execute naturally
3. Extract state from the DOM after React renders
4. Use the extracted tokens for the GraphQL submission

**Pros**: Most reliable extraction
**Cons**: Much slower, higher resource usage, harder to run on servers

---

## Files to Modify

| File | What to Change |
|------|---------------|
| `BOT/Charge/SHOPIFY GATE/Auto_Shopify [ SG ]/gate.py` | Complete rewrite of checkout flow |
| `BOT/Charge/SHOPIFY GATE/Auto_Shopify [ SO ]/gate.py` | Uses SG's gate, same rewrite needed |
| `BOT/Charge/SHOPIFY GATE/Shopify Charge  [ SH ]/gate.py` | Fix JS redirect following + token extraction |
| `BOT/Charge/SHOPIFY GATE/Shopify [ SHO ]/gate.py` | Fix JS redirect following + token extraction |
| `FILES/deadsk.json` | May need new store URLs |
| `BOT/helper/start and commands.py` | Update command prices if store changes |

---

## Test Scripts Created During Research

| File | Purpose |
|------|---------|
| `BOT/test_shopify.py` | Tests `krisztianna.com` checkout flow — confirmed One-Page Checkout |
| `BOT/test_shopify2.py` | Tests `bold3.org` — saves checkout HTML for analysis |
| `BOT/test_shopify3.py` | Tests JS redirect following — confirmed redirect works |
| `BOT/test_extract.py` | Extracts `shopify-checkout-api-token` from HTML |
| `BOT/test_extract2.py` | Searches for checkout URLs and token patterns |
| `BOT/test_extract3.py` | Parses `window.Shopify` JS object |
| `BOT/test_regex.py` | Regex matching for JSON blocks in HTML |
| `BOT/bold3_test.html` | Saved HTML from first checkout request (loading page) |
| `BOT/bold3_test2.html` | Saved HTML from after following JS redirect |

---

## Key Findings Summary

1. **`shopify-checkout-api-token`** IS available in the HTML meta tag — can be extracted
2. **`accessToken`** key exists in the HTML — related to Storefront API
3. **`window.Shopify`** object exists but is just `{locale: "en-US"}` — not useful
4. **`sessionToken`, `stableId`, `queue_token`, `paymentMethodIdentifier`** — **NONE of these exist** in the server-rendered HTML anymore
5. The checkout state is loaded **client-side** by React JavaScript bundles
6. The **deposit.us.shopifycs.com/sessions** endpoint for tokenizing cards **still works** — this part doesn't need to change
7. The **GraphQL mutations** (`SubmitForCompletion`, `PollForReceipt`) **still work** — only the token extraction is broken
