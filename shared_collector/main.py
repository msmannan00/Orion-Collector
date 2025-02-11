from crawler.request_manager import check_services_status, parse_leak_data
from shared_collector.scripts._flock4cvoeqm4c62gyohvmncx6ck2e7ugvyqgyxqtrumklhd5ptwzpqd import \
    _flock4cvoeqm4c62gyohvmncx6ck2e7ugvyqgyxqtrumklhd5ptwzpqd

check_services_status()

if __name__ == "__main__":
    parse_sample = _flock4cvoeqm4c62gyohvmncx6ck2e7ugvyqgyxqtrumklhd5ptwzpqd()
    parsed_data, raw_parse_mapping = parse_leak_data(blocked_media=True, proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample)
    print(parsed_data)
