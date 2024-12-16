from dynamic_collector.sample import sample
import requests

def get_proxy(use_proxy=True):
    if use_proxy:
        proxies = {
            'http': 'socks5h://localhost:9150',
            'https': 'socks5h://localhost:9150',
        }
        try:
            response = requests.get("http://check.torproject.org", proxies=proxies, timeout=10)
            response.raise_for_status()
            return proxies
        except requests.ConnectionError:
            raise RuntimeError("Error: TOR is not running. Please start TOR and try again.")
        except requests.RequestException as e:
            raise RuntimeError(f"Error testing TOR connection: {e}")
    return {}

def main():
    url = "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion/"
    use_proxy = True

    try:
        proxies = get_proxy(use_proxy=use_proxy)
        sample_instance = sample()
        result = sample_instance.parse_leak_data(p_data_url=url, proxies=proxies)
        print(result)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
