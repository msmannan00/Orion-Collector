from crawler.request_manager import check_services_status
from crawler.request_parser import RequestParser
from leak_collector.scripts._k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd import _k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd

check_services_status()

if __name__ == "__main__":
    parse_sample = _k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd()
    parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
    print(parse_sample.card_data)
