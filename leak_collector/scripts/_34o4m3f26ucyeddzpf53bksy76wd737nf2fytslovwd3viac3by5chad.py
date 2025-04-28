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
class _34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad(leak_extractor_interface, ABC):
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
            cls._instance = super(_34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad.onion/leaks"

    @property
    def base_url(self) -> str:
        return "http://34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad.onion"

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
        return "http://34o4m3f26ucyeddzpf53bksy76wd737nf2fytslovwd3viac3by5chad.onion/contact"

    def append_leak_data(self, leak: leak_model, entity: entity_model):

        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        html_content = page.content()
        self.soup = BeautifulSoup(html_content, 'html.parser')

        leak_cards = self.soup.find_all('div', class_='py-6')

        for card in leak_cards:
            date_tag = card.find('time')
            leak_date = date_tag.text.strip() if date_tag else ""

            # Extract title
            title_tag = card.find('h2')
            title = title_tag.text.strip() if title_tag else ""

            # Extract paragraphs
            parsed_post_text = card.find('div', class_='parsed-post-text')
            paragraphs = []
            if parsed_post_text:
                paragraphs = [p.text.strip() for p in parsed_post_text.find_all('p')]

            full_content = "\n".join(paragraphs)

            downloads = []
            ul_tag = card.find('ul', class_='parsed-post-text')
            if ul_tag:
                li_tags = ul_tag.find_all('li')
                for li in li_tags:
                    a_tag = li.find('a')
                    size_span = li.find('span', class_='inline-block')
                    if a_tag and size_span:
                        downloads.append({
                            "link": a_tag['href'],
                            "file_name": a_tag.get('download'),
                            "size": size_span.text.strip()
                        })

            # Create card_data (leak_model)
            card_data = leak_model(
                m_title=title,
                m_url=page.url,
                m_base_url=self.base_url,
                m_screenshot="",  # optional: you could grab page.screenshot() if needed
                m_content=full_content,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=full_content,
                m_weblink=[],
                m_dumplink=[d["link"] for d in downloads],
                m_content_type=["leaks"]
            )

            entity_data = entity_model(
                m_email_addresses=helper_method.extract_emails(full_content),
                m_phone_numbers=helper_method.extract_phone_numbers(full_content),
            )

            # Append to lists and invoke callback
            self.append_leak_data(card_data, entity_data)