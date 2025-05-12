import time
from abc import ABC
from datetime import datetime, timedelta
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.telegram_extractor_interface import telegram_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import telegram_chat_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.env_handler import env_handler
from social_collector.local_client.assets.enums import TelegramConfig
from social_collector.local_client.helper.telegram.telegram_message_helper import telegram_message_helper


class _telegram_extractor(telegram_extractor_interface, ABC):
  _instance = None
  _seed_url = None

  def __init__(self, callback=None):
    self.callback = callback
    self._card_data = []
    self._entity_data = []
    self.soup = None
    self._initialized = None
    self._redis_instance = redis_controller()
    self._channel_name = None

  def init_callback(self, callback=None):
    self.callback = callback

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  @property
  def seed_url(self) -> str:
    return self._seed_url

  @property
  def base_url(self) -> str:
    return "https://web.telegram.org/k/"

  @property
  def entity_data(self) -> List[entity_model]:
    return self._entity_data

  @property
  def rule_config(self) -> RuleModel:
    return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT, m_resoource_block=False)

  @property
  def channel_name(self) -> str:
    return self._channel_name

  @property
  def card_data(self) -> List[telegram_chat_model]:
    return self._card_data

  def invoke_db(self, command: int, key: str, default_value):
    return self._redis_instance.invoke_trigger(command, [key, default_value, None])

  def contact_page(self) -> str:
    return "https://web.telegram.org/"

  def append_leak_data(self, leak: telegram_chat_model):
    self._card_data.append(leak)
    if self.callback:
      if self.callback():
        self._card_data.clear()
        self._entity_data.clear()

  def parse_leak_data(self, page: Page = None):
    try:
      page.wait_for_selector(".chatlist-chat", timeout=150000)
    except:
      return

    chat_items = page.query_selector_all(".chatlist-chat")
    if not chat_items:
      return

    for index in range(len(chat_items)):
      channel_date = None

      chat_items = page.query_selector_all(".chatlist-chat")
      if index >= len(chat_items):
        break

      chat = chat_items[index]
      try:
        title = chat.inner_text().split('\n')[0]
      except:
        title = f"Chat #{index + 1}"

      try:
        chat.click()
        time.sleep(2)
        page.wait_for_selector(".chat-info", state="visible", timeout=10000)
      except:
        continue

      try:
        title_element = page.query_selector(".chat-info .peer-title")
        if title_element:
          channel_name = title_element.inner_text().strip()
          peer_id = title_element.get_attribute("data-peer-id")
        else:
          channel_name = title
          peer_id = None
      except:
        channel_name = title
        peer_id = None
      self._channel_name= channel_name

      channel_url = telegram_message_helper.get_instance().open_sidebar(page)
      # if channel_name not in TelegramConfig.ALLOWED_TELEGRAM_CHANNEL_NAMES and channel_url not in TelegramConfig.ALLOWED_TELEGRAM_CHANNEL_ID:
      #   continue

      stored_date = self.invoke_db(REDIS_COMMANDS.S_GET_STRING, CUSTOM_SCRIPT_REDIS_KEYS.TELEGRAM_CHANNEL_PARSED.value + peer_id, None)
      if stored_date:
        stored_date = datetime.strptime(stored_date, "%Y-%m-%d").date()

      scrollable = page.query_selector(".chats-container .scrollable.scrollable-y")
      if not scrollable:
        continue

      page.evaluate("(el) => el.scrollTop = el.scrollHeight", scrollable)
      time.sleep(1)

      telegram_channel_id = telegram_message_helper.get_instance().get_channel_shareable_link(page)
      seen_messages = set()
      threshold_date = datetime.now().date() - timedelta(days=2500)
      scroll_count = 0
      max_scrolls = 200
      self._seed_url = peer_id

      while scroll_count < max_scrolls and scroll_count < 5:
        sections = page.query_selector_all("section.bubbles-date-group")
        stop_scroll = False

        for section in reversed(sections):
          message_date = telegram_message_helper.get_instance().extract_message_date(section)
          if not channel_date:
            channel_date = message_date
            if channel_date is None:
              time.sleep(5)
              break
          if message_date and stored_date and message_date <= stored_date and env_handler.get_instance().env("PRODUCTION") == "1":
            scroll_count = max_scrolls
            break

          if message_date and message_date <= threshold_date:
            stop_scroll = True
            break
          bubbles = section.query_selector_all(".bubble.channel-post")
          for bubble in reversed(bubbles):
            try:
              msg_id = bubble.get_attribute("data-mid")
              if not msg_id or msg_id in seen_messages:
                continue
              html = telegram_message_helper.get_instance().get_bubble_html(bubble)
              model = telegram_message_helper.get_instance().extract_messages(page, html, channel_name, msg_id, telegram_channel_id, channel_url)
              scroll_count = 0
              if model:
                model.m_message_date = message_date
                self.append_leak_data(model)
                seen_messages.add(msg_id)
            except Exception as _:
              continue

        if stop_scroll:
          break

        telegram_message_helper.get_instance().scroll_up(page, scrollable)
        scroll_count += 1
      if channel_date:
        self.invoke_db(REDIS_COMMANDS.S_SET_STRING, CUSTOM_SCRIPT_REDIS_KEYS.TELEGRAM_CHANNEL_PARSED.value + peer_id, channel_date.isoformat())
      self.callback()
      self._card_data.clear()
      self._entity_data.clear()
