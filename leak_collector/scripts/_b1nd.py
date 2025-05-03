import traceback
from abc import ABC
from datetime import datetime

from typing import List

from playwright.sync_api import Page
from urllib.parse import urljoin
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _b1nd(leak_extractor_interface, ABC):
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
      cls._instance = super(_b1nd, cls).__new__(cls)
    return cls._instance

  @property
  def seed_url(self) -> str:
    return "http://b1nd.net"

  @property
  def base_url(self) -> str:
    return "http://b1nd.net"

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
    return self.seed_url

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

      current_time = "2025-05-03 19:57:47"
      current_user = "Ibrahim-sayys"
      print(f"Data collection started at {current_time} by {current_user}")


      thread_links = []


      print(f"Navigating to main page: {self.seed_url}")
      page.goto(self.seed_url)
      page.wait_for_load_state("load")


      db_link_element = page.query_selector('h3.node-title a[href*="/forums/databases"]')
      if not db_link_element:
        print("Databases category link not found. Trying alternative selector...")
        db_link_element = page.query_selector('a[href="/forums/databases.5/"]')

      if not db_link_element:
        raise Exception("Could not find databases category link")

      db_link = db_link_element.get_attribute("href")
      full_db_link = urljoin(self.base_url, db_link)
      print(f"Found databases category link: {full_db_link}")


      page.goto(full_db_link)
      page.wait_for_load_state("load")


      current_page = 1
      max_pages = 13

      while current_page <= max_pages:
        print(f"Processing databases category page {current_page}/{max_pages}")


        page.wait_for_selector('div.structItem-title a')


        thread_elements = page.query_selector_all('div.structItem-title a')


        for element in thread_elements:
          href = element.get_attribute("href")
          if href:
            full_url = urljoin(self.base_url, href)
            if full_url not in thread_links:
              thread_links.append(full_url)
              print(f"Added thread: {full_url}")

        print(f"Collected {len(thread_links)} thread links so far")


        current_page += 1
        if current_page <= max_pages:
          next_page_url = f"{full_db_link}page-{current_page}"
          print(f"Moving to next page: {next_page_url}")
          page.goto(next_page_url)
          page.wait_for_load_state("load")


      print(f"Processing {len(thread_links)} threads...")

      for idx, thread_url in enumerate(thread_links):
        try:
          print(f"Processing thread {idx + 1}/{len(thread_links)}: {thread_url}")


          page.goto(thread_url)
          page.wait_for_load_state("load")



          date_element = page.query_selector('time.u-dt')
          date_text = ""
          if date_element:
            date_text = date_element.get_attribute("data-date-string")
            print(f"Found date: {date_text}")


          title_element = page.query_selector('h1.p-title-value')
          title = ""
          if title_element:
            title = title_element.inner_text().strip()
            print(f"Found title: {title}")


          content_element = page.query_selector('article.message-body div.bbWrapper')
          content = ""
          if content_element:

            content_html = content_element.inner_html()

            content = content_element.inner_text().strip()

            content = content.replace('\n', ' ')
            print(f"Found content (truncated): {content[:100]}...")


          image_logos = []
          img_elements = page.query_selector_all('article.message-body div.bbWrapper img')
          for img in img_elements:
            src = img.get_attribute("src")
            if src:
              full_img_url = urljoin(self.base_url, src)
              image_logos.append(full_img_url)
              print(f"Found image: {full_img_url}")


          websites = []

          domain_pattern = r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?|[a-zA-Z0-9.-]+\.onion(?:/\S*)?'


          if content:
            import re
            matches = re.findall(domain_pattern, content)
            for match in matches:
              if match not in websites:
                websites.append(match)
                print(f"Found website: {match}")


          link_elements = page.query_selector_all('article.message-body div.bbWrapper a')
          for link in link_elements:
            href = link.get_attribute("href")
            if href and (href.startswith("http") or ".com" in href or ".net" in href or ".onion" in href):
              if href not in websites:
                websites.append(href)
                print(f"Found website link: {href}")


          password = ""
          password_js = """
                () => {
                    // Find spans containing "Passwords:" text
                    const spans = Array.from(document.querySelectorAll('span'));
                    const passwordSpan = spans.find(span => span.textContent.includes('Passwords:'));

                    if (passwordSpan) {
                        const text = passwordSpan.textContent;
                        const parts = text.split('Passwords:');
                        if (parts.length > 1) {
                            return parts[1].trim();
                        }
                    }

                    // Check in signature area
                    const signature = document.querySelector('aside.message-signature div.bbWrapper');
                    if (signature && signature.textContent.includes('Passwords:')) {
                        const text = signature.textContent;
                        const parts = text.split('Passwords:');
                        if (parts.length > 1) {
                            return parts[1].trim();
                        }
                    }

                    // Check in any element with text containing "Passwords:"
                    const allElements = document.querySelectorAll('*');
                    for (const el of allElements) {
                        if (el.textContent && el.textContent.includes('Passwords:') && 
                            el.children.length === 0) { // Only get from leaf nodes
                            const text = el.textContent;
                            const parts = text.split('Passwords:');
                            if (parts.length > 1) {
                                return parts[1].trim();
                            }
                        }
                    }

                    return '';
                }
                """

          try:
            password = page.evaluate(password_js)
            if password:
              print(f"Found password: {password}")
          except Exception as pw_error:
            print(f"Error extracting password: {pw_error}")


          m_leak_date = None
          if date_text:
            try:
              m_leak_date = datetime.strptime(date_text, '%b %d, %Y').date()
              print(f"Parsed date: {m_leak_date}")
            except Exception as date_error:
              print(f"Error parsing date: {date_error}")




          card_data = leak_model(
            # m_screenshot=helper_method.get_screenshot_base64(page, title),
            m_title=title,
            m_screenshot="",
            m_weblink=websites,
            m_url=thread_url,
            m_base_url=self.base_url,
            m_content=content + " " + self.base_url + " " + thread_url if content else self.base_url + " " + thread_url,
            m_network=helper_method.get_network_type(self.base_url),
            m_important_content=content[:500],
            m_content_type=["leaks"],
            m_leak_date=m_leak_date,
            m_logo_or_images=image_logos,
            m_password=password
          )

          entity_data = entity_model(
            m_email_addresses=helper_method.extract_emails(content) if content else [],
            m_phone_numbers=helper_method.extract_phone_numbers(content) if content else [],
            m_company_name=title
          )

          self.append_leak_data(card_data, entity_data)
          print(f"Successfully processed thread #{idx + 1}")

        except Exception as thread_error:
          print(f"Error processing thread {thread_url}: {thread_error}")
          traceback.print_exc()
          continue

      print(f"Completed processing {len(thread_links)} threads from databases category")
      print(f"Data collection completed at {current_time} by {current_user}")

    except Exception as e:
      print(f"An error occurred: {e}")
      traceback.print_exc()
    finally:
      self.invoke_db(REDIS_COMMANDS.S_SET_BOOL, CUSTOM_SCRIPT_REDIS_KEYS.URL_PARSED, True)