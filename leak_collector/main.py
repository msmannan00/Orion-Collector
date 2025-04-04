from crawler.request_manager import check_services_status, parse_leak_data
from leak_collector._example import _example
from leak_collector.scripts._public_tableau import _public_tableau
from leak_collector.scripts._ransomlook import _ransomlook

check_services_status()

if __name__ == "__main__":
    parse_sample = _public_tableau()
    parsed_data, raw_parse_mapping = parse_leak_data(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample)
    print(parsed_data)
