from crawler.request_manager import check_services_status, parse_leak_data
from shared_collector.scripts._zone_xsec import _zone_xsec

check_services_status()

if __name__ == "__main__":
    parse_sample = _zone_xsec()
    parsed_data, raw_parse_mapping = parse_leak_data({"server": "socks5://127.0.0.1:9150"}, parse_sample)
    print(parsed_data)
