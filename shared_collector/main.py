from crawler.request_manager import check_services_status, parse_leak_data
from shared_collector.scripts._mblogci3rudehaagbryjznltdp33ojwzkq6hn2pckvjq33rycmzczpid import \
    _mblogci3rudehaagbryjznltdp33ojwzkq6hn2pckvjq33rycmzczpid

check_services_status()

if __name__ == "__main__":
    parse_sample = _mblogci3rudehaagbryjznltdp33ojwzkq6hn2pckvjq33rycmzczpid()
    parsed_data, raw_parse_mapping = parse_leak_data(blocked_media=True, proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample)
    print(parsed_data)
