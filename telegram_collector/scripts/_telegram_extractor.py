from abc import ABC
from typing import List
from bs4 import BeautifulSoup
import time

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import telegram_chat_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS


class _telegram_extractor(leak_extractor_interface, ABC):
  _instance = None

  def __init__(self, callback=None):
    self.callback = callback
    self._card_data = []
    self._entity_data = []
    self.soup = None
    self._initialized = None
    self._redis_instance = redis_controller()

  def init_callback(self, callback=None):
    self.callback = callback

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  @property
  def seed_url(self) -> str:
    return "https://web.telegram.org/k/"

  @property
  def base_url(self) -> str:
    return "https://web.telegram.org/"

  @property
  def entity_data(self) -> List[entity_model]:
      return self._entity_data

  @property
  def rule_config(self) -> RuleModel:
    return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT, m_resoource_block=False)

  @property
  def card_data(self) -> List[telegram_chat_model]:
    return self._card_data

  def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
    return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

  def contact_page(self) -> str:
    return "https://web.telegram.org/"

  def append_leak_data(self, leak: telegram_chat_model, entity: entity_model):
    self._card_data.append(leak)
    self._entity_data.append(entity)
    if self.callback:
      self.callback()

  @staticmethod
  def wait_for_main_columns(page):
    while True:
      try:
        main_columns_locator = page.locator("#main-columns")
        main_columns_locator.wait_for(state="visible")
        print("Main columns are loaded.")
        break
      except Exception as e:
        print(f"Waiting for main columns: {e}")
      time.sleep(2)

  @staticmethod
  def scroll_to_top(page):
    try:
      scrollable_div = page.query_selector(".scrollable-y")
      page.evaluate("arguments[0].scrollTop = 0;", scrollable_div)
    except Exception as e:
      print(f"Scroll error: {e}")

  @staticmethod
  def click_chat(chat):
    try:
      chat.click()
      time.sleep(2)
    except Exception as e:
      print(f"Click error: {e}")

  @staticmethod
  def extract_from_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    try:
      return telegram_chat_model(
        message_id=soup.find('div', class_='document-container')['data-mid'],
        content_html=str(soup),
        timestamp=soup.find('div', class_='time-inner')['title'],
        views=soup.find('span', class_='post-views').text.strip() if soup.find('span',
                                                                                 class_='post-views') else None,
        file_name=soup.find('middle-ellipsis-element').text if soup.find(
          'middle-ellipsis-element') else None,
        file_size=soup.find('div', class_='document-size').text.strip() if soup.find('div',
                                                                                       class_='document-size') else None,
        forwarded_from=soup.find('span', class_='peer-title').text.strip() if soup.find('span',
                                                                                          class_='peer-title') else None,
        peer_id=soup.find('div', class_='document-container')['data-peer-id']
      )
    except Exception as e:
      print(f"Error parsing HTML: {e}")
      return None

  def parse_leak_data(self, page:Page=None):
    self. wait_for_main_columns(page)
    last_active = None
    while True:
      try:
        chat_elements = page.query_selector_all("ul a.chatlist-chat")
        for chat in chat_elements:
          if "active" in chat.get_attribute("class") and chat != last_active:
            self.click_chat(chat)
            last_active = chat
            time.sleep(3)

            messages = page.query_selector_all("div.bubble.channel-post.with-beside-button.hide-name.photo.is-in.can-have-tail")
            print(f"Found {len(messages)} messages.")
            for msg in messages:
              html = msg.inner_html()
              parsed = self.extract_from_html(html)
              if parsed:
                self.append_leak_data(parsed, entity_model())

      except Exception as e:
        print(f"Main loop error: {e}")
        time.sleep(1)
