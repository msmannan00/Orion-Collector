from abc import ABC
from typing import List
from bs4 import BeautifulSoup
import time
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import telegram_chat_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from playwright.sync_api import sync_playwright  # Playwright import for sync usage


class _telegram_extractor(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self, callback=None):
        self._card_data = []
        self._initialized = None
        self._redis_instance = redis_controller()
        self.callback = callback
        self.browser = None
        self.context = None
        self.page = None

    def __new__(cls, callback=None):
        if cls._instance is None:
            cls._instance = super(_telegram_extractor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _initialize_browser(self):
        """Initialize Playwright browser and page."""
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=True)  # Start browser in headless mode
            print("Browser initialized")
            self.context = self.browser.new_context()  # New context for isolation
            self.page = self.context.new_page()  # Open a new page
            print("Page initialized")

    def close_browser(self):
        """Close Playwright browser."""
        if self.browser:
            self.browser.close()

    @property
    def seed_url(self) -> str:
        return "https://web.telegram.org/k/"

    @property
    def base_url(self) -> str:
        return "https://web.telegram.org/"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM, m_resoource_block=False)

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
        print("Please scan the QR code to log in.")

        def wait_for_main_columns(self):
            """Wait for the main columns to appear after login using page locator."""
            while True:
                try:
                    # Use locator to wait for the main columns element to be visible
                    main_columns_locator = page.locator("#main-columns")
                    main_columns_locator.wait_for(state="visible")
                    print("Main columns are loaded.")
                    break  # Exit the loop once the main columns are visible
                except Exception as e:
                    print(f"Waiting for main columns: {e}")
                time.sleep(2)

        def scroll_to_top():
            """Scroll to the top of the chat if possible."""
            try:
                scrollable_div = self.page.query_selector(".scrollable-y")
                self.page.evaluate("arguments[0].scrollTop = 0;", scrollable_div)
            except Exception as e:
                print(f"Scroll error: {e}")

        def click_chat(chat):
            """Click on the chat element to open the chat window."""
            try:
                chat.click()  # Playwright has a click method on elements directly
                time.sleep(2)
            except Exception as e:
                print(f"Click error: {e}")

        def extract_from_html(html: str):
            """Extract chat data from the HTML of a message."""
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

        # Wait until main columns are available
        wait_for_main_columns(self)

        last_active = None
        while True:
            try:
                # Locate active chat elements
                chat_elements = self.page.query_selector_all("ul a.chatlist-chat")
                for chat in chat_elements:
                    if "active" in chat.get_attribute("class") and chat != last_active:
                        click_chat(chat)
                        last_active = chat
                        time.sleep(3)

                        # Locate message elements and parse
                        messages = self.page.query_selector_all(
                            "div.bubble.channel-post.with-beside-button.hide-name.photo.is-in.can-have-tail")
                        print(f"Found {len(messages)} messages.")
                        for msg in messages:
                            html = msg.inner_html()
                            parsed = extract_from_html(html)
                            if parsed:
                                self.append_leak_data(parsed)

            except Exception as e:
                print(f"Main loop error: {e}")
                time.sleep(1)
