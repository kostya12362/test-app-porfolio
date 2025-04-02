from datetime import datetime
from core.schemas import PublicSchema
from social_media.models import Account


class TagSchemaRequest(PublicSchema):
    title: str


class TagCreateSchemaRequest(TagSchemaRequest):
    title: str


class TagSchemaResponse(TagSchemaRequest):
    id: int


class AccountSchemaRequest(PublicSchema):
    username: str
    provider: Account.Provider
    tags: list[str] = []


class TagsForAccountSchemaResponse(PublicSchema):
    total: int
    items: list[TagSchemaResponse] = []


class AccountSchemaResponse(AccountSchemaRequest):
    id: int
    created_at: datetime
    tags: TagsForAccountSchemaResponse


class TagsForPostSchemaResponse(TagsForAccountSchemaResponse):
    pass


class PostSchemaResponse(PublicSchema):
    id: int
    uid: str
    likes: int
    comments: int
    description: str
    username: str
    uid: str
    created_at: datetime
    store_at: datetime
    tags: TagsForPostSchemaResponse
