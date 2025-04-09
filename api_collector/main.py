import asyncio
from playwright.async_api import async_playwright

from api_collector._example import _example
from crawler.request_manager import initialize_webdriver

email = "msmannan00@gmail.com"
username = "msmannan00"
query = {"email": email, "username": username}

async def main():
    try:
        async with async_playwright() as playwright:
            context, browser = await initialize_webdriver(playwright, use_proxy=True)
            handler_instance = _example()
            await handler_instance.parse_leak_data(query=query, context=context)
            print(handler_instance.card_data)
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    asyncio.run(main())
