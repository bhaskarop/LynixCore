import json
import re

with open('bold3_test2.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Try finding API token
token = re.search(r'shopify-checkout-api-token"\s*content="([^"]+)"', text)
if token:
    print("API Token:", token.group(1))

# Try finding the checkout state JSON
state_match = re.search(r'window\.Shopify\s*=\s*(.*?);', text, re.DOTALL)
if state_match:
    state_str = state_match.group(1)
    print("Found window.Shopify, length:", len(state_str))
    
settings_match = re.search(r'{"Storefront":{.*?}', text)
if settings_match:
    print("Found Storefront settings")
