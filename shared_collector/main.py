import json

import requests

from shared_collector.rules.rule_model import RuleModel, FetchProxy
from shared_collector.sample import sample
from playwright.sync_api import sync_playwright

def get_html_via_tor(url, rule:RuleModel):
    try:
        with sync_playwright() as p:
            if rule.m_fetch_proxy is FetchProxy.NONE:
                browser = p.chromium.launch(headless=True)
            else:
                browser = p.chromium.launch(proxy={"server": "socks5://127.0.0.1:9150"}, headless=True)

            context = browser.new_context()
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            page_source = page.content()
            browser.close()
            return page_source

    except requests.ConnectionError:
        print("Error: TOR is not running. Please start TOR and try again.")
        exit(1)

    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

if __name__ == "__main__":
    url = "http://3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd.onion/static/data.js"
    sub_urls = [(url, 0)]
    data_models = []
    visited_urls = set()
    max_depth = 2
    max_sub_depth = 100

    while sub_urls:
        current_url, current_depth = sub_urls.pop(0)
        parse_sample = sample()

        if current_url in visited_urls or current_depth > parse_sample.rule_config.m_depth:
            continue

        visited_urls.add(current_url)
        html = get_html_via_tor(current_url, parse_sample.rule_config)

        if html:
            data_model, sub_links = parse_sample.parse_leak_data(html, current_url)
            sub_links = set(list(sub_links)[0:100])

            if sub_links:
                sub_urls = [(link, current_depth + 1) for link in sub_links if link not in visited_urls] + sub_urls

            if data_model is not None:
                data_models.append({"m_leak_data_model": json.dumps(data_model.model_dump())})
                print(data_models)
        else:
            print(f"Failed to fetch HTML for {current_url}")
