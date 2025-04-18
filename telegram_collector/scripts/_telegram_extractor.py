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
  def build_model_from_message(html: str, channel_name: str, message_type: str = "message") -> telegram_chat_model | None:
    try:
      soup = BeautifulSoup(html, 'html.parser')
      bubble_div = soup.find('div', class_='bubble-content-wrapper')
      avatar_div = soup.find('div', class_='bubble-name-forwarded-avatar')
      peer_id = avatar_div.get('data-peer-id') if avatar_div else None
      if not bubble_div:
        return None

      # Skip service and sponsored messages
      parent_bubble = soup.find_parent('div', class_='bubble')
      if parent_bubble and ('service' in parent_bubble.get('class') or 'is-sponsored' in parent_bubble.get('class')):
        return None

      time_tag = soup.select_one('div.time-inner')
      timestamp = time_tag.get('title').split('\n')[0] if time_tag and time_tag.has_attr('title') else None

      unique_hash = helper_method.generate_data_hash(timestamp + channel_name)
      message_id = unique_hash

      # Timestamp
      time_tag = soup.select_one('div.time-inner')
      timestamp = time_tag.get('title').split('\n')[0] if time_tag and time_tag.has_attr('title') else None

      # Edited timestamp
      edited_timestamp = None
      if time_tag and time_tag.has_attr('title') and '\n' in time_tag.get('title'):
        parts = time_tag.get('title').split('\n')
        for part in parts:
          if part.startswith('Edited:') or part.startswith('Original:'):
            edited_timestamp = part.split(': ', 1)[1].strip()

      # Views
      views_tag = soup.find('span', class_='post-views')
      views = views_tag.get_text(strip=True) if views_tag else None

      # Content text
      content_text = None
      if message_type == "webpage":
        content_tag = soup.find('div', class_='webpage-text')
        content_text = content_tag.get_text(strip=True) if content_tag else None
      if not content_text:
        document_message = soup.find('div', class_='document-message')
        translatable_message = soup.find('span', class_='translatable-message')
        text_tag = document_message if document_message else translatable_message
        content_text = text_tag.get_text(strip=True) if text_tag else None

      # File info
      file_name_tag = soup.find('middle-ellipsis-element')
      file_name = file_name_tag.get_text(strip=True) if file_name_tag else None

      file_size_tag = soup.select_one('div.document-size')
      file_size = None
      if file_size_tag:
        match = re.search(r'\d+(?:\.\d+)?\s*(KB|MB|GB)|[\d,]+\s*(KB|MB|GB)', file_size_tag.get_text())
        file_size = match.group(0) if match else file_size_tag.get_text(strip=True)

      file_path = f"downloads/{file_name}" if file_name else None

      # Forwarded from
      forwarded_from = None
      forwarded_tag = soup.find('div', class_='name')
      if forwarded_tag and 'bubble-name-forwarded' in forwarded_tag.get('class', []):
        peer_title = forwarded_tag.find('span', class_='peer-title')
        forwarded_from = peer_title.get_text(strip=True) if peer_title else None

      # Reply info
      reply_tag = soup.find('div', class_='reply')
      reply_to_message_id = reply_tag.get('data-reply-to-mid') if reply_tag and reply_tag.has_attr('data-reply-to-mid') else None

      # Media URL and caption
      media_url = None
      media_caption = None
      if soup.find('img', class_='media-photo'):
        photo_tag = soup.find('img', class_='media-photo')
        if photo_tag:
          media_url = photo_tag.get('src')
        caption_tag = soup.find('span', class_='translatable-message')
        if caption_tag:
          media_caption = caption_tag.get_text(strip=True)
      elif soup.find('video'):
        video_tag = soup.find('video')
        if video_tag:
          media_url = video_tag.get('src')
        caption_tag = soup.find('span', class_='translatable-message')
        if caption_tag:
          media_caption = caption_tag.get_text(strip=True)
      elif soup.find('audio'):
        audio_tag = soup.find('audio')
        if audio_tag:
          media_url = audio_tag.get('src')
        caption_tag = soup.find('span', class_='translatable-message')
        if caption_tag:
          media_caption = caption_tag.get_text(strip=True)

      # Detect message type
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

      # Status
      status_classes = parent_bubble.get('class') if parent_bubble else []
      message_status = ' '.join(status_classes)

      # Reactions
      reactions = []
      reactions_element = soup.find('reactions-element')
      if reactions_element:
        for reaction in reactions_element.find_all('reaction-element'):
          sticker_id = reaction.find('div', class_='reaction-sticker').get('data-doc-id')
          count = reaction.find('span', class_='reaction-counter').get_text(strip=True)
          reactions.append({'sticker_id': sticker_id, 'count': count})

      return telegram_chat_model(
        message_id=str(message_id),
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
        file_path=file_path,
      )
    except Exception as e:
      print(f"Error parsing message: {e}")
      return None

  def parse_leak_data(self, page: Page = None):
    try:
      page.wait_for_selector(".chatlist-chat", timeout=15000)
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

      seen_messages = set()
      threshold_date = datetime.now() - timedelta(days=305)
      scroll_count = 0
      max_scrolls = 200

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

        for bubble in page.query_selector_all(".bubble.channel-post"):
          try:
            msg_id = bubble.get_attribute("data-mid")
            if msg_id and msg_id not in seen_messages:
              html = bubble.inner_html()
              self.build_model_from_message(html, channel_name)
              seen_messages.add(msg_id)
          except:
            continue

        if oldest_date and oldest_date <= threshold_date:
          break

        prev_scroll = page.evaluate("(el) => el.scrollTop", scrollable)
        page.evaluate("(el) => el.scrollTop -= el.offsetHeight", scrollable)
        new_scroll = page.evaluate("(el) => el.scrollTop", scrollable)

        if new_scroll == prev_scroll:
          break

        scroll_count += 1