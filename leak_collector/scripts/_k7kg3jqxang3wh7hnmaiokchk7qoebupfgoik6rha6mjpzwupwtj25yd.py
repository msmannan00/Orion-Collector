from abc import ABC
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method
from bs4 import BeautifulSoup

class _k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd(leak_extractor_interface, ABC):
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

    def __new__(cls, callback=None):
        if cls._instance is None:
            cls._instance = super(_k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion"

    @property
    def base_url(self) -> str:
        return "http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return f"{self.base_url}/contact.php"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    from bs4 import BeautifulSoup

    def parse_leak_data(self, page: Page):
        page_number = 1

        while True:
            # Navigate to the current page
            page.goto(f"{self.seed_url}/index.php?page={page_number}")

            links = page.eval_on_selector_all(
                "th.News[onclick^='viewtopic']",
                "elements => elements.map(el => el.getAttribute('onclick').match(/'([^']+)'/)[1])"
            )

            if not links:
                break

            full_links = [f"{self.base_url.rstrip('/')}/topic.php?id={link_id}" for link_id in links]

            for card_url in full_links:
                new_page = page.context.new_page()
                new_page.goto(card_url)

                try:
                    new_page.wait_for_selector("body")

                    location_element = new_page.query_selector("i.location")
                    location_text = new_page.evaluate("(element) => element.nextSibling?.textContent?.trim()",
                                                      location_element) if location_element else "Unknown"
                    website_element = new_page.query_selector("i.link")
                    website_text = new_page.evaluate("(element) => element.nextSibling?.textContent?.trim()",
                                                     website_element) if website_element else "Unknown"
                    # Extract all nested divs under the same container
                    details_divs = new_page.query_selector_all("th.News div")

                    views_text = data_size_text = added_date_text = publication_date_text = "Unknown"

                    for div in details_divs:
                        text = div.inner_text().strip()

                        if text.startswith("👁️ views:"):
                            views_text = text.replace("👁️ views:", "").strip()

                        elif text.startswith("amount of data:"):
                            data_size_text = text.replace("amount of data:", "").strip()

                        elif text.startswith("added:"):
                            added_date_text = text.replace("added:", "").strip()

                        elif text.startswith("publication date:"):
                            publication_date_text = text.replace("publication date:", "").strip()

                    print(publication_date_text)

                    information_element = new_page.query_selector("div:has-text('information')")
                    if information_element:
                        raw_information = information_element.inner_text().strip()
                        information_text = raw_information.split("information:", 1)[1].split("comment:", 1)[0].strip()
                    else:
                        information_text = "Unknown"

                    comment_element = new_page.query_selector("div:has-text('comment')")
                    if comment_element:
                        raw_comment = comment_element.inner_text().strip()
                        comment_text = raw_comment.split("comment:", 1)[1].strip()
                    else:
                        comment_text = "Unknown"

                    m_content = f"{information_text}\n\n{comment_text}"
                    screenshot_path = f"screenshot_{card_url.split('=')[-1]}.png"
                    try:
                        new_page.screenshot(path=screenshot_path)
                    except Exception:
                        screenshot_path = "screenshot_missing.png"

                    card_data = leak_model(
                        m_title=new_page.title(),
                        m_url=new_page.url,
                        m_base_url=self.base_url,
                        m_content=m_content,
                        m_important_content=m_content,
                        m_network=helper_method.get_network_type(self.base_url),
                        m_content_type=["leaks"],
                        m_screenshot=screenshot_path,
                        m_weblink=[website_text],
                        m_dumplink=[],

                        # m_leak_date=datetime.strptime(added_date_text, "%Y-%m-%d").date() if added_date_text else None,
                        m_data_size=data_size_text,
                        m_revenue=None
                    )

                    entity_data = entity_model(
                        m_email_addresses=helper_method.extract_emails(m_content),
                        m_phone_numbers=helper_method.extract_phone_numbers(m_content),
                    )

                    self.append_leak_data(card_data, entity_data)
                except Exception as e:
                    print(f"Failed to extract data for {card_url}: {e}")
                new_page.close()

            page_number += 1
