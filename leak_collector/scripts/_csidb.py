import traceback
from abc import ABC
from datetime import datetime

from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from dateutil import parser
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _csidb(leak_extractor_interface, ABC):
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

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_csidb, cls).__new__(cls)
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "https://www.csidb.net"

    @property
    def base_url(self) -> str:
        return "https://www.csidb.net"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.NONE, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return self.base_url

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    @staticmethod
    def safe_find(page, selector, attr=None):

        try:
            element = page.locator(selector).first
            if element.count() > 0:
                return element.get_attribute(attr) if attr else element.inner_text().strip()
        except Exception:
            return None

    def parse_leak_data(self, page: Page):
        try:
            # Navigate to the main page
            page.goto(self.seed_url)
            page.wait_for_load_state('load')

            # Lists to store collected links
            incident_links = []
            organisation_links = []
            actor_links = []

            # Set limit for testing (first 10 items from each section)
            testing_limit = 10

            # Step 1: Get main navigation links
            main_nav_links = {}
            nav_elements = page.query_selector_all("a.nav-link.link-light.btn.btn-secondary")
            for nav in nav_elements:
                text = nav.inner_text().strip()
                href = nav.get_attribute("href")
                main_nav_links[text] = href

            print(f"Found main navigation links: {main_nav_links}")

            # Step 2: Process Incidents section first
            if "INCIDENTS" in main_nav_links:
                incidents_url = urljoin(self.base_url, main_nav_links["INCIDENTS"])
                print(f"Navigating to Incidents: {incidents_url}")
                page.goto(incidents_url)
                page.wait_for_load_state('load')

                # Process all pages of incidents
                has_next_page = True
                current_page = 1

                while has_next_page and len(incident_links) < testing_limit:
                    print(f"Processing incidents page {current_page}")
                    page.wait_for_selector('tbody tr')

                    # Collect incident links from current page
                    links = page.query_selector_all("tbody tr td a.link-primary")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "/csidb/incidents/" in href:
                            full_url = urljoin(self.base_url, href)
                            if full_url not in incident_links:
                                incident_links.append(full_url)
                                if len(incident_links) >= testing_limit:
                                    break

                    print(f"Collected {len(incident_links)} incident links so far")

                    # Check for next page (only if we need more links)
                    if len(incident_links) < testing_limit:
                        next_button = page.query_selector(
                            "button.btn.btn-secondary[onclick*='page=" + str(current_page + 1) + "']")
                        if next_button:
                            next_button.click()
                            page.wait_for_load_state('networkidle')
                            page.wait_for_timeout(1000)  # Wait for page to render
                            current_page += 1
                        else:
                            has_next_page = False
                    else:
                        has_next_page = False

            # Step 3: Process Organizations section
            if "ORGANISATIONS" in main_nav_links:
                orgs_url = urljoin(self.base_url, main_nav_links["ORGANISATIONS"])
                print(f"Navigating to Organizations: {orgs_url}")
                page.goto(orgs_url)
                page.wait_for_load_state('load')

                # Process all pages of organizations
                has_next_page = True
                current_page = 1

                while has_next_page and len(organisation_links) < testing_limit:
                    print(f"Processing organizations page {current_page}")
                    page.wait_for_selector('tbody tr')

                    # Collect organization links from current page
                    links = page.query_selector_all("tbody tr td a")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "/csidb/organisations/" in href:
                            full_url = urljoin(self.base_url, href)
                            if full_url not in organisation_links:
                                organisation_links.append(full_url)
                                if len(organisation_links) >= testing_limit:
                                    break

                    print(f"Collected {len(organisation_links)} organization links so far")

                    # Check for next page (only if we need more links)
                    if len(organisation_links) < testing_limit:
                        next_button = page.query_selector(
                            "button.btn.btn-secondary[onclick*='page=" + str(current_page + 1) + "']")
                        if next_button:
                            next_button.click()
                            page.wait_for_load_state('networkidle')
                            page.wait_for_timeout(1000)  # Wait for page to render
                            current_page += 1
                        else:
                            has_next_page = False
                    else:
                        has_next_page = False

            # Step 4: Process Threat Actors section
            if "THREAT ACTORS" in main_nav_links:
                actors_url = urljoin(self.base_url, main_nav_links["THREAT ACTORS"])
                print(f"Navigating to Threat Actors: {actors_url}")
                page.goto(actors_url)
                page.wait_for_load_state('load')

                # Process all pages of threat actors
                has_next_page = True
                current_page = 1

                while has_next_page and len(actor_links) < testing_limit:
                    print(f"Processing threat actors page {current_page}")
                    page.wait_for_selector('tbody tr')

                    # Collect threat actor links from current page
                    links = page.query_selector_all("tbody tr td a")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "/csidb/actors/" in href:
                            full_url = urljoin(self.base_url, href)
                            if full_url not in actor_links:
                                actor_links.append(full_url)
                                if len(actor_links) >= testing_limit:
                                    break

                    print(f"Collected {len(actor_links)} threat actor links so far")

                    # Check for next page (only if we need more links)
                    if len(actor_links) < testing_limit:
                        next_button = page.query_selector(
                            "button.btn.btn-secondary[onclick*='page=" + str(current_page + 1) + "']")
                        if next_button:
                            next_button.click()
                            page.wait_for_load_state('networkidle')
                            page.wait_for_timeout(1000)  # Wait for page to render
                            current_page += 1
                        else:
                            has_next_page = False
                    else:
                        has_next_page = False

            # Step 5: Process each incident link and extract data
            print(f"Processing {len(incident_links)} individual incident pages")
            incident_data = []

            for idx, incident_url in enumerate(incident_links):
                try:
                    print(f"Processing incident {idx + 1}/{len(incident_links)}: {incident_url}")
                    page.goto(incident_url)
                    page.wait_for_load_state('load')

                    # Extract incident date
                    date_element = page.query_selector(
                        "p.col-8.d-inline.text-start.bg-white.text-nowrap.m-0.border.ps-2")
                    incident_date = date_element.inner_text().strip() if date_element else None

                    # Extract victim name and title
                    title_element = page.query_selector("h1.col.h-100.text-center.text-white.text-wrap a.link-info")
                    title = title_element.inner_text().strip() if title_element else None

                    # Extract location
                    location_element = page.query_selector(
                        "p.col-8.d-inline.text-start.bg-white.text-nowrap.m-0.border.ps-2 span.flag-icon + span, p.col-8.d-inline.text-start.bg-white.text-nowrap.m-0.border.ps-2:nth-child(2)")
                    if not location_element:
                        location_element = page.query_selector(
                            "p.col-8.d-inline.text-start.bg-white.text-nowrap.m-0.border.ps-2 span.flag-icon")
                        if location_element:
                            # Get text next to the flag icon
                            location_text = page.evaluate('''
                                el => {
                                    const text = el.parentNode.textContent.trim();
                                    return text.replace(/\\s+/g, ' ');
                                }
                            ''', location_element)
                            location = location_text
                        else:
                            location = None
                    else:
                        location = location_element.inner_text().strip()

                    # Extract description/content
                    description_element = page.query_selector("div.container div.row div.col")
                    description = ""
                    if description_element:
                        description = description_element.inner_text().strip()
                    else:
                        # Try alternative selectors
                        description_element = page.query_selector("div.p-2, p.p-2")
                        if description_element:
                            description = description_element.inner_text().strip()

                    # Extract website links
                    websites = []
                    website_rows = page.query_selector_all("td.align-middle.col-2 a, td.align-middle a")
                    for website in website_rows:
                        website_url = website.get_attribute("href")
                        if website_url and website_url.startswith("http"):
                            websites.append(website_url)

                    # Format date if available
                    m_leak_date = None
                    if incident_date:
                        try:
                            m_leak_date = parser.parse(incident_date).date()
                        except:
                            print(f"Could not parse date: {incident_date}")

                    # Prepare important content (first 500 words if description is long)
                    important_content = ""
                    if description:
                        words = description.split()
                        if len(words) > 500:
                            important_content = " ".join(words[:500])
                        else:
                            important_content = description

                    # Create leak model
                    card_data = leak_model(
                        m_title=title,
                        m_screenshot="",
                        m_url=incident_url,
                        m_network=helper_method.get_network_type(self.base_url),
                        m_base_url=self.base_url,
                        m_content=description + " " + self.base_url + " " + incident_url if description else self.base_url + " " + incident_url,
                        m_important_content=important_content,
                        m_content_type=["hacking"],
                        m_leak_date=m_leak_date,
                        m_weblink=websites
                    )

                    entity_data = entity_model(
                        m_email_addresses=helper_method.extract_emails(description) if description else [],
                        m_phone_numbers=helper_method.extract_phone_numbers(description) if description else [],
                        m_company_name=title,
                        m_country_name=location
                    )

                    self.append_leak_data(card_data, entity_data)
                    incident_data.append((title, incident_date, location))

                except Exception as incident_error:
                    print(f"Error processing incident {incident_url}: {incident_error}")
                    traceback.print_exc()

            # Step 6: Process each organization link and extract data
            print(f"Processing {len(organisation_links)} individual organization pages")
            org_data = []

            for idx, org_url in enumerate(organisation_links):
                try:
                    print(f"Processing organization {idx + 1}/{len(organisation_links)}: {org_url}")
                    page.goto(org_url)
                    page.wait_for_load_state('load')

                    # Extract organization name
                    org_name_element = page.query_selector("h1.h-100.text-center.text-white.text-wrap")
                    org_name = org_name_element.inner_text().strip() if org_name_element else None

                    # Extract website link
                    weblink_element = page.query_selector("td.text-center a[target='_blank']")
                    weblink = weblink_element.get_attribute("href") if weblink_element else None

                    # Extract location
                    location_element = page.query_selector("td.text-center span.flag-icon")
                    if location_element:
                        # Get text next to the flag icon
                        location_text = page.evaluate('''
                            el => {
                                const text = el.parentNode.textContent.trim();
                                return text.replace(/\\s+/g, ' ');
                            }
                        ''', location_element)
                        location = location_text
                    else:
                        location = None

                    # Extract description
                    description_element = page.query_selector("div.p-2.m-2, td.text-wrap.d-none.d-md-inline-block")
                    description = description_element.inner_text().strip() if description_element else None

                    # Extract incident date if available
                    date_element = page.query_selector("td.text-center a")
                    incident_date = None
                    if date_element and date_element.inner_text().strip():
                        date_text = date_element.inner_text().strip()
                        if any(month in date_text for month in
                               ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                            incident_date = date_text

                    # Format date if available
                    m_leak_date = None
                    if incident_date:
                        try:
                            m_leak_date = parser.parse(incident_date).date()
                        except:
                            print(f"Could not parse date: {incident_date}")

                    # Prepare important content (first 500 words if description is long)
                    important_content = ""
                    if description:
                        words = description.split()
                        if len(words) > 500:
                            important_content = " ".join(words[:500])
                        else:
                            important_content = description

                    # Create leak model
                    card_data = leak_model(
                        m_title=org_name,
                        m_screenshot="",
                        m_url=org_url,
                        m_network=helper_method.get_network_type(self.base_url),
                        m_base_url=self.base_url,
                        m_content=description + " " + self.base_url + " " + org_url if description else self.base_url + " " + org_url,
                        m_important_content=important_content,
                        m_content_type=["leaks"],
                        m_leak_date=m_leak_date,
                        m_weblink=[weblink] if weblink else []
                    )

                    entity_data = entity_model(
                        m_email_addresses=helper_method.extract_emails(description) if description else [],
                        m_phone_numbers=helper_method.extract_phone_numbers(description) if description else [],
                        m_company_name=org_name,
                        m_country_name=location
                    )

                    self.append_leak_data(card_data, entity_data)
                    org_data.append((org_name, weblink, location))

                except Exception as org_error:
                    print(f"Error processing organization {org_url}: {org_error}")
                    traceback.print_exc()

            # Step 7: Process each threat actor link and extract data
            print(f"Processing {len(actor_links)} individual threat actor pages")
            actor_data = []

            for idx, actor_url in enumerate(actor_links):
                try:
                    print(f"Processing threat actor {idx + 1}/{len(actor_links)}: {actor_url}")
                    page.goto(actor_url)
                    page.wait_for_load_state('load')

                    # Extract actor name
                    actor_name_element = page.query_selector("h1.h-100.text-center.text-white.text-wrap")
                    actor_name = ""
                    if actor_name_element:
                        full_text = actor_name_element.inner_text().strip()
                        # Remove "Cyber Threat Actor: " prefix if present
                        actor_name = full_text.replace("Cyber Threat Actor: ", "")

                    # Extract location
                    location_element = page.query_selector(
                        "td.text-center.align-middle div.d-flex span.flag-icon + div")
                    location = location_element.inner_text().strip() if location_element else None

                    # If location not found with the above selector, try another approach
                    if not location:
                        location_element = page.query_selector("td.text-center span.flag-icon")
                        if location_element:
                            # Get text next to the flag icon
                            location_text = page.evaluate('''
                                el => {
                                    const text = el.parentNode.textContent.trim();
                                    return text.replace(/\\s+/g, ' ');
                                }
                            ''', location_element)
                            location = location_text

                    # Extract description
                    description_element = page.query_selector("div.p-2.m-2")
                    description = ""
                    if description_element:
                        description = description_element.inner_text().strip()
                    else:
                        # Try alternative selector
                        description_element = page.query_selector("td.text-wrap.d-none.d-md-inline-block")
                        if description_element:
                            description = description_element.inner_text().strip()

                    # Extract target organization links
                    websites = []
                    target_org_links = page.query_selector_all("a[href^='/csidb/organisations/']")
                    for org_link in target_org_links:
                        org_href = org_link.get_attribute("href")
                        if org_href:
                            full_url = urljoin(self.base_url, org_href)
                            websites.append(full_url)

                    # Extract dates
                    dates = []
                    date_elements = page.query_selector_all(
                        "td.text-center a[href^='/csidb/incidents/'], td.text-center.align-middle.col-1.text-nowrap")
                    for date_elem in date_elements:
                        date_text = date_elem.inner_text().strip()
                        if date_text and any(month in date_text for month in
                                             ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
                                              "Nov", "Dec"]):
                            dates.append(date_text)

                    # Extract external website links
                    weblinks = []
                    weblink_elements = page.query_selector_all(
                        "td.align-middle.col-2 a[target='_blank'], td.align-middle a[target='_blank']")
                    for weblink in weblink_elements:
                        weblink_url = weblink.get_attribute("href")
                        if weblink_url and weblink_url.startswith("http"):
                            weblinks.append(weblink_url)

                    # Format first date if available
                    m_leak_date = None
                    if dates:
                        try:
                            m_leak_date = parser.parse(dates[0]).date()
                        except:
                            print(f"Could not parse date: {dates[0]}")

                    # Prepare important content (first 500 words if description is long)
                    important_content = ""
                    if description:
                        words = description.split()
                        if len(words) > 500:
                            important_content = " ".join(words[:500])
                        else:
                            important_content = description

                    # Create leak model
                    card_data = leak_model(
                        m_title=actor_name,
                        m_screenshot="",
                        m_url=actor_url,
                        m_network=helper_method.get_network_type(self.base_url),
                        m_base_url=self.base_url,
                        m_content=description + " " + self.base_url + " " + actor_url if description else self.base_url + " " + actor_url,
                        m_important_content=important_content,
                        m_content_type=["leaks"],
                        m_leak_date=m_leak_date,
                        m_weblink=websites + weblinks
                    )

                    entity_data = entity_model(
                        m_email_addresses=helper_method.extract_emails(description) if description else [],
                        m_phone_numbers=helper_method.extract_phone_numbers(description) if description else [],
                        m_company_name=actor_name,
                        m_country_name=location
                    )

                    self.append_leak_data(card_data, entity_data)
                    actor_data.append((actor_name, location, dates[0] if dates else None))

                except Exception as actor_error:
                    print(f"Error processing threat actor {actor_url}: {actor_error}")
                    traceback.print_exc()

            print(
                f"Completed processing {len(incident_data)} incidents, {len(org_data)} organizations, and {len(actor_data)} threat actors")

            # Add timestamp and user info for logging
            current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            current_user = "Ibrahim-sayys"  # Or retrieve from system if available
            print(f"Data collection completed at {current_time} by {current_user}")

            return True

        except Exception as ex:
            print(f"An error occurred in parse_leak_data: {ex}")
            traceback.print_exc()
            return False