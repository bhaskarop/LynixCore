"""
Shopify [SHO] - $25 gate (bold3.org).
Crafted With <3 By Bhaskar
"""
from FUNC.shopify_utils import create_shopify_charge as _shopify_charge


async def create_shopify_charge(fullz, session):
    return await _shopify_charge(
        fullz, session,
        product_url='https://bold3.org/products/25-donation',
        variant_id='12240744611932',
        amount='25.00',
        currency='USD',
    )
