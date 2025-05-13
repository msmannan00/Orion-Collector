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

class _zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid(leak_extractor_interface, ABC):
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
            cls._instance = super(_zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid.onion"

    @property
    def base_url(self) -> str:
        return "http://zohlm7ahjwegcedoz7lrdrti7bvpofymcayotp744qhx6gjmxbuo2yid.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "https://t.me/RHouseNews"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        processed_urls = set()

        page.wait_for_timeout(15000)
        page.wait_for_selector(".cls_records .cls_record", timeout=10000)

        title_links = []
        cards = page.query_selector_all(".cls_records .cls_record")
        for card in cards:
            title_link = card.query_selector("a")
            if title_link:
                href = title_link.get_attribute("href")
                if href:
                    title_links.append(href)

        for index, link in enumerate(title_links):
            try:
                if link in processed_urls:
                    print(f"Link {link} already processed, skipping...")
                    continue
                processed_urls.add(link)

                with page.expect_navigation(wait_until="domcontentloaded"):
                    page.goto(self.base_url + link)

                page.wait_for_timeout(2000)

                title_element = page.query_selector("p.cls_headerXtraLarge")
                title = title_element.inner_text().strip() if title_element else "Unknown"

                description_element = page.query_selector(
                    ".cls_recordDetailsTop .cls_verticalContent p:not(.cls_headerMedium):not(.cls_headerXtraLarge)"
                )
                description = description_element.inner_text().strip() if description_element else "No description"

                website_element = page.query_selector(".cls_recordDetailsMiddleBottom .cls_verticalContent a")
                website_link = website_element.get_attribute("href").strip() if website_element else "No website link"

                revenue_element = page.query_selector(
                    ".cls_recordDetailsMiddleBottom .cls_verticalContent p:has-text('Revenue') + p"
                )
                revenue = revenue_element.inner_text().strip() if revenue_element else "Unknown"

                employees_element = page.query_selector(
                    ".cls_recordDetailsMiddleBottom .cls_verticalContent p:has-text('Employees') + p"
                )
                employees = employees_element.inner_text().strip() if employees_element else "Unknown"

                action_date_element = page.query_selector(".cls_recordDetailsMiddleTopRight .cls_headerMedium")
                action_date_text = action_date_element.inner_text().strip() if action_date_element else "Unknown"
                try:
                    action_date = (
                        datetime.strptime(action_date_text, "%d/%m/%Y").date()
                        if action_date_text != "Unknown"
                        else None
                    )
                except ValueError:
                    action_date = None

                data_size_element = page.query_selector(
                    ".cls_recordDetailsMiddleBottom .cls_verticalContent p:has-text('Downloaded') + p"
                )
                data_size = data_size_element.inner_text().strip() if data_size_element else "Unknown"

                status_element = page.query_selector(
                    ".cls_recordDetailsMiddleBottom p.cls_headerLarge:has-text('Status:')"
                )
                status = status_element.inner_text().replace("Status:", "").strip() if status_element else "Unknown"

                social_links = []
                social_elements = page.query_selector_all(".cls_recordDetailsRight a")
                for social in social_elements:
                    social_link = social.get_attribute("href")
                    if social_link:
                        social_links.append(social_link.strip())

                dumplink_element = page.query_selector(".cls_rawText a")
                dumplink = dumplink_element.get_attribute("href").strip() if dumplink_element else "No dumplink"

                password_element = page.query_selector(".cls_rawText p:has-text('Password:') + p")
                password = password_element.inner_text().strip() if password_element else "No password"

                description += f"\n status: {status} \nemployee count: {employees}"

                card_data = leak_model(
                    m_title=title,
                    m_url=page.url,
                    m_base_url=self.base_url,
                    m_screenshot=helper_method.get_screenshot_base64(page, title),
                    m_content=description,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_important_content=description[:500],
                    m_weblink=[website_link],
                    m_dumplink=[dumplink],
                    m_content_type=["leaks"],
                    m_revenue=revenue,
                    m_leak_date=action_date,
                    m_data_size=data_size,
                    m_password=password,
                )

                entity_data = entity_model(
                    m_email_addresses=helper_method.extract_emails(description),
                    m_phone_numbers=helper_method.extract_phone_numbers(description),
                    m_social_media_profiles=social_links,
                )

                self.append_leak_data(card_data, entity_data)

                with page.expect_navigation(wait_until="domcontentloaded"):
                    page.goto(self.base_url)

                page.wait_for_timeout(15000)

            except Exception as e:
                print(f"Error processing link {link} at index {index}: {e}")