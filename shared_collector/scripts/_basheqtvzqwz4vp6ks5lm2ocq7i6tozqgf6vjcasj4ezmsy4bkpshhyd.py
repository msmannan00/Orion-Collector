from abc import ABC
from typing import List

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):
        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:

        return "http://basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd.onion/"

    @property
    def base_url(self) -> str:

        return "http://basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd.onion/"

    @property
    def rule_config(self) -> RuleModel:

        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:

        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:

        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:

        return "http://basheqtvzqwz4vp6ks5lm2ocq7i6tozqgf6vjcasj4ezmsy4bkpshhyd.onion/contact_us.php"

    def parse_leak_data(self, page: Page):
        page.wait_for_selector('.main__contant')  

        title = page.title()

        deadline_element = page.query_selector('.deadline:first-of-type')
        deadline = deadline_element.inner_text().replace("Deadline: ", "") if deadline_element else "N/A"

        views_element = page.query_selector('.deadline:last-of-type')
        views = views_element.inner_text().replace("Views: ", "") if views_element else "N/A"

        country_element = page.query_selector('.count__text')
        country = country_element.inner_text() if country_element else "N/A"

        description_element = page.query_selector('.dsc__text')
        description = description_element.inner_text() if description_element else "N/A"

        image_urls = []
        images = page.query_selector_all('img')
        for img in images:
            src = img.get_attribute('src')
            if src:
                image_urls.append(src)

        hrefs = []
        links = page.query_selector_all('a')
        for link in links:
            href = link.get_attribute('href')
            if href:
                hrefs.append(href)

        card_data = card_extraction_model(
            m_title=title,
            m_url=page.url,
            m_base_url=self.base_url,
            m_content=f"Deadline: {deadline}\nViews: {views}\nCountry: {country}\nDescription: {description}",
            m_network=helper_method.get_network_type(self.base_url),
            m_important_content=f"Deadline: {deadline}\nViews: {views}\nCountry: {country}\nDescription: {description}",
            m_weblink=hrefs,
            m_dumplink=image_urls,
            m_email_addresses=helper_method.extract_emails(description),
            m_phone_numbers=helper_method.extract_phone_numbers(description),
            m_content_type="leaks",
        )
        self._card_data.append(card_data)
