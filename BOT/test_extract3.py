import re

with open('bold3_test2.html', 'r', encoding='utf-8') as f:
    text = f.read()

# See what's inside window.Shopify
state_match = re.search(r'window\.Shopify\s*=\s*(\{.*?\});\n', text, re.DOTALL)
if state_match:
    state_str = state_match.group(1)
    
    # search for our keys inside this string
    print("Does it have stableId?", "stableId" in state_str)
    print("Does it have checkoutId?", "checkoutId" in state_str)
    print("Does it have queueToken?", "queueToken" in state_str or "queue_token" in state_str)
    print("Does it have session token?", "sessionToken" in state_str)
    print("Does it have paymentMethodIdentifier?", "paymentMethodIdentifier" in state_str)
    
    # print all ids just in case
    ids = re.findall(r'"([a-zA-Z0-9]+Id)":"([^"]+)"', state_str)
    print("IDs:", set(ids))
    
    tokens = re.findall(r'"([a-zA-Z0-9]*[tT]oken)":"([^"]+)"', state_str)
    print("Tokens:", set(tokens))
