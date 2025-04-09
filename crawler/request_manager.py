import sys
import redis
import requests
from playwright.async_api import Browser, BrowserContext


def check_services_status():
  try:
    tor_proxy = "socks5h://127.0.0.1:9150"
    response = requests.get("http://check.torproject.org", proxies={"http": tor_proxy}, timeout=100)
    response.raise_for_status()
    if response.status_code != 200:
      print("Tor is running but not working as expected.")
      sys.exit(1)
  except Exception as ex:
    print(f"Error: Tor is not running or accessible. Details: {ex}")
    sys.exit(1)

  try:
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    if not redis_client.ping():
      print("Redis server is running but not responding.")
      sys.exit(1)
  except Exception as ex:
    print(f"Error: Redis server is not running or accessible. Details: {ex}")
    sys.exit(1)


async def initialize_webdriver(playwright, use_proxy: bool = True) -> (BrowserContext, Browser):
  if use_proxy:
    tor_proxy = "socks5://127.0.0.1:9150"
    browser = await playwright.chromium.launch(headless=False, proxy={"server": tor_proxy})
  else:
    browser = await playwright.chromium.launch(headless=True)

  context = await browser.new_context()
  return context, browser