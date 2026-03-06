import re

with open('bold3_test2.html', 'r', encoding='utf-8') as f:
    text = f.read()

# find any URL containing /checkouts/
urls = set(re.findall(r'https://[^"\']*?/checkouts/[^"\']*', text))
print("Checkout URLs found:")
for u in urls:
    print(" -", u)

# checkout session ID
m = re.search(r'"checkoutId":"([^"]+)"', text)
if m: print("checkoutId:", m.group(1))

# token
m = re.search(r'"token":"([^"]+)"', text)
if m: print("token:", m.group(1))
