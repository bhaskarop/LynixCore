import re
text = open('bold3_test2.html', 'r', encoding='utf-8').read()

print('sessionToken?', 'sessionToken' in text)
print('checkout_one_session_token?', 'checkout_one_session_token' in text)
print('queue_token?', 'queue_token' in text)
print('stableId?', 'stableId' in text)
print('session_id?', 'session_id' in text)
print('checkout_id?', 'checkout_id' in text)

m = re.findall(r'"token":"([a-zA-Z0-9_-]+)"', text)
if m: print('Tokens found:', set(m))

m2 = re.findall(r'"sessionToken":"(.*?)"', text)
if m2: print('sessionTokens:', set(m2))

m3 = re.findall(r'"checkout\[([^\]]+)\]"', text)
if m3: print('checkout array fields:', set(m3))

m4 = re.findall(r'name="([^"]+)"', text)
if m4: print('Input names:', [n for n in set(m4) if 'checkout' in n or 'token' in n.lower()])

print("Any token keys:", set(re.findall(r'"([a-zA-Z0-9_\-]+[tT]oken)":', text)))
