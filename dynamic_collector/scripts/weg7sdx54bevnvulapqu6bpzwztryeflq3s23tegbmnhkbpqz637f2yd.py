import re
from abc import ABC
from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from dynamic_collector.lib.model.collector_extraction_model import collector_extraction_model
from dynamic_collector.lib.interface.collector_interface import collector_interface
from dynamic_collector.lib.model.collector_data_model import collector_data_model


class sample(collector_interface, ABC):
    _instance = None

    def __init__(self):
        self.soup = None
        self._initialized = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(sample, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def base_url(self) -> str:
        return "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion"

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def parse_leak_data(self, p_data_url: str, proxies: Dict[str, str]) -> collector_data_model:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        tor_proxy = "socks5://127.0.0.1:9150"
        options.add_argument(f"--proxy-server={tor_proxy}")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        collector_model = collector_data_model(
            base_url=p_data_url,
            content_type=["leak"],
        )

        try:
            driver.get(p_data_url)

            if "This site can’t be reached" in driver.page_source or "ERR_" in driver.page_source:
                raise RuntimeError("Failed to load the page, likely due to network or proxy issues.")

            cards = driver.find_elements(By.CLASS_NAME, "card")

            for card in cards:
                title_element = card.find_element(By.CLASS_NAME, "title")
                url_element = card.find_element(By.CLASS_NAME, "url")
                text_element = card.find_element(By.CLASS_NAME, "text")

                m_title = self.clean_text(title_element.text)
                description = self.clean_text(text_element.text)
                url = url_element.get_attribute("href").strip() if url_element.get_attribute("href") else ""

                collector_model.cards_data.append(collector_extraction_model(m_title=m_title, description=description, websites=[url]))

            return collector_model
        except Exception as e:
            raise RuntimeError(f"An error occurred while processing: {e}")
        finally:
            driver.quit()