import os
from typing import Dict, Any

import requests
import traceback

from threading import Timer
from playwright.sync_api import sync_playwright, Route
from bs4 import BeautifulSoup

from crawler.constants.enums import PRESIDIO_TO_ENTITY_MODEL_MAP
from crawler.crawler_instance.local_interface_model.leak.telegram_extractor_interface import telegram_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import ChatDataModel
from crawler.crawler_instance.local_shared_model.rule_model import FetchProxy
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS
from crawler.crawler_services.shared.env_handler import env_handler
from crawler.crawler_services.shared.helper_method import helper_method
from telegram_collector.local_client.telegram_helper import parse_data


class RequestParser:

  def __init__(self, proxy: dict, model: telegram_extractor_interface):
    self.proxy = proxy
    self.model = model
    self.model.init_callback(self.callback)
    self.browser = None
    self.timeout_flag = False
    self.timeout_timer = None
    self.production = env_handler.get_instance().env("PRODUCTION") == "1"

  @staticmethod
  def generate_entity_model(res: Dict[str, Any]) -> entity_model:
    entity_data = {}

    for item in res.get("result", []):
      for key, value in item.items():
        field = PRESIDIO_TO_ENTITY_MODEL_MAP.get(key)
        if not field:
          continue
        if isinstance(value, str):
          entity_data.setdefault(field, []).append(value)
        elif isinstance(value, list):
          entity_data.setdefault(field, []).extend(value)

    return entity_model(**entity_data)

  def callback(self):
    if len(self.model.card_data) < 3:
      return False

    try:
      self.production = env_handler.get_instance().env("PRODUCTION") == "1"
      server_url = env_handler.get_instance().env("S_SERVER") if self.production else "http://localhost:8080"
      endpoint = f"{server_url}/api/index/chat"
      entity_endpoint = f"{server_url}/api/index/entity"

      token = redis_controller().invoke_trigger(REDIS_COMMANDS.S_GET_STRING, ["bearertoken", None, None])
      headers = {"Authorization": f"Bearer {token}"} if token else {}

      merged_chat_data = []

      for chat in self.model.card_data:
        content = chat.m_content
        if not content:
          continue

        res = parse_data(content)
        entity = self.generate_entity_model(res).model_dump()
        entity["m_cluster_id"] = "chat"
        entity["m_document_id"] = helper_method.generate_data_hash(chat.m_message_id)
        requests.post(entity_endpoint, json=entity, headers=headers)
        chat_dict = chat.model_dump(mode="json")

        for key, value in entity.items():
          if value not in (None, "", [], {}):
            chat_dict[key] = value

        merged_chat_data.append(chat_dict)

      payload = {"m_chat_data": merged_chat_data, "m_network": "telegram", "m_source_channel_url": self.model.seed_url}

      response = requests.post(endpoint, json=payload, headers=headers)
      if response.status_code == 200:
        self.model.card_data.clear()

      return True

    except Exception as _:
      return False

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
    default_data_model = ChatDataModel(
      m_chat_data=[],
      m_network = "telegram"
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

          page.goto(self.model.base_url, wait_until="domcontentloaded")
          page.wait_for_timeout(5000)

          self.model.soup = BeautifulSoup(page.content(), 'html.parser')
          self.model.parse_leak_data(page)

        except Exception:
          print("TRACEBACK:", traceback.format_exc())
        finally:
          self.timeout_timer.cancel()

    except Exception:
      print("TRACEBACK:", traceback.format_exc())

    default_data_model.m_chat_data = self.model.card_data
    return default_data_model, None

  def _launch_persistent_context(self, playwright):
    user_data_dir = os.path.join(os.getcwd(), "playwright_user_data")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    os.makedirs(base_dir, exist_ok=True)

    launch_args = {"user_data_dir": user_data_dir, "headless": False, "viewport": None, "accept_downloads": True, "args": ["--start-maximized"], "firefox_user_prefs": {"browser.download.folderList": 2, "browser.download.useDownloadDir": True, "browser.download.dir": base_dir,
      "browser.helperApps.neverAsk.saveToDisk": ",".join(["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "application/pdf", "application/zip", "application/octet-stream"]), "browser.download.manager.showWhenStarting": False, "browser.helperApps.alwaysAsk.force": False,
      "pdfjs.disabled": True, "browser.download.panel.shown": False, "browser.download.manager.closeWhenDone": True, "browser.download.animateNotifications": False, "browser.download.improvements_to_download_panel": False}}

    if self.model.rule_config.m_fetch_proxy is not FetchProxy.NONE:
      launch_args["proxy"] = self.proxy

    context = playwright.firefox.launch_persistent_context(**launch_args)
    return context
