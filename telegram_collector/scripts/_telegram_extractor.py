from abc import ABC
from typing import List
from bs4 import BeautifulSoup
import time

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import telegram_chat_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from selenium.webdriver.common.by import By


class _telegram_extractor(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self, callback=None):
        self._card_data = []
        self._initialized = None
        self._redis_instance = redis_controller()
        self.callback = callback

    def __new__(cls, callback=None):
        if cls._instance is None:
            cls._instance = super(_telegram_extractor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "https://web.telegram.org/k/"

    @property
    def base_url(self) -> str:
        return "https://web.telegram.org/"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.NONE, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[telegram_chat_model]:
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "https://web.telegram.org/"

    def append_leak_data(self, chat: telegram_chat_model) -> None:
        self._card_data.append(chat)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page=None):
        page.goto(self.seed_url, wait_until="networkidle")
        print("Please scan the QR code to log in.")
        time.sleep(30)

        def wait_for_main_columns():
            while True:
                try:
                    if driver.find_element(By.ID, "main-columns"):
                        break
                except:
                    pass
                time.sleep(2)

        def scroll_to_top():
            try:
                scrollable_div = driver.find_element(By.CLASS_NAME, "scrollable-y")
                driver.execute_script("arguments[0].scrollTop = 0;", scrollable_div)
            except Exception as e:
                print(f"Scroll error: {e}")

        def click_chat(chat):
            try:
                driver.execute_script("arguments[0].click();", chat)
                time.sleep(2)
            except Exception as e:
                print(f"Click error: {e}")

        def extract_from_html(html: str):
            soup = BeautifulSoup(html, 'html.parser')
            try:
                return telegram_chat_model(
                    message_id=soup.find('div', class_='document-container')['data-mid'],
                    content_html=str(soup),
                    timestamp=soup.find('div', class_='time-inner')['title'],
                    views=soup.find('span', class_='post-views').text.strip() if soup.find('span', class_='post-views') else None,
                    file_name=soup.find('middle-ellipsis-element').text if soup.find('middle-ellipsis-element') else None,
                    file_size=soup.find('div', class_='document-size').text.strip() if soup.find('div', class_='document-size') else None,
                    forwarded_from=soup.find('span', class_='peer-title').text.strip() if soup.find('span', class_='peer-title') else None,
                    peer_id=soup.find('div', class_='document-container')['data-peer-id']
                )
            except Exception as e:
                print(f"Error parsing HTML: {e}")
                return None

        wait_for_main_columns()

        last_active = None
        while True:
            try:
                chat_elements = driver.find_elements(By.XPATH, "//ul/a[contains(@class, 'chatlist-chat')]")
                for chat in chat_elements:
                    if "active" in chat.get_attribute("class") and chat != last_active:
                        click_chat(chat)
                        scroll_to_top()
                        last_active = chat
                        time.sleep(3)

                        messages = driver.find_elements(By.CSS_SELECTOR, "div.bubble.channel-post.with-beside-button.hide-name.photo.is-in.can-have-tail")
                        print(f"Found {len(messages)} messages.")
                        for msg in messages:
                            html = msg.get_attribute("innerHTML")
                            parsed = extract_from_html(html)
                            if parsed:
                                self.append_leak_data(parsed)
            except Exception as e:
                print(f"Main loop error: {e}")

            time.sleep(1)
