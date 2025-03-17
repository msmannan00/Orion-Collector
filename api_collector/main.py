import asyncio
from playwright.async_api import async_playwright

from api_collector._example import _example
from crawler.request_manager import _initialize_webdriver
from api_collector.scripts._breachdbsztfykg2fdaq2gnqnxfsbj5d35byz3yzj73hazydk4vq72qd import _breachdbsztfykg2fdaq2gnqnxfsbj5d35byz3yzj73hazydk4vq72qd

email = "msmannan00@gmail.com"
username = "msmannan00"
query = {"email": email, "username": username}

async def main():
    try:
        async with async_playwright() as playwright:
            context, browser = await _initialize_webdriver(playwright, use_proxy=True)
            handler_instance = _example()
            result = await handler_instance.parse_leak_data(query=query, context=context)
            print(result)
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    asyncio.run(main())
