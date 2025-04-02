import re
from datetime import datetime
from typing import Optional, Any

import jmespath
from pydantic import BaseModel

from core.parser import BaseParser


class PostItemSchema(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    tags: list[str] = []
    created_at: int
    stored_at: int
    account_id: int


class PostItemParser(BaseParser):
    instance = PostItemSchema

    def __init__(self, obj: dict[str, Any], metadata: dict[str, Any]):
        self.metadata = metadata
        self.data: dict[str, Any] = jmespath.search(
            """{
                id: id,
                shortcode: code,
                created_at: caption.created_at,
                caption: caption.text,
                taken_at: taken_at,
                video_versions: video_versions,
                image_versions2: image_versions2,
                original_height: original_height,
                original_width: original_width,
                link: link,
                title: title,
                comment_count: comment_count,
                top_likers: top_likers,
                like_count: like_count,
                usertags: usertags,
                clips_metadata: clips_metadata,
                comments: comments
            }""",
            obj,
        )

    @property
    def id(self) -> str:
        return self.data['id']

    @property
    def title(self) -> str | None:
        return self.data['title']

    @property
    def description(self) -> str | None:
        return self.data['caption']

    @property
    def like_count(self) -> int:
        value = self.data.get('like_count')
        return value if value else 0

    @property
    def comment_count(self) -> int:
        value = self.data.get('comment_count')
        return value if value else 0

    @property
    def created_at(self) -> int:
        return self.data['created_at']

    @property
    def stored_at(self) -> int:
        return int(datetime.now().timestamp())

    @property
    def tags(self) -> list[str]:
        caption_text = self.data.get("caption", "")
        tags = re.findall(r"#\w+", caption_text)
        return [re.sub(r'^#', '', i) for i in tags]

    @property
    def account_id(self) -> str:
        return self.metadata['account_id']
