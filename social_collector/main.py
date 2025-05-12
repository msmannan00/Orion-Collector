from social_collector.local_client.helper.telegram.telegram_helper import check_services_status, run_env_update_script
from social_collector.local_client.parsers.request_parser import RequestParser
from social_collector.scripts.telegram._telegram_extractor import _telegram_extractor

run_env_update_script()
check_services_status()

if __name__ == "__main__":
  parse_sample = _telegram_extractor()
  parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
