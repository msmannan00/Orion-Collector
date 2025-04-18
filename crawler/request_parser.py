import os
from threading import Timer
from playwright.sync_api import sync_playwright, Route
from bs4 import BeautifulSoup
import traceback

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_interface_model.leak.model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.rule_model import FetchProxy


class RequestParser:

  def __init__(self, proxy: dict, model: leak_extractor_interface):
    self.proxy = proxy
    self.model = model
    self.model.init_callback(self.callback)
    self.browser = None
    self.timeout_flag = False
    self.timeout_timer = None

  def callback(self):
    print("currently parsing index : " + str(len(self.model.card_data)))

  @staticmethod
  def _should_block_resource(route: Route) -> bool:
    request_url = route.request.url.lower()
    return (
        any(request_url.startswith(scheme) for scheme in ["data:image", "data:video", "data:audio"]) or
        route.request.resource_type in ["image", "media", "font", "stylesheet"]
    )

  def _handle_route(self, route: Route):
    if self._should_block_resource(route):
      route.abort()
    else:
      route.continue_()

  def _terminate_browser(self):
    self.timeout_flag = True
    if self.browser:
      try:
        print("Timeout reached. Closing browser and terminating tasks.")
        self.browser.close()
      except Exception:
        pass

  def parse(self):
    default_data_model = leak_data_model(
      cards_data=[],
      contact_link=self.model.contact_page(),
      base_url=self.model.base_url,
      content_type=["leak"]
    )

    try:
      with sync_playwright() as playwright:
        context = self._launch_persistent_context(playwright)
        self.browser = context.browser

        context.set_default_timeout(600000)
        context.set_default_navigation_timeout(600000)

        self.timeout_timer = Timer(self.model.rule_config.m_timeout, self._terminate_browser)
        self.timeout_timer.start()

        try:
          page = context.pages[0]
          page.goto("about:blank")

          page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
          })

          page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    });
                """)

          if self.model.rule_config.m_resoource_block:
            page.route("**/*", self._handle_route)

          page.goto(self.model.seed_url, wait_until="domcontentloaded")
          page.wait_for_timeout(5000)

          self.model.soup = BeautifulSoup(page.content(), 'html.parser')
          self.model.parse_leak_data(page)

        except Exception:
          print("TRACEBACK:", traceback.format_exc())
        finally:
          self.timeout_timer.cancel()

    except Exception:
      print("TRACEBACK:", traceback.format_exc())

    default_data_model.cards_data = self.model.card_data
    return default_data_model, None

  def _launch_persistent_context(self, playwright):
    user_data_dir = os.path.join(os.getcwd(), "playwright_user_data")

    launch_args = {
      "user_data_dir": user_data_dir,
      "headless": False,
      "viewport": None,
      "args": ["--start-maximized"]
    }

    if self.model.rule_config.m_fetch_proxy is not FetchProxy.NONE:
      launch_args["proxy"] = self.proxy

    context = playwright.firefox.launch_persistent_context(**launch_args)
    return context
