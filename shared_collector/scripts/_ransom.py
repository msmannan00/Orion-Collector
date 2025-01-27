from abc import ABC
from typing import Tuple, Set
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from crawler.crawler_instance.local_interface_model.collector_interface import collector_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_instance.local_shared_model import leak_data_model


# Initialize Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the target website
driver.get("https://ransom.wiki/")
time.sleep(5)  # Wait for page to load

class _ransom(collector_interface, ABC):
    _instance = None

    def _init_(self):
        self.soup = None

    def _new_(cls):
        if cls._instance is None:
            cls.instance = super(_ransom, cls).new_(cls)
        return cls._instance

    @property
    def base_url(self) -> str:
        return "https://ransom.wiki/"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    def parse_leak_data(self, html_content: str, p_data_url: str) -> Tuple[leak_data_model, Set[str]]:
        self.soup = BeautifulSoup(html_content, 'html.parser')
        data_model = leak_data_model(
            cards_data=[],  # Initialize an empty list for storing cards data
            contact_link=self.contact_page(),
            base_url=self.base_url,
            content_type=["leak"]
        )

        # Locate the section containing recently added victims
        victim_elements = driver.find_elements(By.CSS_SELECTOR, "div.col-sm ul.list-group li.list-group-item")
        recently_added_victims = []

        # Extract victim names
        for element in victim_elements:
            victim_name = element.text.strip()
            if victim_name.startswith("Victime:"):
                # Remove "Victime:" and trailing dots
                victim_name = victim_name.replace("Victime:", "").strip().rstrip(".")
                recently_added_victims.append(victim_name)

        print("Recently Added Victims:")
        print(recently_added_victims)

        # Search each victim and collect their data
        for victim in recently_added_victims:
            print(f"\nSearching data for victim: {victim}")

            # Clear the search box, enter the victim's name, and submit the search
            search_box = driver.find_element(By.ID, "search_box")
            search_box.clear()
            search_box.send_keys(victim)
            search_box.send_keys(Keys.RETURN)
            time.sleep(10)  # Wait for search results to load

            # Locate the results table and collect its data
            table = driver.find_element(By.CLASS_NAME, "table")
            data = table.text
            print(f"Data for {victim}:")
            print(data)

            # Parse the data into specific fields
            lines = data.splitlines()
            victim_data = {}

            for line in lines:
                if line.startswith("Victime:"):
                    victim_data['Victime'] = line.replace("Victime:", "").strip()
                if line.startswith("Group:"):
                    victim_data['Group'] = line.replace("Group:", "").strip()
                if line.startswith("Discovered:"):
                    victim_data['Discovered'] = line.replace("Discovered:", "").strip()
                if line.startswith("Description:"):
                    victim_data['Description'] = line.replace("Description:", "").strip()
                if line.startswith("Website:"):
                    victim_data['Website'] = line.replace("Website:", "").strip()
                if line.startswith("Published:"):
                    victim_data['Published'] = line.replace("Published:", "").strip()
                if line.startswith("Post_url:"):
                    victim_data['Post_url'] = line.replace("Post_url:", "").strip()
                if line.startswith("Country:"):
                    victim_data['Country'] = line.replace("Country:", "").strip()

            # Store each piece of extracted data in separate variables
            title = victim_data.get('Victime', 'No Title')
            group = victim_data.get('Group', 'No Group')
            discovered = victim_data.get('Discovered', 'No Discovery Date')
            content = victim_data.get('Description', 'No Description')
            website = victim_data.get('Website', 'No Website')
            published = victim_data.get('Published', 'No Published Date')
            post_url = victim_data.get('Post_url', 'No Post URL')
            country = victim_data.get('Country', 'No Country')

            # Create card model with the collected data
            card_model = card_extraction_model(
                m_title=title,
                m_network=group,
                m_leak_date=discovered,
                m_content=content,
                m_websites=website,
                m_url=post_url,
                m_addresses=country,
            )

            # Append the card model to the cards_data list in the data model
            data_model.cards_data.append(card_model)

            # Wait 10 seconds before searching the next victim
            time.sleep(10)

        # Return the final data model with the extracted data
        return data_model, set()

    def contact_page(self) -> str:
        return "https://github.com/soufianetahiri"