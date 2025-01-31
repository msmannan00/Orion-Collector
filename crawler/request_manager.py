import sys
from os import PathLike
from threading import Timer

import redis
import requests
from typing import Dict
from bs4 import BeautifulSoup
from playwright.async_api import Browser, BrowserContext
from playwright.sync_api import sync_playwright
from selenium.common import TimeoutException
from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.rule_model import FetchProxy


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

def parse_leak_data(proxy: dict, model:leak_extractor_interface) -> tuple:
  default_data_model = leak_data_model(
    cards_data=[],
    contact_link=model.contact_page(),
    base_url=model.base_url,
    content_type=["leak"]
  )

  raw_parse_mapping = {}
  timeout_flag = {"value": False}
  browser = None

  def terminate_browser():
    nonlocal browser
    timeout_flag["value"] = True
    if browser:
      try:
        print("Timeout reached. Closing browser and terminating tasks.")
      except Exception:
        pass

  try:
    with sync_playwright() as p:
      if model.rule_config.m_fetch_proxy is FetchProxy.NONE:
        browser = p.chromium.launch(headless=False)
      else:
        browser = p.chromium.launch(proxy=proxy, headless=False)

      context = browser.new_context()
      context.set_default_timeout(60000)
      context.set_default_navigation_timeout(60000)
      timeout_timer = Timer(model.rule_config.m_timeout, terminate_browser)
      timeout_timer.start()

      try:
        page = context.new_page()

        def capture_response(response):
          if response.request.resource_type == "document" and response.ok:
            try:
              cc = response.text()
              raw_parse_mapping[response.url] = response.text()
              print("parsed : " + response.url)
            except Exception as ex:
              pass

        page.on("response", capture_response)
        page.goto(model.seed_url, wait_until="networkidle")

        if timeout_flag["value"]:
          raise TimeoutException("Timeout occurred during navigation.")

        model.soup = BeautifulSoup(page.content(), 'html.parser')
        raw_parse_mapping[page.url] = page.content()
        model.parse_leak_data(page)
      except Exception as e:
        pass
      finally:
        timeout_timer.cancel()

  except Exception as e:
    print(f"Unexpected Error: {e}")

  default_data_model.cards_data = model.card_data
  return default_data_model, raw_parse_mapping


async def get_proxy(use_proxy=True) -> Dict[str, str]:
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

async def _initialize_webdriver(playwright, use_proxy: bool = True) -> (BrowserContext, Browser):
  if use_proxy:
    tor_proxy = "socks5://127.0.0.1:9150"
    browser = await playwright.chromium.launch(headless=False, proxy={"server": tor_proxy})
  else:
    browser = await playwright.chromium.launch(headless=True)

  context = await browser.new_context()
  return context, browser