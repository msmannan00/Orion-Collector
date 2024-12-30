import json
from crawler.proxy import get_html_via_tor
from shared_collector._shared_sample import _shared_sample

url = "https://example.com"
max_depth = 2
max_sub_depth = 100

if __name__ == "__main__":
    sub_urls = [(url, 0)]
    data_models = []
    visited_urls = set()

    while sub_urls:
        current_url, current_depth = sub_urls.pop(0)
        parse_sample = _shared_sample()

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
