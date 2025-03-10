from crawler.request_manager import check_services_status, parse_leak_data
from shared_collector.scripts._ddosecrets import _ddosecrets

check_services_status()

if __name__ == "__main__":
    parse_sample = _ddosecrets()
    parsed_data, raw_parse_mapping = parse_leak_data(blocked_media=True, proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample)
    print(parsed_data)
