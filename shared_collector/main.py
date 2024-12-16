import requests
from shared_collector.sample import sample

def get_html_via_tor(url):
    proxies = {
        'http': 'socks5h://localhost:9150',
        'https': 'socks5h://localhost:9150',
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.ConnectionError:
        print("Error: TOR is not running. Please start TOR and try again.")
        exit(1)

    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

if __name__ == "__main__":
    url = "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion"
    sub_urls = [url]

    while sub_urls:
        current_url = sub_urls.pop(0)
        html = get_html_via_tor(current_url)

        if html:
            parse_sample = sample()
            data_model, sub_links = parse_sample.parse_leak_data(html, current_url)
            if sub_links:
                sub_urls.extend(sub_links)

            print(data_model)
        else:
            print(f"Failed to fetch HTML for {current_url}")