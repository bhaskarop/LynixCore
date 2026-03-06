import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def main():
    async with aiohttp.ClientSession() as session:
        # 1. Add to cart
        data = {'id': '39384609259606', 'quantity': 1}
        print("Adding to cart...")
        async with session.post('https://krisztianna.com/cart/add.js', data=data) as resp:
            print("Cart Add status:", resp.status)
            print(await resp.text())
        
        # 2. Go to checkout URL
        print("\nRequesting checkout...")
        async with session.get('https://krisztianna.com/checkout') as resp:
            text = await resp.text()
            print("Checkout URL:", resp.url)
            print("Status:", resp.status)
            
            if 'authenticity_token' in text:
                print("Found authenticity_token (Classic Checkout)")
            else:
                print("NO authenticity_token (Possible One-Page Checkout)")
                if 'serialized-session-token' in text or 'queue_token' in text:
                    print("Found One-Page fields instead")
                
                with open('D:/Coding-Folder/Codes-CL/LynixCore-Telegram/FILES/kris_test.html', 'w', encoding='utf-8') as f:
                    f.write(text)
                    print("Saved HTML to kris_test.html")

asyncio.run(main())
