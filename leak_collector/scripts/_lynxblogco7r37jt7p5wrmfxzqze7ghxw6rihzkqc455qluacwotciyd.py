from abc import ABC
from datetime import datetime
from typing import List
import time
from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _lynxblogco7r37jt7p5wrmfxzqze7ghxw6rihzkqc455qluacwotciyd(leak_extractor_interface, ABC):
    _instance = None

    def __new__(cls, callback=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, callback=None):
        self.callback = callback
        self._card_data = []
        self._entity_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def init_callback(self, callback=None):
        self.callback = callback

    @property
    def seed_url(self) -> str:
        return "http://lynxblogco7r37jt7p5wrmfxzqze7ghxw6rihzkqc455qluacwotciyd.onion/leaks"

    @property
    def base_url(self) -> str:
        return "http://lynxblogco7r37jt7p5wrmfxzqze7ghxw6rihzkqc455qluacwotciyd.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(
            m_fetch_proxy=FetchProxy.TOR,
            m_fetch_config=FetchConfig.PLAYRIGHT,
            m_resoource_block=True
        )

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://lynxblogco7r37jt7p5wrmfxzqze7ghxw6rihzkqc455qluacwotciyd.onion/leaks"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    def parse_leak_data(self, page: Page):
        try:
            time.sleep(30)
            cards = page.query_selector_all('.news__block.chat__block')

            for card in cards:
                title = card.query_selector('.chat__block-title').inner_text().strip() if card.query_selector('.chat__block-title') else "No Title"
                date_text = card.query_selector('.chat__block-date span').inner_text().strip() if card.query_selector('.chat__block-date span') else "No Date"
                date = datetime.strptime(date_text, "%d/%m/%Y").date() if date_text != "No Date" else None

                link_element = card.query_selector('a.button-blue')
                full_url = self.base_url + link_element.get_attribute('href') if link_element else None

                description = revenue = downloaded = urls = ""

                if full_url:
                    detail_page = page.context.new_page()
                    detail_page.goto(full_url)

                    try:
                        detail_page.wait_for_selector('.detailed p', timeout=10000)
                    except:
                        detail_page.close()
                        continue

                    description = detail_page.query_selector('.detailed p').inner_text().strip() if detail_page.query_selector('.detailed p') else "No description available"
                    income = detail_page.query_selector('span:has-text("Income") + p').inner_text().strip() if detail_page.query_selector('span:has-text("Income") + p') else "No income info"
                    revenue = detail_page.query_selector('span:has-text("Revenue") + p').inner_text().strip() if detail_page.query_selector('span:has-text("Revenue") + p') else "No revenue info"
                    downloaded = detail_page.query_selector('span:has-text("Downloaded") + p').inner_text().strip() if detail_page.query_selector('span:has-text("Downloaded") + p') else "No data size info"
                    employees = detail_page.query_selector('span:has-text("Employees") + p').inner_text().strip() if detail_page.query_selector('span:has-text("Employees") + p') else "No employee info"

                    urls = [a.get_attribute('href') for a in detail_page.query_selector_all('a') if a.get_attribute('href')]
                    description += f"\nURLs: {', '.join(urls)} \nIncome: {income}, \nEmployees: {employees}"

                    detail_page.close()

                card_data = leak_model(
                    m_title=title,
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_screenshot=helper_method.get_screenshot_base64(page, title),
                    m_content=description,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=description,
                    m_content_type=["leaks"],
                    m_revenue=revenue,
                    m_data_size=downloaded,
                    m_leak_date=date,
                    m_weblink=urls,
                )

                entity_data = entity_model(
                    m_email_addresses=helper_method.extract_emails(description),
                    m_phone_numbers=helper_method.extract_phone_numbers(description),
                )

                self.append_leak_data(card_data, entity_data)

        except Exception as e:
            print(f"An error occurred while parsing leak data: {e}")
