from crawler.crawler_instance.local_shared_model.rule_model import FetchProxy, RuleModel
from typing import Dict
import requests
from playwright.sync_api import sync_playwright
from playwright.async_api import Browser, BrowserContext


def get_html_via_tor(url: str, rule: RuleModel) -> str:
  try:
    with sync_playwright() as p:
      if rule.m_fetch_proxy is FetchProxy.NONE:
        browser = p.chromium.launch(headless=True)
      else:
        browser = p.chromium.launch(proxy={"server": "socks5://127.0.0.1:9150"}, headless=True)

      context = browser.new_context()
      page = context.new_page()
      page.goto(url, wait_until="networkidle")
      page_source = page.content()
      browser.close()
      return page_source

  except requests.ConnectionError:
    print("Error: TOR is not running. Please start TOR and try again.")
    exit(1)

  except requests.RequestException as e:
    print(f"Error fetching the URL: {e}")
    return ""

  except Exception as e:
    print(f"Unexpected error occurred: {e}")
    return ""

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
    browser = await playwright.chromium.launch(headless=True, proxy={"server": tor_proxy})
  else:
    browser = await playwright.chromium.launch(headless=True)

  context = await browser.new_context()
  return context, browser