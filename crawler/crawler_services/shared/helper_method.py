# Local Imports
import re
from urllib.parse import urlparse
from crawler.constants.enums import network_type


class helper_method:

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
