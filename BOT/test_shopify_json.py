import json
import re

text = open('bold3_test2.html', 'r', encoding='utf-8').read()
m = re.findall(r'window\.Shopify\s*=.*?({.*});', text, re.DOTALL)
if m:
    try:
        data = json.loads(m[0])
        print("Keys in window.Shopify:")
        for k in data.keys():
            print(" -", k)
            
        if 'Checkout' in data:
            print("\nKeys in window.Shopify.Checkout:")
            for k in data['Checkout'].keys():
                print(" -", k)
                
            print("\ntoken:", data['Checkout'].get('token'))
            print("paymentDue:", data['Checkout'].get('paymentDue'))
    except Exception as e:
        print("Failed to parse json:", e)
