import asyncio
import aiohttp
import json
import re

def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return None

async def main():
    async with aiohttp.ClientSession() as session:
        data = {'form_type': 'product', 'id': '12240744611932', 'quantity': 1}
        print("Adding bold3.org to cart...")
        async with session.post('https://bold3.org/cart/add.js', data=data) as resp:
            pass
        
        async with session.get('https://bold3.org/cart.js') as r:
            j = json.loads(await r.text())
            token = j.get('token')
        
        print("\nRequesting checkout...")
        async with session.get(f'https://bold3.org/checkouts/cn/{token}') as resp:
            text = await resp.text()
            # look for redirect
            redirect = find_between(text, "window.location.href = '", "'")
            
        if redirect:
            print("Found JS redirect:", redirect)
            async with session.get(redirect) as resp2:
                text2 = await resp2.text()
                print("Followed redirect. Status:", resp2.status)
                
                with open('bold3_test2.html', 'w', encoding='utf-8') as f:
                    f.write(text2)
                
                x_checkout = find_between(text2, 'serialized-session-token" content="&quot;', '&quot;"')
                queue_token = find_between(text2, '''queue_token=' + "''', '"')
                stable_id = find_between(text2, 'stableId&quot;:&quot;', '&quot;')
                payment = find_between(text2, 'paymentMethodIdentifier&quot;:&quot;', '&quot;')
                
                print(f"x_checkout: {x_checkout}")
                print(f"queue_token: {queue_token}")
                print(f"stable_id:    {stable_id}")
                print(f"payment:      {payment}")

asyncio.run(main())
