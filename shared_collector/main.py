from crawler.request_manager import check_services_status, parse_leak_data
from shared_collector.scripts._leaksndi6i6m2ji6ozulqe4imlrqn6wrgjlhxe25vremvr3aymm4aaid import _leaksndi6i6m2ji6ozulqe4imlrqn6wrgjlhxe25vremvr3aymm4aaid

check_services_status()

if __name__ == "__main__":
    parse_sample = _leaksndi6i6m2ji6ozulqe4imlrqn6wrgjlhxe25vremvr3aymm4aaid()
    parsed_data, raw_parse_mapping = parse_leak_data(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample)
    print(parsed_data)
