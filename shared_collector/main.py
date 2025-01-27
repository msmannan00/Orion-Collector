from crawler.request_manager import check_services_status, parse_leak_data
from shared_collector._example import _example
from shared_collector.scripts._weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd import _weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd

check_services_status()

if __name__ == "__main__":
    parse_sample = _weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd()
    parsed_data, raw_parse_mapping = parse_leak_data({"server": "socks5://127.0.0.1:9150"}, parse_sample)
    print(parsed_data)
