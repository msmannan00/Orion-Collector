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
        max_pages = 3  # Set the maximum number of pages to fetch

        for i in range(1, max_pages + 1):
            try:
                # Construct the URL for each page
                url = f"{self.seed_url}/{i}"
                print(f"Fetching page: {url}")

                page.goto(url, timeout=60000)  # Navigate to the page with a longer timeout

                # Wait for content to load before proceeding
                page.wait_for_selector(".py-6")  # Wait for the section to load

                # Parse the page content with BeautifulSoup
                self.soup = BeautifulSoup(page.content(), "html.parser")

                # Find all the sections (each section is wrapped in a <div> with the specific class)
                sections = self.soup.find_all("div",
                                              class_="py-6 relative after:absolute after:bottom-0 after:w-full after:border-b after:border-slate-50/[0.06]")

                for section in sections:
                    # Extract the date and time
                    date_time = section.find("time").text.strip() if section.find("time") else ""

                    # Extract the title
                    title = section.find("h2").text.strip() if section.find("h2") else ""
                    print(title)
                    # Extract the description (all <p> tags inside the parsed-post-text div)
                    description = ""
                    description_div = section.find("div", class_="parsed-post-text")
                    if description_div:
                        description = "\n".join(p.text.strip() for p in description_div.find_all("p"))
                    print(description)
                    # Extract the file link and size (inside <ul> with class parsed-post-text)
                    file_link = ""
                    file_size = ""
                    link_tag = section.find("a")
                    size_tag = section.find("span", class_="inline-block ml-1.5 text-slate-600 font-bold")
                    if link_tag:
                        file_link = self.base_url + link_tag.get("href", "")
                    if size_tag:
                        file_size = size_tag.text.strip()

                    # Populate a new leak_model for this title
                    leak_data = leak_model(
                        m_title=title,
                        m_url=page.url,
                        m_base_url=self.base_url,
                        m_screenshot="",  # Add screenshot logic if needed
                        m_content=f"{description}\nDate: {date_time}",
                        m_network=helper_method.get_network_type(self.base_url),
                        m_important_content=description,
                        m_weblink=[],
                        m_dumplink=[file_link],
                        m_content_type=["leaks"],
                    )

                    # Populate a new entity_model for this title
                    entity_data = entity_model(
                        m_email_addresses=helper_method.extract_emails(description),
                        m_phone_numbers=helper_method.extract_phone_numbers(description),
                    )

                    # Append the data for this title
                    self.append_leak_data(leak_data, entity_data)

            except Exception as e:
                print(f"Error fetching or parsing page {url}: {e}")



