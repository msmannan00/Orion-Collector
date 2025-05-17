from abc import ABC
from datetime import datetime
from typing import List
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid(leak_extractor_interface, ABC):
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
            cls._instance = super(_z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid.onion/blog"

    @property
    def base_url(self) -> str:
        return "http://z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid.onion"

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
        return "http://z3wqggtxft7id3ibr7srivv5gjof5fwg76slewnzwwakjuf3nlhukdid.onion/blog"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    def parse_leak_data(self, page: Page):
        try:
            page.wait_for_selector(".publications-list")

            while True:
                cards = page.query_selector_all(".publications-list__publication")
                if not cards:
                    break

                for card_index, card in enumerate(cards, start=1):
                    try:
                        title, weblink, address, datasize, description, date, dumplink = (None,) * 7

                        title_el = card.query_selector("h3.list-publication__name")
                        title = title_el.text_content().strip() if title_el else None

                        for _ in range(3):
                            try:
                                open_button = card.query_selector("button.publication-footer_readmore")
                                if open_button:
                                    open_button.click()
                                    page.wait_for_selector(".publication-content")
                                    break
                            except Exception as e:
                                print(f"Retrying click on 'Open' button for card {card_index} due to error: {e}")

                        weblink_el = page.query_selector(".content-addictional__row a.addictional-row__link")
                        weblink = weblink_el.get_attribute("href") if weblink_el else None

                        address_el = page.query_selector(
                            ".content-addictional__row:nth-child(2) .addictional-row__text")
                        address = address_el.text_content().strip() if address_el else None

                        datasize_el = page.query_selector(
                            ".content-addictional__row:nth-child(3) .addictional-row__text")
                        datasize = datasize_el.text_content().strip() if datasize_el else None

                        description_el = page.query_selector(".content-description__description")
                        description = description_el.text_content().strip() if description_el else None

                        date_el = page.query_selector(".content-footer__date span:nth-child(2)")
                        if date_el:
                            try:
                                date = datetime.strptime(date_el.text_content().strip(), "%d %B %Y").date()
                            except ValueError:
                                date = None

                        dumplink_el = page.query_selector(".content-statuses__publicated a.publicated-files__link")
                        if dumplink_el:
                            with page.expect_popup() as popup_info:
                                dumplink_el.click()
                            new_page = popup_info.value
                            new_page.wait_for_load_state("load")
                            new_page.wait_for_timeout(5000)
                            iframe_el = new_page.query_selector("iframe.visor-content")
                            dumplink = iframe_el.get_attribute("src") if iframe_el else None
                            new_page.close()

                        close_button = page.query_selector(".publication-header__close")
                        if close_button:
                            close_button.click()
                            page.wait_for_selector(".publications-list")

                        card_data = leak_model(
                            m_title=title,
                            m_url=page.url,
                            m_base_url=self.base_url,
                            m_screenshot=helper_method.get_screenshot_base64(page, title, self.base_url),
                            m_content=description,
                            m_network=helper_method.get_network_type(self.base_url),
                            m_important_content=description,
                            m_weblink=[weblink] if weblink else [],
                            m_dumplink=[dumplink] if dumplink else [],
                            m_content_type=["leaks"],
                            m_data_size=datasize,
                            m_leak_date=date,
                        )
                        entity_data = entity_model(
                            m_email_addresses=helper_method.extract_emails(description) if description else [],
                            m_phone_numbers=helper_method.extract_phone_numbers(description) if description else [],
                            m_location_info=[address] if address else [],
                            m_company_name=title,
                        )
                        self.append_leak_data(card_data, entity_data)

                    except Exception as e:
                        print(f"Error processing card {card_index}: {e}")

                next_button = page.query_selector(".navigation-button__next:not([disabled])")
                if next_button:
                    next_button.click()
                    page.wait_for_selector(".publications-list")
                else:
                    break

        except Exception as e:
            print(f"An error occurred while parsing leak data: {e}")