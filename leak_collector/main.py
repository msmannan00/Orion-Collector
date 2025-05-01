from crawler.request_manager import check_services_status
from crawler.request_parser import RequestParser
from leak_collector.scripts._ddosecrets import _ddosecrets
from leak_collector.scripts._lynxblogco7r37jt7p5wrmfxzqze7ghxw6rihzkqc455qluacwotciyd import _lynxblogco7r37jt7p5wrmfxzqze7ghxw6rihzkqc455qluacwotciyd
from leak_collector.scripts._monitor_mozilla import _monitor_mozilla
from leak_collector.scripts._weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd import _weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd
from telegram_collector.scripts._telegram_extractor import _telegram_extractor

check_services_status()

if __name__ == "__main__":
    parse_sample = _monitor_mozilla()
    parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
    print(parse_sample.card_data)
