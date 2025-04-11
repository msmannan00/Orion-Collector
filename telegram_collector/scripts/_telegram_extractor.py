from abc import ABC
from typing import List
import re
from bs4 import BeautifulSoup
import time
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import telegram_chat_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
import json


class _telegram_extractor(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self, callback=None):
        self.callback = callback
        self._card_data = []
        self._entity_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def init_callback(self, callback=None):
        self.callback = callback

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "https://web.telegram.org/k/"

    @property
    def base_url(self) -> str:
        return "https://web.telegram.org/"

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT, m_resoource_block=False)

    @property
    def card_data(self) -> List[telegram_chat_model]:
        return self._card_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "https://web.telegram.org/"

    def append_leak_data(self, leak: telegram_chat_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            self.callback()

    @staticmethod
    def wait_for_main_columns(page):
        while True:
            try:
                main_columns_locator = page.locator("#main-columns")
                main_columns_locator.wait_for(state="visible")
                print("Main columns are loaded.")
                break
            except Exception as e:
                print(f"Waiting for main columns: {e}")
            time.sleep(2)

    @staticmethod
    def scroll_to_top(page):
        try:
            scrollable_div = page.query_selector(".scrollable-y")
            page.evaluate("(element) => element.scrollTop = 0", scrollable_div)
        except Exception as e:
            print(f"Scroll error: {e}")

    @staticmethod
    def click_chat(chat):
        try:
            chat.click()
            time.sleep(2)
        except Exception as e:
            print(f"Click error: {e}")

    def extract_from_html(self, html: str, channel_name: str = None):

        soup = BeautifulSoup(html, 'html.parser')
        try:
            document_container = soup.find('div', class_='document-container')
            if not document_container or not document_container.get('data-mid'):
                print("[Warning] Missing document container or message_id. Skipping...")
                return None
            message_id = document_container.get('data-mid')
            peer_id = document_container.get('data-peer-id')

            timestamp_tag = soup.find('div', class_='time-inner')
            timestamp = timestamp_tag['title'] if timestamp_tag else None

            views = soup.find('span', class_='post-views')
            file_name_tag = soup.find('middle-ellipsis-element')
            file_name = file_name_tag.text.strip() if file_name_tag else None
            file_size_tag = soup.find('div', class_='document-size')
            file_size = None
            if file_size_tag:
                # Clean up file size by extracting the first number + unit (e.g., "412 KB")
                match = re.search(r'\d+\s*(?:KB|MB|GB)', file_size_tag.get_text())
                file_size = match.group(0) if match else file_size_tag.get_text(strip=True)

            forwarded_from = soup.find('span', class_='peer-title')

            sender_name = soup.find('div', class_='name')
            sender_username = soup.find('span', class_='usernames')
            chat_title = soup.find('div', class_='bubble-title')
            text_content_tag = soup.find('div', class_='text-content') or soup.find('div',
                                                                                    class_='translatable-message')
            text = text_content_tag.text.strip() if text_content_tag else soup.get_text(strip=True)

            message_type = 'audio' if soup.find('audio-element') else 'video' if soup.find('video') else 'text'
            media_url = None
            media_caption = soup.find('div', class_='translatable-message')
            reply_to = soup.find('div', class_='reply')
            edited = soup.find('i', class_='time-edited')
            status = soup.get('class')

            file_path = f"downloads/{file_name}" if file_name else None

            model = telegram_chat_model(
                message_id=message_id,
                content=text,
                timestamp=timestamp,
                views=views.text.strip() if views else None,
                file_name=file_name,
                file_size=file_size,
                forwarded_from=forwarded_from.text.strip() if forwarded_from else None,
                peer_id=peer_id,
                sender_name=sender_name.text.strip() if sender_name else None,
                sender_username=sender_username.text.strip() if sender_username else None,
                chat_title=chat_title.text.strip() if chat_title else None,
                channel_name=channel_name,
                message_type=message_type,
                media_url=media_url,
                media_caption=media_caption.text.strip() if media_caption else None,
                reply_to_message_id=reply_to['data-mid'] if reply_to and 'data-mid' in reply_to.attrs else None,
                edited_timestamp=edited.text.strip() if edited else None,
                message_status=' '.join(status) if status else None,
                file_path=file_path
            )

            print(json.dumps(model.dict(), ensure_ascii=False, indent=2))
            return model

        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return None

    def parse_leak_data(self, page: Page = None):
        self.wait_for_main_columns(page)
        last_active_chat_id = None

        print("Waiting for user to manually click chats...")

        while True:
            try:
                chat_elements = page.query_selector_all("ul a.chatlist-chat")

                for chat in chat_elements:
                    chat_classes = chat.get_attribute("class")

                    if "active" in chat_classes:
                        chat_id = chat.get_attribute("href") or chat.get_attribute("data-peer-id")

                        if chat_id != last_active_chat_id:
                            # Print active chat name
                            channel = chat.query_selector("span.peer-title")
                            channel_name = channel.inner_text().strip()
                            print("New active chat detected. Scraping messages...")

                            self.scroll_to_top(page)
                            time.sleep(3)

                            message_selector = "div.bubble.channel-post.with-beside-button.hide-name.photo.is-in.can-have-tail"
                            messages = page.query_selector_all(message_selector)
                            print(f"\n--- Extracting {len(messages)} messages ---")

                            for idx, msg in enumerate(messages, start=1):
                                try:
                                    html = msg.inner_html()
                                    parsed = self.extract_from_html(html, channel_name)

                                    if parsed:
                                        print(f"\n[Message {idx} JSON]")
                                        print(json.dumps(parsed.dict(), ensure_ascii=False, indent=2))

                                        self.append_leak_data(parsed, entity_model())
                                except Exception as e:
                                    print(f"Error extracting message {idx}: {e}")

                            group_selector = "div.bubbles-group"
                            groups = page.query_selector_all(group_selector)
                            print(f"\n--- Extracting {len(groups)} bubble groups ---")

                            for idx, group in enumerate(groups, start=1):
                                try:
                                    group_html = group.inner_html()
                                    soup = BeautifulSoup(group_html, 'html.parser')

                                    # Loop over individual bubbles/messages inside the group
                                    bubbles = soup.select("div.bubble")
                                    print(f"[Bubble Group {idx}] Found {len(bubbles)} messages.")

                                    for msg_idx, bubble in enumerate(bubbles, start=1):
                                        try:
                                            bubble_html = str(bubble)
                                            parsed = self.extract_from_html(bubble_html, channel_name)
                                            if parsed:
                                                print(f"\n[Group {idx} - Message {msg_idx} JSON]")
                                                print(json.dumps(parsed.dict(), ensure_ascii=False, indent=2))
                                                self.append_leak_data(parsed, entity_model())
                                            else:
                                                print(f"[Group {idx} - Message {msg_idx}]: Failed to parse.")
                                        except Exception as e:
                                            print(f"[Group {idx} - Message {msg_idx}] Error: {e}")

                                except Exception as e:
                                    print(f"Error processing bubble group {idx}: {e}")

                            last_active_chat_id = chat_id

            except Exception as e:
                print(f"Main loop error: {e}")

            time.sleep(2)
