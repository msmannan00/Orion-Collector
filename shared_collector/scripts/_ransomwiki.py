from abc import ABC
from typing import List

from bs4 import BeautifulSoup
from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _ransomwiki(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):
        """
        Initialize the _shared_sample class instance.
        Sets up attributes for storing card data, parsing content, and interacting with Redis.
        """
        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):
        """
        Create a singleton instance of the _shared_sample class.
        Ensures only one instance of the class is created during runtime.
        """
        if cls._instance is None:
            cls._instance = super(_ransomwiki, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        """
        Returns the seed URL for the data extraction process.
        This is the starting point for parsing the required content.
        """
        return "https://ransom.wiki/"

    @property
    def base_url(self) -> str:
        """
        Returns the base URL for relative URL resolution.
        Used to create absolute URLs during parsing.
        """
        return "https://ransom.wiki/"

    @property
    def rule_config(self) -> RuleModel:
        """
        Returns the configuration rules for data fetching.
        Specifies the use of TOR as the proxy and Selenium as the fetching mechanism.
        """
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:
        """
        Returns the list of extracted card data models.
        Stores all parsed information from the leak extraction process.
        """
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        """
        Interacts with the Redis database to perform a specified command.

        Args:
            command (REDIS_COMMANDS): The Redis command to execute (e.g., GET, SET).
            key (CUSTOM_SCRIPT_REDIS_KEYS): The key for the operation.
            default_value: The default value to use if the key is not found.

        Returns:
            None
        """
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        """
        Returns the URL of the contact page for the shared sample data source.
        Useful for referencing or navigating to the contact page.
        """
        return "https://www.linkedin.com/in/soufianetahiri/"

    def parse_leak_data(self, page: Page):

        html_content = page.content()

        soup = BeautifulSoup(html_content, 'html.parser')

        victim_elements = soup.find_all('li', class_='list-group-item')

        victim_names = []
        for victim in victim_elements:
            text = victim.text.strip()
            if text.startswith("Victime:"):
                clean_name = text.replace("Victime:", "").strip().rstrip("...")
                victim_names.append(clean_name)

        for victim_name in victim_names:
            search_box = page.locator('input#search_box')
            search_box.fill(victim_name)
            search_box.press('Enter')

            page.wait_for_selector('table.table', timeout=5000)
            table_row = page.locator('table.table tbody tr td')
            raw_data = table_row.inner_text()

            data = {}
            lines = raw_data.split('\n')

            victim = None
            group = None
            description = None
            website = None
            published = None
            post_url = None
            country = None

            for line in lines:
                if "Victime" in line:
                    victim = line.split(":")[-1].strip()
                    data["Victime"] = victim
                if "Group" in line:
                    group = line.split(":")[-1].strip()
                    data["Group"] = group
                if "Discovered" in line:
                    discovered = line.split(":")[-1].strip()
                    data["Discovered"] = discovered
                if "Description" in line:
                    description = line.split(":")[-1].strip()
                    data["Description"] = description
                if "Website" in line:
                    website = line.split(":")[-1].strip()
                    data["Website"] = website
                if "Published" in line:
                    published = line.split(":")[-1].strip()
                    data["Published"] = published
                if "Post_url" in line:
                    post_url = line.split(":")[-1].strip()
                    data["Post_url"] = post_url
                if "Country" in line:
                    country = line.split(":")[-1].strip()
                    data["Country"] = country

            self._card_data = card_extraction_model(
                m_title=victim,
                m_url=post_url,
                m_base_url=self.base_url,
                m_content=description,
                m_company_name=group,
                m_network=helper_method.get_network_type(self.base_url).value,
                m_important_content=description,
                m_weblink=[website],
                m_leak_date=published,
                m_addresses=[country],
                m_dumplink=[],
                m_email_addresses=helper_method.extract_emails(soup.text),
                m_phone_numbers=helper_method.extract_phone_numbers(soup.text),
                m_extra_tags=[],
                m_content_type="Leak",
            )

