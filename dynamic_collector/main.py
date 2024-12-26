from playwright.async_api import async_playwright
from typing import Dict, Optional
import requests
import asyncio


def get_proxy(use_proxy=True) -> Dict[str, str]:
    if use_proxy:
        proxies = {"server": "socks5://127.0.0.1:9150"}
        try:
            response = requests.get("http://check.torproject.org", proxies={"http": "socks5h://127.0.0.1:9150"}, timeout=10)
            response.raise_for_status()
            print("Tor proxy is working correctly.")
            return proxies
        except Exception as ex:
            print("Failed to initialize proxy:", ex)
    return {}


async def _initialize_webdriver(use_proxy: bool = True) -> Optional[object]:
    if use_proxy:
        tor_proxy = "socks5://127.0.0.1:9150"
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False, proxy={"server": tor_proxy} if tor_proxy else None)
    else:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)

    context = await browser.new_context()
    return context


async def main():
    url = "http://breachdbsztfykg2fdaq2gnqnxfsbj5d35byz3yzj73hazydk4vq72qd.onion/"
    email = "msmannan00@gmail.com"
    username = "msmannan00"
    query = {"url": url, "email": email, "username": username}

    try:
        browser_context = await _initialize_webdriver(use_proxy=True)
        from dynamic_collector.sample import sample
        sample_instance = sample()
        result = await sample_instance.parse_leak_data(query=query, context=browser_context)
        print(result)
    except Exception as e:
        print("Error occurred:", e)
    finally:
        pass


if __name__ == "__main__":
    asyncio.run(main())