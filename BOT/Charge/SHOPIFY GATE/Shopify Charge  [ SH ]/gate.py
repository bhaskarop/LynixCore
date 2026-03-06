"""
Shopify Charge [SH] - $10 gate (givepowerstore.org).
Crafted With <3 By Bhaskar
"""
from FUNC.shopify_utils import create_shopify_charge as _shopify_charge


async def create_shopify_charge(fullz, session):
    return await _shopify_charge(
        fullz, session,
        product_url='https://givepowerstore.org/products/10-donation',
        variant_id='41408502792330',
        amount='10.00',
        currency='USD',
    )
