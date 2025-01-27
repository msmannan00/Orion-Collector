import asyncio
from playwright.async_api import async_playwright
from crawler.request_manager import _initialize_webdriver
from dynamic_collector._dynamic_sample import _dynamic_sample

url = "http://breachdbsztfykg2fdaq2gnqnxfsbj5d35byz3yzj73hazydk4vq72qd.onion/"
email = "syedumairshah81@gmail.com"
username = "syedumairshah81"
query = {"url": url, "email": email, "username": username}

async def main():
    try:
        async with async_playwright() as playwright:
            context, browser = await _initialize_webdriver(playwright, use_proxy=True)
            handler_instance = _dynamic_sample()
            result = await handler_instance.parse_leak_data(query=query, context=context)
            print(result)
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    asyncio.run(main())
