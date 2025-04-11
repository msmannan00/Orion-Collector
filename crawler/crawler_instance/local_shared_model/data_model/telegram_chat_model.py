from pydantic import BaseModel
from typing import Optional


class telegram_chat_model(BaseModel):
    message_id: str
    content: str
    timestamp: Optional[str] = None
    views: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[str] = None
    forwarded_from: Optional[str] = None
    peer_id: Optional[str] = None
    sender_name: Optional[str] = None
    sender_username: Optional[str] = None
    chat_type: Optional[str] = None
    chat_title: Optional[str] = None
    message_type: Optional[str] = None
    media_url: Optional[str] = None
    media_caption: Optional[str] = None
    reply_to_message_id: Optional[str] = None
    edited_timestamp: Optional[str] = None
    message_status: Optional[str] = None
    file_saved_as: Optional[str] = None
    file_path: Optional[str] = None
    channel_name: Optional[str] = None
