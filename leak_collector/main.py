from crawler.request_manager import check_services_status
from crawler.request_parser import RequestParser
from leak_collector._example import _example

check_services_status()

if __name__ == "__main__":
    parse_sample = _example()
    parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
    print(parse_sample.card_data)
