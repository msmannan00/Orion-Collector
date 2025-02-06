from crawler.request_manager import check_services_status, parse_leak_data
from shared_collector.scripts._nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad import \
    _nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad

check_services_status()

if __name__ == "__main__":
    parse_sample = _nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad()
    parsed_data, raw_parse_mapping = parse_leak_data({"server": "socks5://127.0.0.1:9150"}, parse_sample)
    print(parsed_data)
