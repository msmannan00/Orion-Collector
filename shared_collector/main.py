from crawler.request_manager import check_services_status, parse_leak_data
from shared_collector.scripts._in_the_wild import _in_the_wild

check_services_status()

if __name__ == "__main__":
    parse_sample = _in_the_wild()
    parsed_data, raw_parse_mapping = parse_leak_data(blocked_media=True, proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample)
    print(parsed_data)
