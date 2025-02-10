# Local Imports
import re
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
  def extract_emails(text: str) -> list:

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails

  @staticmethod
  def extract_phone_numbers(text: str) -> list:

    phone_pattern = r'\+?[0-9]{1,4}?[ -.]?\(?[0-9]{1,4}?\)?[ -.]?[0-9]{1,4}[ -.]?[0-9]{1,9}'
    phone_numbers = re.findall(phone_pattern, text)
    return phone_numbers

  @staticmethod
  def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=' ')
    return helper_method.clean_text(text)
