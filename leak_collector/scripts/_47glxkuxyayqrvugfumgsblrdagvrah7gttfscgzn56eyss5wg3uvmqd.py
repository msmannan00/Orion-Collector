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
from datetime import datetime

class _47glxkuxyayqrvugfumgsblrdagvrah7gttfscgzn56eyss5wg3uvmqd(leak_extractor_interface, ABC):
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
            cls._instance = super(_47glxkuxyayqrvugfumgsblrdagvrah7gttfscgzn56eyss5wg3uvmqd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "https://47glxkuxyayqrvugfumgsblrdagvrah7gttfscgzn56eyss5wg3uvmqd.onion"

    @property
    def base_url(self) -> str:
        return "https://47glxkuxyayqrvugfumgsblrdagvrah7gttfscgzn56eyss5wg3uvmqd.onion"

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
        return "https://47glxkuxyayqrvugfumgsblrdagvrah7gttfscgzn56eyss5wg3uvmqd.onion"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    def parse_leak_data(self, page: Page):
        try:
            cards = page.query_selector_all('.col-lg-6')

            for card in cards:
                try:
                    title = card.query_selector("span:has-text('Name:') + p")
                    revenue = card.query_selector("span:has-text('Revenue:') + p")
                    country = card.query_selector("span:has-text('Сountry:') + p")

                    title = title.text_content() if title else "No Title"
                    revenue = revenue.text_content() if revenue else "No Revenue"
                    country = country.text_content() if country else "No Country"

                    date_el = page.query_selector("span:has-text('Date:') + p")
                    size_el = page.query_selector("span:has-text('Size:') + p")
                    date = date_el.text_content() if date_el else "No Date"
                    size = size_el.text_content() if size_el else "No Size"

                    show_files_el = page.query_selector('a:has-text("Show/Download files")')
                    download_listing_el = page.query_selector('a:has-text("Download file listing")')
                    show_files_link = show_files_el.get_attribute('href') if show_files_el else ""
                    download_listing_link = download_listing_el.get_attribute('href') if download_listing_el else ""

                    description = (
                        f"Title: {title}\nRevenue: {revenue}\nCountry: {country}\n"
                        f"Date: {date}\nSize: {size}\nShow Files Link: {show_files_link}\nDownload Link: {download_listing_link}"
                    )

                    if date != "No Date":
                        try:
                            date = datetime.strptime(date, "%m/%d/%Y %H:%M").strftime("%Y-%m-%d")
                        except ValueError:
                            date = "Invalid Date Format"

                except Exception as e:
                    print(f"Error occurred while extracting data from a card: {e}")

                card_data = leak_model(
                    m_title=title,
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_screenshot="",
                    m_content=description,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=description,
                    m_weblink=[],
                    m_dumplink=[show_files_link, download_listing_link],
                    m_content_type=["leaks"],
                    m_revenue=revenue,
                    m_leak_date=date,
                    m_data_size=size
                )

                entity_data = entity_model(
                    m_email_addresses=helper_method.extract_emails(description),
                    m_phone_numbers=helper_method.extract_phone_numbers(description),
                    m_country_name=country,
                )

                self.append_leak_data(card_data, entity_data)

        except Exception as e:
            print(f"An error occurred while parsing leak data: {e}")
