import os
import time
from abc import ABC
from datetime import datetime, timedelta
from typing import List
import re
from bs4 import BeautifulSoup
from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.telegram_chat_model import telegram_chat_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


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

  def invoke_db(self, command: int, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value) -> None:
    return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

  def contact_page(self) -> str:
    return "https://web.telegram.org/"

  def append_leak_data(self, leak: telegram_chat_model, entity: entity_model):
    self._card_data.append(leak)
    self._entity_data.append(entity)
    if self.callback:
      self.callback()

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

        except Exception:
          continue

      if hashed_file_names:
        return hashed_file_names
      else:
        return None

    except Exception:
      return None

  @staticmethod
  def get_channel_shareable_link(page) -> str | None:
    try:
      rows = page.query_selector_all(".sidebar-left-section-content .row.row-clickable")
      for row in rows:
        subtitle = row.query_selector(".row-subtitle")
        title = row.query_selector(".row-title")
        if subtitle and subtitle.inner_text().strip().lower() == "link":
          if title:
            link_text = title.inner_text().strip()
            if link_text:
              return link_text  # e.g., 't.me/AntiPlumbers'
    except Exception as e:
      print("Error extracting public link:", e)

    return None

  @staticmethod
  def build_model_from_message(page, html: str, channel_name: str, msg_id, telegram_channel_id) -> telegram_chat_model | None:
    message_link = None
    try:
      message_type: str = "message"
      soup = BeautifulSoup(html, 'html.parser')

      bubble_div = soup.find('div', class_='bubble-content-wrapper')
      avatar_div = soup.find('div', class_='bubble-name-forwarded-avatar')
      peer_id = avatar_div.get('data-peer-id') if avatar_div else None
      if not bubble_div:
        return None

      parent_bubble = soup.find('div', class_='bubble')
      if parent_bubble and ('service' in parent_bubble.get('class') or 'is-sponsored' in parent_bubble.get('class')):
        return None

      time_tag = soup.select_one('div.time-inner')
      timestamp = time_tag.get('title').split('\n')[0] if time_tag and time_tag.has_attr('title') else None

      unique_hash = helper_method.generate_data_hash(msg_id)
      message_id = parent_bubble.get('data-mid') if parent_bubble and parent_bubble.has_attr('data-mid') else unique_hash

      selector = f'div.bubble[data-mid="{msg_id}"]'

      try:
        page.wait_for_selector(selector, timeout=3000, state="visible")
        bubble_handle = page.query_selector(selector)
        if bubble_handle:
          bubble_handle.scroll_into_view_if_needed()
          page.wait_for_timeout(200)

          box = bubble_handle.bounding_box()
          if box:
            viewport = page.viewport_size
            if viewport:
              page.mouse.click(0, 0)

            center_x = box["x"] + box["width"] / 4
            center_y = box["y"] + box["height"] / 4
            page.mouse.click(center_x, center_y, button="right")
            page.wait_for_selector(".btn-menu-items", timeout=21000)

            menu_items = page.query_selector_all(".btn-menu-item")
            for item in menu_items:
              text_span = item.query_selector(".btn-menu-item-text")
              if text_span:
                text = text_span.inner_text().strip()
                if text.lower() == "copy message link":
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
                  message_link = str(page.eval_on_selector('#paste-helper', 'el => el.value'))
                  page.evaluate("document.getElementById('paste-helper').value = ''")
                  break
      except Exception:
        pass

      edited_timestamp = None
      if time_tag and time_tag.has_attr('title') and '\n' in time_tag.get('title'):
        parts = time_tag.get('title').split('\n')
        for part in parts:
          if part.startswith('Edited:') or part.startswith('Original:'):
            edited_timestamp = part.split(': ', 1)[1].strip()

      views_tag = soup.find('span', class_='post-views')
      views = views_tag.get_text(strip=True) if views_tag else None

      content_text = ""
      webpage_title = soup.find("div", class_="webpage-title")
      webpage_text = soup.find("div", class_="webpage-text")

      if webpage_title or webpage_text:
        title = webpage_title.get_text(strip=True) if webpage_title else ""
        summary = webpage_text.get_text(strip=True) if webpage_text else ""
        content_text = f"{title}\n{summary}".strip()

      message_div = soup.select_one("div.message.spoilers-container")

      if message_div:
        for unwanted in message_div.select(".time, .webpage-title, .webpage-text, .post-views, .time-inner, .webpage"):
            unwanted.extract()
        message_raw = message_div.stripped_strings
        if message_raw:
          content_text = " ".join(message_raw).strip() + content_text

      if not content_text:
        document_message = soup.find('div', class_='document-message')
        translatable_message = soup.find('span', class_='translatable-message')
        text_tag = document_message if document_message else translatable_message
        content_text = text_tag.get_text(strip=True) if text_tag else None

      file_name_tag = soup.find('middle-ellipsis-element')
      file_name = file_name_tag.get_text(strip=True) if file_name_tag else None

      file_size_tag = soup.select_one('div.document-size')
      file_size = None

      if file_size_tag:
        raw = file_size_tag.get_text(strip=True)
        match = re.search(r'([\d.,]+)\s*(KB|MB|GB)', raw)
        if match:
          num, unit = match.groups()
          num = float(num.replace(',', ''))
          file_size = f"{num:.2f} {unit}"
        else:
          file_size = raw

      forwarded_from = None
      forwarded_tag = soup.find('div', class_='name')
      if forwarded_tag and 'bubble-name-forwarded' in forwarded_tag.get('class'):
        peer_title = forwarded_tag.find('span', class_='peer-title')
        forwarded_from = peer_title.get_text(strip=True) if peer_title else None

      reply_tag = soup.find('div', class_='reply')
      reply_to_message_id = reply_tag.get('data-reply-to-mid') if reply_tag and reply_tag.has_attr('data-reply-to-mid') else None

      media_url = None
      media_caption = None
      if soup.find('img', class_='media-photo'):
        media_url = soup.find('img', class_='media-photo').get('src')
      elif soup.find('video'):
        media_url = soup.find('video').get('src')
      elif soup.find('audio'):
        media_url = soup.find('audio').get('src')

      caption_tag = soup.find('span', class_='translatable-message')
      if caption_tag:
        media_caption = caption_tag.get_text(strip=True)

      if message_type == "message":
        if soup.find('div', class_='document ext-torrent'):
          message_type = 'document'
        elif soup.find('video'):
          message_type = 'video'
        elif soup.find('audio'):
          message_type = 'audio'
        elif soup.find('img', class_='media-photo'):
          message_type = 'photo'
        elif soup.find('a', class_='webpage'):
          message_type = 'webpage'
        else:
          message_type = 'text'

      status_classes = parent_bubble.get('class') if parent_bubble else []
      message_status = ' '.join(status_classes)

      reactions = []
      reactions_element = soup.find('reactions-element')
      if reactions_element:
        for reaction in reactions_element.find_all('reaction-element'):
          sticker_id = reaction.find('div', class_='reaction-sticker').get('data-doc-id')
          count = reaction.find('span', class_='reaction-counter').get_text(strip=True)
          reactions.append({'sticker_id': sticker_id, 'count': count})

      print(":::::::::::::::::::::::::::::::::::")
      print(message_link)
      print(":::::::::::::::::::::::::::::::::::")

      return telegram_chat_model(
        message_id=str(message_id),
        message_sharable_link=message_link,
        channel_id=telegram_channel_id,
        content=content_text,
        timestamp=timestamp,
        views=views,
        file_name=file_name,
        file_size=file_size,
        peer_id=peer_id,
        forwarded_from=forwarded_from,
        sender_name=None,
        sender_username=None,
        chat_title=None,
        channel_name=channel_name,
        message_type=message_type,
        media_url=media_url,
        media_caption=media_caption,
        reply_to_message_id=reply_to_message_id,
        edited_timestamp=edited_timestamp,
        message_status=message_status,
      )

    except Exception as e:
      print(f"Error parsing message: {e}")
      return None

  def parse_leak_data(self, page: Page = None):
    try:
      page.wait_for_selector(".chatlist-chat", timeout=150000)
    except:
      return

    chat_items = page.query_selector_all(".chatlist-chat")
    if not chat_items:
      return

    for index in range(len(chat_items)):
      chat_items = page.query_selector_all(".chatlist-chat")
      if index >= len(chat_items):
        break

      chat = chat_items[index]
      try:
        title = chat.inner_text().split('\n')[0]
      except:
        title = f"Chat #{index + 1}"

      try:
        chat.click()
        time.sleep(2)
        page.wait_for_selector(".chat-info", state="visible", timeout=10000)
      except:
        continue

      try:
        title_element = page.query_selector(".chat-info .peer-title")
        channel_name = title_element.inner_text().strip() if title_element else title
      except:
        channel_name = title

      scrollable = page.query_selector(".chats-container .scrollable.scrollable-y")
      if not scrollable:
        continue

      page.evaluate("(el) => el.scrollTop = el.scrollHeight", scrollable)
      time.sleep(1)

      seen_messages = set()
      threshold_date = datetime.now() - timedelta(days=305)
      scroll_count = 0
      max_scrolls = 200
      telegram_channel_id = self.get_channel_shareable_link(page)

      def get_oldest_date():
        oldest_date_local = None
        for group in page.query_selector_all("section.bubbles-date-group"):
          span = group.query_selector(".bubble.service.is-date span.i18n")
          if not span:
            continue
          try:
            text = span.inner_text().strip()
            try:
              date = datetime.strptime(text, "%B %d, %Y")
            except ValueError:
              date = datetime.strptime(text + f" {datetime.now().year}", "%B %d %Y")
              if date > datetime.now():
                date = date.replace(year=date.year - 1)
            if not oldest_date_local or date < oldest_date_local:
              oldest_date_local = date
          except:
            continue
        return oldest_date_local

      while scroll_count < max_scrolls:
        oldest_date = get_oldest_date()

        bubbles = page.query_selector_all(".bubble.channel-post")
        for bubble in reversed(bubbles):  # reverse for bottom-up processing
          try:
            msg_id = bubble.get_attribute("data-mid")
            if not msg_id or msg_id in seen_messages:
              continue
            html = bubble.inner_html()
            self.build_model_from_message(page, html, channel_name, msg_id, telegram_channel_id)
            seen_messages.add(msg_id)
          except:
            continue

        if oldest_date and oldest_date <= threshold_date:
          break

        page.evaluate("(el) => el.scrollTop -= el.offsetHeight", scrollable)

      break
