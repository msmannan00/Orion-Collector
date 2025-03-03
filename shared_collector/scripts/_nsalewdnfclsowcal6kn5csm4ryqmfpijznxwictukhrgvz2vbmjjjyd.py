from abc import ABC
from typing import List

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method

import re

class _nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self):
        self._card_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd.onion"

    @property
    def base_url(self) -> str:
        return "http://nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.SELENIUM)

    @property
    def card_data(self) -> List[card_extraction_model]:
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "https://t.me/fresh_leaks_today"

    def parse_leak_data(self, page: Page):
        self._card_data = []  # Clear existing data before extracting new content

        try:
            page.wait_for_selector("div.elem_ibody", timeout=30000)  # Ensure cards are loaded
            cards = page.query_selector_all("div.elem_ibody")

            if not cards:
                return  # Stop execution if no cards are available

            for index, card in enumerate(cards):
                try:
                    # Re-select elements to prevent stale references
                    cards = page.query_selector_all("div.elem_ibody")
                    card = cards[index]

                    # Extract title and company name
                    title_element = card.query_selector("div.ibody_title")
                    company_name = title_element.inner_text().strip() if title_element else "Unknown"

                    # Extract website links from <a> tags
                    website_elements = card.query_selector_all("div.ibody_body a")
                    websites = [w.get_attribute("href").strip() for w in website_elements if w.get_attribute("href")]

                    # Extract additional website links from <p> tags (plain text links)
                    p_elements = card.query_selector_all("div.ibody_body p")
                    for p in p_elements:
                        p_text = p.inner_text().strip()
                        links_in_p = re.findall(r"https?://[^\s,<>]+", p_text)
                        websites.extend(links_in_p)

                    # Remove duplicates in websites
                    websites = list(set(websites))

                    # Extract content without links
                    content_element = card.query_selector("div.ibody_body")
                    if content_element:
                        content_text = content_element.inner_text().strip()
                        for website in websites:
                            content_text = re.sub(re.escape(website), '', content_text, flags=re.IGNORECASE).strip()
                        content_text = "\n".join([line for line in content_text.split("\n") if line.strip()])
                    else:
                        content_text = "No content available"

                    imp_content = content_text[:500]  # Limiting important content to 500 characters

                    # Extract leak date
                    date_element = card.query_selector("div.ibody_ft_left p:nth-child(1)")
                    leak_date = date_element.inner_text().replace("Date:", "").strip() if date_element else "Unknown"

                    # Extract status
                    status_element = card.query_selector("div.ibody_ft_left p:nth-child(2)")
                    status = status_element.inner_text().replace("Status:", "").strip() if status_element else "Unknown"

                    # Extract views
                    views_element = card.query_selector("div.counter_include")
                    views = views_element.inner_text().strip() if views_element else "Unknown"

                    # Append status and views to content & imp_content
                    content_text += f"\nStatus: {status}, Views: {views}"
                    imp_content += f"\nStatus: {status}, Views: {views}"

                    # Extract image link
                    image_element = card.query_selector("div.ibody_logo picture img")
                    image_url = image_element.get_attribute("src") if image_element else None

                    # If no image is found, skip this card
                    if not image_url:
                        print("Skipping card: No Image found")
                        continue

                    # Navigate using the image URL
                    with page.expect_navigation(wait_until="domcontentloaded"):
                        image_element.click()

                    page.wait_for_load_state("domcontentloaded")

                    # Extract slick images from the next page
                    slick_images = []
                    slick_elements = page.query_selector_all("div.slick-track img")
                    for img in slick_elements:
                        img_src = img.get_attribute("src")
                        if img_src:
                            slick_images.append(img_src.strip())

                    # Go back to main page
                    with page.expect_navigation(wait_until="domcontentloaded"):
                        page.go_back()
                    page.wait_for_selector("div.elem_ibody", timeout=10000)

                    # Store extracted data
                    self._card_data.append(
                        card_extraction_model(
                            m_title=company_name,
                            m_url=page.url,
                            m_websites=websites,
                            m_base_url=self.base_url,
                            m_company_name=company_name,
                            m_content=content_text,
                            m_network=helper_method.get_network_type(self.base_url),
                            m_important_content=imp_content,
                            m_email_addresses=helper_method.extract_emails(content_text),
                            m_phone_numbers=helper_method.extract_phone_numbers(content_text),
                            m_content_type="leaks",
                            m_leak_date=leak_date,
                            m_logo_or_images=slick_images,  # Extracted images from the slider
                        )
                    )

                except Exception as e:
                    print(f"Error processing card: {e}")

        except Exception as e:
            print(f"Error in parsing: {e}")









