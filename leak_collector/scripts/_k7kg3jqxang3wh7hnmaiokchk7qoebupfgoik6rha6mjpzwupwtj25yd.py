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
        return "http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion/contact.php"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()


    def parse_leak_data(self, page: Page):
        page_number = 1

        while True:
            page.goto(f"{self.seed_url}/index.php?page={page_number}",timeout=60000)

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

                    website_element = new_page.query_selector("i.link")
                    website_text = new_page.evaluate("(element) => element.nextSibling?.textContent?.trim()",
                                                     website_element) if website_element else "Unknown"
                    html = new_page.content()

                    soup = BeautifulSoup(html, 'html.parser')

                    news_element = soup.find('th', class_='News')

                    if news_element:
                        m_content = news_element.get_text(strip=True)
                    else:
                        m_content = "No content found"
                    words = m_content.split()
                    if len(words) > 500:
                        m_important_content = " ".join(words[:500])
                    else:
                        m_important_content = m_content


                    download_links_element = new_page.query_selector("div:has-text('DOWNLOAD LINKS:')")
                    dum_links = []
                    if download_links_element:
                        download_links_text = download_links_element.inner_text().strip()
                        if "DOWNLOAD LINKS:" in download_links_text:
                            links_section = download_links_text.split("DOWNLOAD LINKS:")[1].strip()
                            dum_links = [link.strip() for link in links_section.split("\n") if link.startswith("http")]


                    card_data = leak_model(
                        m_title=new_page.title(),
                        m_url=new_page.url,
                        m_base_url=self.base_url,
                        m_content=m_content,
                        m_important_content=m_important_content,
                        m_network=helper_method.get_network_type(self.base_url),
                        m_content_type=["leaks"],
                        m_screenshot=helper_method.get_screenshot_base64(new_page,new_page.title()),
                        m_weblink=[website_text],
                        m_dumplink=dum_links,

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