"""
Auto_Shopify [SG] - $1 Shopify gate (dynamic store URL from deadsk.json).
Crafted With <3 By Bhaskar
"""
import json
from FUNC.shopify_utils import create_shopify_charge as _shopify_charge


async def create_shopify_charge(fullz, session):
    deadsk = json.loads(
        open("FILES/deadsk.json", "r", encoding="utf-8").read()
    )["AUTO_SHOPIFY_SO"]

    return await _shopify_charge(
        fullz, session,
        product_url=deadsk,
        amount='1.00',
        currency='USD',
    )
