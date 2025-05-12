import json
import os
import re
import time
from datetime import datetime
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from nltk import PorterStemmer
from playwright.sync_api import Page
from crawler.crawler_services.shared.helper_method import helper_method
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import telegram_chat_model
from social_collector.local_client.services.translation_service import translation_service


class telegram_message_helper:
    __instance = None
    __m_connection = None

    @staticmethod
    def get_instance():
        if telegram_message_helper.__instance is None:
            telegram_message_helper()
        return telegram_message_helper.__instance

    def __init__(self):
        telegram_message_helper.__instance = self
        self.stemmer = PorterStemmer()
        self.classifiers = self.load_classifier_keywords()

    @staticmethod
    def load_classifier_keywords() -> dict:
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),  '..','..', 'constants'))
            file_path = os.path.join(base_dir, 'classifier.json')

            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"[load_classifier_keywords] Failed to load classifier.json: {e}")
            return {}

    @staticmethod
    def extract_views(soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find('span', class_='post-views')
        return tag.get_text(strip=True) if tag else None

    @staticmethod
    def extract_forwarded_from(soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find('div', class_='name')
        if tag and 'bubble-name-forwarded' in tag.get('class'):
            span = tag.find('span', class_='peer-title')
            return span.get_text(strip=True) if span else None
        return None

    @staticmethod
    def extract_reply_to(soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find('div', class_='reply')
        return tag.get('data-reply-to-mid') if tag and tag.has_attr('data-reply-to-mid') else None

    @staticmethod
    def extract_file_info(soup: BeautifulSoup) -> list[dict]:
        file_infos = []

        containers = soup.select('div.document-wrapper')
        for container in containers:
            file_name = None
            file_size = None

            name_tag = container.find('middle-ellipsis-element')
            if name_tag:
                file_name = name_tag.get('title') or name_tag.get_text(strip=True)

            size_tag = container.select_one('div.document-size')
            if size_tag:
                raw = size_tag.get_text(strip=True)
                match = re.search(r'([\d.,]+)\s*(KB|MB|GB|B)', raw)
                if match:
                    num, unit = match.groups()
                    num = float(num.replace(',', ''))
                    file_size = f"{num:.2f} {unit}"
                else:
                    file_size = raw

            if file_name:
                file_infos.append({
                    "file_name": file_name,
                    "file_size": file_size
                })

        return file_infos

    @staticmethod
    def extract_content(soup: BeautifulSoup) -> Optional[str]:
        content = ""
        webpage_title = soup.find("div", class_="webpage-title")
        webpage_text = soup.find("div", class_="webpage-text")

        if webpage_title or webpage_text:
            title = webpage_title.get_text(strip=True) if webpage_title else ""
            summary = webpage_text.get_text(strip=True) if webpage_text else ""
            content = f"{title}\n{summary}".strip()

        message_div = soup.select_one("div.message.spoilers-container")
        if message_div:
            for tag in message_div.select(".time, .webpage-title, .webpage-text, .post-views, .time-inner, .webpage"):
                tag.extract()
            text = list(message_div.stripped_strings)
            if text:
                content = " ".join(text).strip() + content

        if not content:
            document = soup.find('div', class_='document-message')
            span = soup.find('span', class_='translatable-message')
            fallback = document or span
            if fallback:
                content = fallback.get_text(strip=True)

        return content

    @staticmethod
    def extract_media(soup: BeautifulSoup) -> dict:
        media_url = None
        media_caption = None

        if soup.find('img', class_='media-photo'):
            media_url = soup.find('img', class_='media-photo').get('src')
        elif soup.find('video'):
            media_url = soup.find('video').get('src')
        elif soup.find('audio'):
            media_url = soup.find('audio').get('src')

        cap = soup.find('span', class_='translatable-message')
        if cap:
            media_caption = cap.get_text(strip=True)

        return {"media_url": media_url, "media_caption": media_caption}

    @staticmethod
    def extract_message_type(soup: BeautifulSoup) -> str:
        if soup.find('div', class_='document'):
            return 'document'
        if soup.find('video'):
            return 'video'
        if soup.find('audio'):
            return 'audio'
        if soup.find('img', class_='media-photo'):
            return 'photo/web'
        return 'text'

    @staticmethod
    def extract_status(soup: BeautifulSoup) -> str:
        parent_bubble = soup.find('div', class_='bubble')
        return ' '.join(parent_bubble.get('class')) if parent_bubble else ''

    @staticmethod
    def extract_reactions(soup: BeautifulSoup) -> List[dict]:
        reactions = []
        element = soup.find('reactions-element')
        if element:
            for r in element.find_all('reaction-element'):
                sid = r.find('div', class_='reaction-sticker').get('data-doc-id')
                count = r.find('span', class_='reaction-counter').get_text(strip=True)
                reactions.append({'sticker_id': sid, 'count': count})
        return reactions

    @staticmethod
    def get_bubble_html(bubble) -> str:
        return bubble.inner_html()

    @staticmethod
    def extract_message_date(section) -> Optional[datetime.date]:
        try:
            span = section.query_selector(".bubble.service.is-date span.i18n")
            if not span:
                return None
            raw_date = span.inner_text().strip()
            current_year = datetime.now().year
            today = datetime.now().date()
            if raw_date.lower() == "today":
                return today
            if raw_date.lower() == "yesterday":
                return today.replace(day=today.day - 1)
            if re.search(r"\b\d{4}\b", raw_date):
                return datetime.strptime(raw_date, "%B %d, %Y").date()
            msg_date = datetime.strptime(f"{raw_date} {current_year}", "%B %d %Y").date()
            if msg_date > today:
                msg_date = msg_date.replace(year=current_year - 1)
            return msg_date
        except:
            return None

    @staticmethod
    def scroll_up(page: Page, scrollable):
        page.evaluate("(el) => el.scrollTop += el.offsetHeight / 3", scrollable)
        page.evaluate("(el) => el.scrollTop -= el.offsetHeight", scrollable)
        time.sleep(1)

    @staticmethod
    def get_channel_shareable_link(page) -> Optional[str]:
        try:
            rows = page.query_selector_all(".sidebar-left-section-content .row.row-clickable")
            for row in rows:
                subtitle = row.query_selector(".row-subtitle")
                title = row.query_selector(".row-title")
                if subtitle and subtitle.inner_text().strip().lower() == "link":
                    if title:
                        return title.inner_text().strip()
        except:
            return None

    @staticmethod
    def download_document_from_bubble(page, bubble):
        try:
            document_buttons = bubble.query_selector_all(".document-ico")
            if not document_buttons:
                return None

            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
            os.makedirs(base_dir, exist_ok=True)

            hashed_file_names = []

            for document_button in document_buttons:
                try:
                    with page.expect_download(timeout=15000) as download_info:
                        document_button.click()
                        try:
                            page.wait_for_selector(".quality-download-options-button-menu", timeout=1000)
                            quality_button = page.query_selector(".quality-download-options-button-menu")
                            if quality_button:
                                quality_button.click()
                                time.sleep(1)
                                viewport = page.viewport_size
                                x = viewport['width'] - 30
                                y = 30
                                page.mouse.click(x, y)
                        except:
                            pass

                    download = download_info.value
                    original_name = download.suggested_filename

                    hashed_name = helper_method.generate_data_hash(original_name)
                    download_path = os.path.join(base_dir, hashed_name)
                    download.save_as(download_path)
                    hashed_file_names.append(hashed_name)
                except:
                    continue

            return hashed_file_names if hashed_file_names else None
        except:
            return None

    @staticmethod
    def extract_message_link(page: Page, msg_id: str) -> Optional[str]:
        try:
            selector = f'div.bubble[data-mid="{msg_id}"]'
            page.wait_for_selector(selector, timeout=3000, state="visible")
            bubble_handle = page.query_selector(selector)
            if not bubble_handle:
                return None

            bubble_handle.scroll_into_view_if_needed()
            page.wait_for_timeout(200)
            box = bubble_handle.bounding_box()
            if not box:
                return None

            page.mouse.click(0, 0)  # reset context
            center_x = box["x"] + box["width"]
            center_y = box["y"] + box["height"] / 3
            page.mouse.click(center_x, center_y, button="right")
            page.wait_for_selector(".btn-menu-items", timeout=6000)

            menu_items = page.query_selector_all(".btn-menu-item")
            for item in menu_items:
                text_span = item.query_selector(".btn-menu-item-text")
                if text_span and text_span.inner_text().strip().lower() == "copy message link":
                    item.click()

                    page.evaluate("""
                        if (!document.getElementById('paste-helper')) {
                            const input = document.createElement('input');
                            input.id = 'paste-helper';
                            input.style.position = 'absolute';
                            input.style.opacity = '0';
                            input.style.pointerEvents = 'none';
                            document.body.appendChild(input);
                        }
                    """)
                    page.focus('#paste-helper')
                    page.keyboard.press('Control+V')
                    link = str(page.eval_on_selector('#paste-helper', 'el => el.value'))
                    page.evaluate("document.getElementById('paste-helper').value = ''")
                    return link

        except Exception as e:
            print(f"[extract_message_link] Failed: {e}")
            return None

    @staticmethod
    def _extract_refined_content(soup: BeautifulSoup) -> tuple[str, str]:
        parts = []

        message = soup.select_one(".message span.translatable-message")
        if message:
            text = message.get_text(strip=True)
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            if not (text.startswith("http://") or text.startswith("https://")):
                parts.append(" " + text + " ")

        preview_title = soup.select_one(".webpage-title")
        preview_desc = soup.select_one(".webpage-text")
        title_text = preview_title.get_text(strip=True) if preview_title else ""
        desc_text = preview_desc.get_text(strip=True) if preview_desc else ""
        title_text = re.sub(r'[^\x00-\x7F]+', ' ', title_text)
        title_text = re.sub(r'\s+', ' ', title_text).strip()
        desc_text = re.sub(r'[^\x00-\x7F]+', ' ', desc_text)
        desc_text = re.sub(r'\s+', ' ', desc_text).strip()
        combined_caption = " ".join(filter(None, [title_text, desc_text]))

        file_names = []
        for el in soup.select(".document-name middle-ellipsis-element"):
            name = el.get_text(strip=True)
            name = re.sub(r'[^\x00-\x7F]+', ' ', name)
            name = re.sub(r'\s+', ' ', name).strip()
            file_names.append(name)

        urls = {a["href"] for a in soup.select(".message .anchor-url[href]") if a.get("href")}

        if file_names:
            parts.append("Files: " + ", ".join(file_names))
        if urls:
            parts.extend(sorted(urls))


        final = " ".join(filter(None, parts))
        final = re.sub(r'\s+', ' ', final).strip()

        captions = combined_caption

        return final, captions

    @staticmethod
    def open_sidebar(page: Page):
        link_text = ""
        try:
            avatar = page.query_selector('.person-avatar')
            if not avatar:
                return None

            avatar.click()
            time.sleep(2)
            page.wait_for_selector('.row-clickable', timeout=5000)

            rows = page.query_selector_all('.row-clickable')
            for row in rows:
                subtitle = row.query_selector('.row-subtitle')
                if subtitle and subtitle.inner_text().strip().lower() == "link":
                    title = row.query_selector('.row-title')
                    if title:
                        link_text = title.inner_text().strip()
                        if link_text.startswith("t.me/"):
                            break

            avatar = page.query_selector('.person-avatar')
            if avatar:
                avatar.click()

            return link_text if link_text.startswith("t.me/") else None
        except:
            return None

    def get_content_types(self, content: str) -> list[str]:
        matched_types = []

        tokens = re.split(r'[^a-zA-Z0-9]+', content.lower())

        filtered_tokens = [word for word in tokens if len(word) > 2]
        stemmed_words = {self.stemmer.stem(word) for word in filtered_tokens}

        for category, keywords in self.classifiers.items():
            stemmed_keywords = {self.stemmer.stem(k) for k in keywords}
            if stemmed_words & stemmed_keywords:
                matched_types.append(category)

        return matched_types

    @staticmethod
    def extract_hashtags(content: str) -> List[str]:
        hashtags = re.findall(r'#\w+', content)
        return hashtags

    @staticmethod
    def extract_time(html: str) -> Optional[str]:
        soup = BeautifulSoup(html, 'html.parser')

        date_el = soup.select_one(".time-inner")
        if date_el and date_el.has_attr("title"):
            raw_date = date_el["title"]
            try:
                dt = datetime.strptime(raw_date, "%d %B %Y, %H:%M:%S")
                return dt.strftime("%H:%M:%S")
            except ValueError:
                return None
        return None

    def _extract_refhtml_and_content(self, links: list[str], soup: BeautifulSoup, file_info: list[dict]) -> tuple[str, str, list[str], str]:
        m_ref_html = ""
        if links and links.__len__()<3:
            m_ref_html = helper_method.extract_refhtml(links[0])
        refined_content, captions = self._extract_refined_content(soup)
        refined_content = translation_service.get_instance().translate(refined_content)
        m_ref_html = m_ref_html or ""
        file_names = [f.get("file_name") for f in file_info if f.get("file_name")]
        return m_ref_html, refined_content, file_names, captions

    @staticmethod
    def extract_mentions(content: str) -> List[str]:
        mentions = re.findall(r'(?<![\w])@[\w]{5,32}', content)
        return mentions

    def extract_messages(self, page, html: str, channel_name: str, message_id, telegram_channel_id, channel_url) -> telegram_chat_model | None:
        try:
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')

            parent_bubble = soup.find('div', class_='bubble')
            if parent_bubble and ('service' in parent_bubble.get('class', []) or 'is-sponsored' in parent_bubble.get('class', [])):
                return None

            views = self.extract_views(soup)
            forwarded_from = self.extract_forwarded_from(soup)
            reply_to = self.extract_reply_to(soup)
            file_info = self.extract_file_info(soup)
            media = self.extract_media(soup)
            status = self.extract_status(soup)
            message_link = self.extract_message_link(page, message_id)

            all_links = [
                a['href'] for a in soup.find_all('a', href=True)
                if not a['href'].startswith(('https://t.me', 'http://t.me'))
            ]
            links = list(dict.fromkeys(all_links))

            message_type = self.extract_message_type(soup)
            m_ref_html, refined_content, file_names, captions = self._extract_refhtml_and_content(links, soup, file_info)
            m_time = self.extract_time(html)
            mentions = self.extract_mentions(soup.text or "")
            hashtags = self.extract_hashtags(refined_content or "")
            content_type = self.get_content_types(f"{refined_content or ''} {m_ref_html or ''}")
            media_url = media.get("media_url") if media else None
            media_caption = media.get("media_caption") if media else None
            msg_type_list = [message_type] if message_type else None

            data = {
                "m_message_id": str(message_id),
                "m_time": m_time,
                "m_message_sharable_link": message_link,
                "m_channel_id": telegram_channel_id,
                "m_caption": captions,
                "m_content": refined_content,
                "m_users": mentions,
                "m_ref_html": m_ref_html,
                "m_views": views,
                "m_hashtags": hashtags,
                "m_file_name": file_names,
                "m_forwarded_from": forwarded_from,
                "m_weblink": links,
                "m_content_type": content_type,
                "m_channel_name": channel_name,
                "m_message_type": msg_type_list,
                "m_media_url": media_url,
                "m_media_caption": media_caption,
                "m_reply_to_message_id": reply_to,
                "m_message_status": status,
                "m_channel_url": channel_url
            }

            clean_data = {k: v for k, v in data.items() if v not in [None, [], "", {}]}
            return telegram_chat_model(**clean_data)

        except Exception:
            return None
