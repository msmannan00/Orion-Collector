from typing import List
from pydantic import BaseModel

class telegram_chat_model(BaseModel):
    message_id: str
    content_html: str
    timestamp: str = None
    views: str = None
    file_name: str = None
    file_size: str = None
    forwarded_from: str = None
    peer_id: str = None
