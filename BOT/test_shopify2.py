import asyncio
import aiohttp
import json

async def main():
    async with aiohttp.ClientSession() as session:
        data = {'form_type': 'product', 'id': '12240744611932', 'quantity': 1}
        async with session.post('https://bold3.org/cart/add.js', data=data) as resp:
            pass
        
        async with session.get('https://bold3.org/cart.js') as r:
            j = json.loads(await r.text())
            token = j.get('token')
        
        async with session.get(f'https://bold3.org/checkouts/cn/{token}') as resp:
            text = await resp.text()
            with open('bold3_test.html', 'w', encoding='utf-8') as f:
                f.write(text)
            print("Wrote to bold3_test.html successfully")

asyncio.run(main())
