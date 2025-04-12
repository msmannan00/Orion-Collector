from crawler.request_manager import check_services_status
from crawler.request_parser import RequestParser
from telegram_collector.scripts._telegram_extractor import _telegram_extractor

check_services_status()

if __name__ == "__main__":
    parse_sample = _telegram_extractor()
    parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
