from crawler.request_manager import check_services_status
from crawler.request_parser import RequestParser
from leak_collector.scripts._3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd import _3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd
from leak_collector.scripts._ks5424y3wpr5zlug5c7i6svvxweinhbdcqcfnptkfcutrncfazzgz5id import _ks5424y3wpr5zlug5c7i6svvxweinhbdcqcfnptkfcutrncfazzgz5id
from leak_collector.scripts._rnsmwareartse3m4hjsumjf222pnka6gad26cqxqmbjvevhbnym5p6ad_script import \
    _rnsmwareartse3m4hjsumjf222pnka6gad26cqxqmbjvevhbnym5p6ad_script

check_services_status()

if __name__ == "__main__":
    parse_sample = _rnsmwareartse3m4hjsumjf222pnka6gad26cqxqmbjvevhbnym5p6ad_script()
    parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
    print(parse_sample.card_data)
