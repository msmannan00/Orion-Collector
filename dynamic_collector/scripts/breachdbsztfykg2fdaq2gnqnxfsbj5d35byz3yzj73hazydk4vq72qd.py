import re
from abc import ABC
from typing import Dict
from playwright.async_api import BrowserContext

from dynamic_collector.lib.interface.collector_interface import collector_interface
from dynamic_collector.lib.model.collector_data_model import collector_data_model
from dynamic_collector.lib.model.collector_extraction_model import collector_extraction_model
from shared_collector.rules.rule_model import RuleModel, FetchProxy, FetchConfig


class sample(collector_interface, ABC):
    _instance = None

    def __init__(self):
        self._initialized = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(sample, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def base_url(self) -> str:
        return "http://breachdbsztfykg2fdaq2gnqnxfsbj5d35byz3yzj73hazydk4vq72qd.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config = FetchConfig.SELENIUM)

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    async def parse_leak_data(self, query: Dict[str, str], context: BrowserContext):
        p_data_url = query.get("url", "")
        email = query.get("email", "")
        username = query.get("username", "")

        collector_model = collector_data_model(base_url=p_data_url, content_type=["leak"])

        try:
            page = await context.new_page()
            await page.goto(p_data_url)

            page_content = await page.content()
            if "This site can’t be reached" in page_content or "ERR_" in page_content:
                return collector_model

            try:
                await page.locator("#SearchType").wait_for(timeout=10000)
                cards = []

                for search_type, query_value in [("Username", username), ("Email", email)]:
                    if not query_value:
                        continue

                    try:
                        await page.locator("#SearchType").select_option(value=search_type)
                        search_box = page.locator("#TxtSearch")
                        await search_box.fill(query_value)
                        search_button = page.locator("#BtnSearch")
                        await search_button.click()

                        result_panel_locator = page.locator(".ResultPanel")
                        await result_panel_locator.wait_for(timeout=10000)

                        spans = await result_panel_locator.locator("span").all()
                        public_records = [
                            (await span.text_content()).split("-->", 1)[0].strip()
                            for span in spans if "-->" in (await span.text_content())
                        ]

                        if public_records:
                            cards.append(collector_extraction_model(
                                m_title=f"Records for {query_value[:10]}",
                                description=f"Total records were found for {search_type}.",
                                websites=[],
                                m_public_records=public_records,
                                m_email_addresses=[email] if search_type == "Email" else [],
                                m_name=username if search_type == "Username" else ""
                            ))
                    except Exception:
                        continue

                collector_model.cards_data = cards

            except Exception:
                return collector_model

        finally:
            pass

        return collector_model