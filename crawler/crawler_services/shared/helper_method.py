# Local Imports
import hashlib
import json
import re
import datetime
import socket
import base64
import unicodedata
import requests

from typing import Optional, OrderedDict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from crawler.crawler_instance.genbot_service.shared.shared_data_controller import shared_data_controller
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, REDIS_KEYS


class helper_method:
  _refhtml_cache = OrderedDict()

  @staticmethod
  def is_sentence(text):
    words = text.split()
    count = 0

    for word in words:
        if len(word) > 3 and re.fullmatch(r'[\w]+', word):
            count += 1
            if count >= 4:
                return True
        else:
            count = 0
    return False

  @staticmethod
  def clean_summary(text: str, max_length: int = 300) -> str:
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[\s\t\n\r]+', ' ', text)
    text = text.strip()
    return text[:max_length]

  @staticmethod
  def generate_data_hash(data):
    if isinstance(data, dict):
      data_copy = {key: value for key, value in data.items() if key not in {'m_update_date', 'm_base_url', 'm_url'}}
      data_string = json.dumps(data_copy, sort_keys=True)
    elif isinstance(data, str):
      data_string = data
    else:
      raise ValueError("Input must be a dictionary or a string")

    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

  @staticmethod
  def extract_refhtml(url: str) -> str | None:
    try:
      if "t.me" in url:
        return None

      if not url.startswith("http"):
        url = f"https://{url.lstrip('http://').lstrip('https://')}"

      parsed = urlparse(url)
      if not parsed.scheme or not parsed.netloc:
        return None

      if url in helper_method._refhtml_cache:
        helper_method._refhtml_cache.move_to_end(url)
        return helper_method._refhtml_cache[url]

      headers = {
        "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/120.0.0.0 Safari/537.36"
        )
      }

      socket.setdefaulttimeout(15)
      response = requests.get(url, headers=headers, timeout=(5, 15))

      if response.status_code != 200 or not response.text:
        return None

      soup = BeautifulSoup(response.text, "html.parser")
      parts = [(soup.find("meta", {"name": "description"}) or {}).get("content", "").strip()]
      parts += [e.get_text(strip=True) for e in soup.select("h1,h2,h3,h4,h5,h6,p")]

      result, total = [], 0
      for part in filter(None, parts):
        total += len(part) + (3 if result else 0)
        result.append(part)
        if total > 1500:
          break

      text = " - ".join(result)[:2000]
      clean_text = re.sub(r"\s{2,}", " ", text).strip(" -.,:;") or None

      if clean_text:
        helper_method._refhtml_cache[url] = clean_text
        if len(helper_method._refhtml_cache) > 20:
          helper_method._refhtml_cache.popitem(last=False)

      return clean_text

    except (requests.RequestException, socket.timeout):
      pass
    except Exception:
      pass
    return None

  @staticmethod
  def get_host_name(p_url):
    m_parsed_uri = urlparse(p_url)
    m_netloc = m_parsed_uri.netloc

    if m_netloc.startswith('www.'):
      m_netloc = m_netloc[4:]

    netloc_parts = m_netloc.split('.')

    if len(netloc_parts) > 2:
      m_host_name = netloc_parts[-2]
    elif len(netloc_parts) == 2:
      m_host_name = netloc_parts[0]
    else:
      m_host_name = m_netloc

    return m_host_name

  @staticmethod
  def clean_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\u2066\u2067\u2068\u2069\u202A-\u202E]', '', text)
    text = ''.join(char for char in text if char.isprintable())
    return text.strip()

  @staticmethod
  def get_screenshot_base64(page, search_string, base_url):
    try:
      storage_key = REDIS_KEYS.LEAK_PARSED + helper_method.get_host_name(base_url)
      url_previously_parsed = redis_controller().invoke_trigger(REDIS_COMMANDS.S_GET_BOOL,[storage_key, False, None])
      if url_previously_parsed:
        return ""

      search_string = re.sub(r"[^\w\s-]", "", search_string).strip()
      page.wait_for_load_state("networkidle", timeout=1000)
      element = page.locator(f":text('{search_string}')").first
      element.wait_for(timeout=1000)
      element.evaluate("el => el.scrollIntoView({ block: 'center', behavior: 'instant' })")
      screenshot_bytes = element.screenshot(timeout=1000)
      return base64.b64encode(screenshot_bytes).decode("utf-8")
    except Exception as ex:
      print(f"Error in get_screenshot_base64: {ex}")
    return ""

  @staticmethod
  def get_network_type(url: str):
    try:
      if not url.startswith("http"):
        url = "http://" + url
      parsed_url = urlparse(url)
      if not parsed_url.scheme or not parsed_url.netloc:
        return "invalid"
      if re.search(r"\.onion$", parsed_url.netloc, re.IGNORECASE):
        return "onion"
      if re.search(r"\.i2p$", parsed_url.netloc, re.IGNORECASE):
        return "i2p"
      return "clearnet"
    except Exception:
      return "invalid"

  @staticmethod
  def extract_and_convert_date(text: str) -> Optional[datetime.date]:
    for pattern, fmt in [
      (r'(\d{4}-\d{2}-\d{2})', "%Y-%m-%d"),
      (r'(\d{4}/\d{2}/\d{2})', "%Y/%m/%d"),
      (r'(\d{2}-\d{2}-\d{4})', "%d-%m-%Y"),
      (r'(\d{2}/\d{2}/\d{4})', "%m/%d/%Y"),
      (r'(\d{1,2} \w+ \d{4})', "%d %B %Y")
    ]:
      if match := re.search(pattern, text):
        try:
          return datetime.datetime.strptime(match.group(0), fmt).date()
        except ValueError:
          continue
    return None

  @staticmethod
  def extract_entities(text: str, model: entity_model) -> entity_model:
    emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text))
    if emails:
      model.m_email_addresses.extend(list(emails))

    result = shared_data_controller.get_instance().trigger_nlp_classifier(text)

    for entry in result:
      for key, value in entry.items():
        if key in {"m_domains", "m_file_path"} or not value:
          continue
        existing = getattr(model, key, [])
        if not isinstance(existing, list):
          existing = []
        if isinstance(value, str):
          if value not in existing:
            existing.append(value)
        elif isinstance(value, list):
          existing.extend([v for v in value if v not in existing])
        setattr(model, key, existing)

    return model

  @staticmethod
  def extract_emails(text: str) -> list:

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails

  @staticmethod
  def extract_phone_numbers(text: str) -> list:
    phone_pattern = r'\(?\b\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
    phone_numbers = re.findall(phone_pattern, text)

    filtered_phone_numbers = []
    for number in phone_numbers:
      digits_only = re.sub(r'[^0-9]', '', number)

      if 7 <= len(digits_only) <= 15:
        if '(' in text[text.find(number):text.find(number) + len(number)]:
          filtered_phone_numbers.append(number)
        else:
          filtered_phone_numbers.append(number)

    return filtered_phone_numbers

  # noinspection PyArgumentList
  @staticmethod
  def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=' ')
    return helper_method.clean_text(text)
