# Local Imports
import re
from urllib.parse import urlparse
from crawler.constants.enums import network_type

class helper_method:

  @staticmethod
  def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

  @staticmethod
  def get_network_type(url:str):
    try:
      if not url.startswith("http"):
        url = "http://" + url
      parsed_url = urlparse(url)
      if not parsed_url.scheme or not parsed_url.netloc:
        return network_type.INVALID
      if re.search(r"\.onion$", parsed_url.netloc, re.IGNORECASE):
        return network_type.ONION
      if re.search(r"\.i2p$", parsed_url.netloc, re.IGNORECASE):
        return network_type.I2P
      return network_type.CLEARNET
    except Exception:
      return network_type.INVALID

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

