from social_collector.local_client.constants.enums import TelegramConfig
from social_collector.local_client.helper.telegram.telegram_helper import check_services_status
from social_collector.local_client.parsers.request_parser import RequestParser
from social_collector.scripts.telegram._telegram_extractor import _telegram_extractor

check_services_status()

TelegramConfig.ALLOWED_TELEGRAM_CHANNEL_ID = [
    "t.me/AntiPlumbers",
    "t.me/DataLeaks24",
    "t.me/solntsepekZ",
    "t.me/APTANALYSIS",
    "t.me/altenens",
    "t.me/proxy_bar"
]

TelegramConfig.ALLOWED_TELEGRAM_CHANNEL_NAMES = [
    "#𝕎𝕖𝔸𝕣𝕖ℝ𝕠𝕠𝕥𝕊𝕖𝕔",
    "CASPER CLOUD",
    "Stealer Store"
]

if __name__ == "__main__":
  parse_sample = _telegram_extractor()
  parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
