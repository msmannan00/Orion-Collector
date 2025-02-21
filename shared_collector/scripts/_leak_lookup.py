from abc import ABC
from typing import List

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _leak_lookup(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):
        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_leak_lookup, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "https://leak-lookup.com/breaches"

    @property
    def base_url(self) -> str:
        return "https://leak-lookup.com"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "https://www.iana.org/help/example-domains"

    def parse_leak_data(self, page: Page):
       
        while True:
            rows = page.query_selector_all("table tr")

            for row in rows:
                link_element = row.query_selector("td a")
                if not link_element:
                    continue

                site_name = link_element.inner_text()
                site_url = link_element.get_attribute("href")
                dropdown_button = row.query_selector("td .dropdown a")
                if dropdown_button:
                    dropdown_button.click()
                    page.wait_for_timeout(1000)

                    info_link = row.query_selector("td .dropdown-menu a[data-bs-toggle='modal']")
                    if info_link:
                        info_link.click()

                        page.wait_for_selector("#breachModal .modal-body", timeout=5000)
                        page.wait_for_timeout(2000)

                        modal_content = page.query_selector("#breachModal .modal-body")
                        modal_text = modal_content.inner_text() if modal_content else "No data available"

                        self._card_data.append(card_extraction_model(
                            m_title=site_name,
                            m_url=site_url,
                            m_base_url=self.base_url,
                            m_content=modal_text,
                            m_network=helper_method.get_network_type(self.base_url),
                            m_important_content=modal_text,
                            m_weblink=[],
                            m_dumplink=[],
                            m_email_addresses=helper_method.extract_emails(modal_text),
                            m_phone_numbers=helper_method.extract_phone_numbers(modal_text),
                            m_content_type="leaks",
                        ))


                        close_button = page.query_selector("#breachModal .btn-close")
                        if close_button:
                            close_button.click()
                            page.wait_for_timeout(1000)

            next_button = page.query_selector(
                "a.page-link[aria-controls='datatables-indexed-breaches'][data-dt-idx='next']")
            if next_button:
                next_button.click()
                page.wait_for_selector("a.page-link[aria-controls='datatables-indexed-breaches'][data-dt-idx='next']",
                                       timeout=5000)
                page.wait_for_timeout(3000)
            else:
                break