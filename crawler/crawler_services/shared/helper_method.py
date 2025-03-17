# Local Imports
import re
import datetime
from urllib.parse import urlparse

import unicodedata
from bs4 import BeautifulSoup

class helper_method:

  @staticmethod
  def clean_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\u2066\u2067\u2068\u2069\u202A-\u202E]', '', text)
    text = ''.join(char for char in text if char.isprintable())
    return text.strip()

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
  def extract_and_convert_date(text: str) -> datetime.date:
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
    return datetime.date.today()

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

  @staticmethod
  def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=' ')
    return helper_method.clean_text(text)
