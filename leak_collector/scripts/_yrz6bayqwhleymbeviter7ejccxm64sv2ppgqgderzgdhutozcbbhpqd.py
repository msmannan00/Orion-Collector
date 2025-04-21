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

class _yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd(leak_extractor_interface, ABC):
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
            cls._instance = super(_yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd.onion/"

    @property
    def base_url(self) -> str:
        return "http://yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd.onion/"

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
        return "http://yrz6bayqwhleymbeviter7ejccxm64sv2ppgqgderzgdhutozcbbhpqd.onion/contacts"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        soup = BeautifulSoup(page.content(), 'html.parser')
        card_divs = soup.find_all('div', class_='flex w-full mt-3 bg-stone-100 rounded-lg p-4 shadow-md')

        for card in card_divs:
            try:
                # Title
                title_tag = card.find('div', class_='text-2xl font-bold')
                title = title_tag.get_text(strip=True) if title_tag else "N/A"

                # Weblink
                weblink_tag = card.find_all('div', class_='flex flex-row')[0].find('span')
                weblink = weblink_tag.get_text(strip=True) if weblink_tag else "N/A"
                print(weblink)
                # Revenue
                revenue_tag = card.find_all('div', class_='flex flex-row')[1].find('span')
                revenue = revenue_tag.get_text(strip=True) if revenue_tag else "N/A"
                print(revenue)
                # Country
                country_tag = card.find_all('div', class_='flex flex-row')[2].find('span')
                country = country_tag.get_text(strip=True) if country_tag else "N/A"
                print(country)
                # Description
                desc_tag = card.find('div', class_='text-gray-900 whitespace-pre-line')
                description = desc_tag.get_text(strip=True) if desc_tag else "N/A"

                # Explore Data link
                explore_link_tag = card.find('a', string=lambda s: s and 'Explore data' in s)
                explore_href = explore_link_tag['href'] if explore_link_tag else "#"
                full_explore_url = self.base_url + explore_href if not explore_href.startswith("http") else explore_href

                # --- Creating model objects ---
                m_content = f"{title}\n{weblink}\n{revenue}\n{country}\n{description}"

                card_data = leak_model(
                    m_title=title,
                    m_url=full_explore_url,
                    m_base_url=self.base_url,
                    m_screenshot="",
                    m_content=m_content,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=description,
                    m_weblink=[weblink],
                    m_dumplink=[],
                    m_content_type=["leaks"],
                )

                entity_data = entity_model(
                    m_email_addresses=helper_method.extract_emails(m_content),
                    m_phone_numbers=helper_method.extract_phone_numbers(m_content),
                )

                self.append_leak_data(card_data, entity_data)

            except Exception as e:
                print(f"[ERROR] Failed to parse card: {e}")
