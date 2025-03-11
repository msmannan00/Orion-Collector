from abc import ABC
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _embargobe3n5okxyzqphpmk3moinoap2snz5k6765mvtkk7hhi544jid(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):
        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_embargobe3n5okxyzqphpmk3moinoap2snz5k6765mvtkk7hhi544jid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://embargobe3n5okxyzqphpmk3moinoap2snz5k6765mvtkk7hhi544jid.onion/#/"

    @property
    def base_url(self) -> str:
        return "http://embargobe3n5okxyzqphpmk3moinoap2snz5k6765mvtkk7hhi544jid.onion/#/"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "http://embargobe3n5okxyzqphpmk3moinoap2snz5k6765mvtkk7hhi544jid.onion/#/"

    def safe_find(self, page, selector, attr=None):
        try:
            element = page.query_selector(selector)
            if element:
                return element.get_attribute(attr) if attr else element.inner_text().strip()
        except Exception:
            return None

    def parse_leak_data(self, page: Page):
        try:
            page.goto(self.seed_url)
            page.wait_for_load_state('load')

            more_pages = True
            page_count = 1

            while more_pages:
                print(f"Processing page {page_count}...")


                card_elements = page.query_selector_all("div.p-4.border-1.surface-border.surface-card.border-round")
                if not card_elements:
                    print(f"No leak data cards found on page {page_count}.")
                    break

                print(f"Found {len(card_elements)} cards on page {page_count}")

                for card in card_elements:
                    try:

                        company_name_element = card.query_selector("div.text-2xl.font-bold")
                        company_name = company_name_element.inner_text() if company_name_element else None


                        description_element = card.query_selector("div.blog-preview span")
                        description = description_element.inner_text() if description_element else None


                        image_element = card.query_selector("img.blog-image")
                        image_url = image_element.get_attribute("src") if image_element else None


                        date_element = card.query_selector("div.flex.flex-wrap.justify-content-end.gap-2 span")
                        date_of_publication = date_element.inner_text() if date_element else None

                        card_data = card_extraction_model(
                            m_company_name=company_name,
                            m_title=company_name,
                            m_url=self.base_url,
                            m_network=helper_method.get_network_type(self.base_url),
                            m_base_url=self.base_url,
                            m_content=description,
                            m_important_content=description,
                            m_logo_or_images=[image_url] if image_url else [],
                            m_content_type="leaks",
                            m_email_addresses=helper_method.extract_emails(description) if description else [],
                            m_phone_numbers=helper_method.extract_phone_numbers(description) if description else [],
                            m_leak_date=date_of_publication,
                        )

                        self._card_data.append(card_data)

                    except Exception as card_ex:
                        print(f"Error processing card: {card_ex}")
                        continue


                next_page_button = page.query_selector("button.p-paginator-next:not([disabled])")

                if next_page_button:
                    print(f"Moving to page {page_count + 1}...")
                    try:

                        next_page_button.click()

                        page.wait_for_load_state('networkidle')

                        page.wait_for_selector("div.p-4.border-1.surface-border.surface-card.border-round",
                                               state="visible", timeout=10000)
                        page_count += 1
                    except Exception as nav_ex:
                        print(f"Error navigating to next page: {nav_ex}")
                        more_pages = False
                else:
                    print("No more pages to process.")
                    more_pages = False

            print(f"Successfully processed {len(self._card_data)} cards across {page_count} pages")

        except Exception as ex:
            print(f"An error occurred in parse_leak_data: {ex}")