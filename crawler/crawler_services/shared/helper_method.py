# Local Imports
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class helper_method:

  @staticmethod
  def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

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
          return datetime.strptime(match.group(0), fmt).date()
        except ValueError:
          continue
    return None

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
