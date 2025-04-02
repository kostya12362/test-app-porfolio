from typing import Annotated

from asgiref.sync import sync_to_async

from fastapi import APIRouter, Depends, status, Path, Query

from core.db.utils import AsyncAtomicContextManager, AsyncModelUtils
from core.pagination import PageInfo, PaginationResponse, ParamsInput, paginate
from core.schemas import MessageResponse, Response, ResponseMulti

from users.models import User
from users.api.auth.security import user_auth
from social_media.api.messages import AccountNotFound, AccountAlreadyExists, TagAlreadyExists
from social_media.api.schemas import (
    AccountSchemaRequest,
    AccountSchemaResponse,
    PostSchemaResponse,
    TagSchemaRequest,
    TagSchemaResponse,
    TagCreateSchemaRequest
)
from social_media.models import Account, Post, UserSubscription, Tag

router = APIRouter(prefix="/social-media")

AccountID = Annotated[int, Path(..., title="Account ID", alias="id", gt=0)]
PostID = Annotated[int, Path(..., title="Post ID", alias="id", gt=0)]
TagID = Annotated[int, Path(..., title="Tag ID", alias="id", gt=0)]


@router.get('/providers', status_code=status.HTTP_200_OK, tags=["Providers"])
async def get_all_providers() -> ResponseMulti[str]:
    return ResponseMulti[str](data=[i[0] for i in Account.Provider.choices])


@router.post(path="/accounts", status_code=status.HTTP_201_CREATED, tags=["Accounts"])
async def add_account(
        body: AccountSchemaRequest,
        user: User = Depends(user_auth.get_current_user)
) -> Response[AccountSchemaResponse]:
    async with AsyncAtomicContextManager():
        account, _ = await Account.objects.aget_or_create(
            username=body.username,
            provider=body.provider,
        )
        subscription, state = await UserSubscription.objects.aget_or_create(
            account=account,
            user=user,
        )
        if state is False:
            raise AccountAlreadyExists(body.username)
        multi = AsyncModelUtils(Tag, [{"title": i} for i in body.tags], 'title')
        tags = await multi.update_or_create()
        await subscription.follow_tags.aset(tags)
        await subscription.asave()
    obj = await Account.extract(user=user).filter(id=account.id).afirst()
    return Response[AccountSchemaResponse](data=obj)


@router.delete(
    path='/accounts/{id}',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(user_auth.get_current_user)],
    tags=["Accounts"],
)
async def remove_account(account_id: AccountID):
    total, _ = await UserSubscription.objects.filter(account_id=account_id).adelete()
    if total == 0:
        raise AccountNotFound(account_id)
    return MessageResponse(
        message="Account deleted successfully",
        code="ACCOUNT_DELETED",
    )


@router.get(path="/accounts", status_code=status.HTTP_200_OK, tags=["Accounts"])
async def get_accounts(
        q: str = Query(None, title="Search by username"),
        params: ParamsInput = Depends(),
        user: User = Depends(user_auth.get_current_user),
) -> PaginationResponse[AccountSchemaResponse, PageInfo]:
    """Display only first 5 tags"""
    queryset = Account.extract(user=user, tags_limit=5)
    if q:
        queryset = queryset.filter(username__icontains=q)
    return await paginate(queryset, params, AccountSchemaResponse)


@router.get(path='/accounts/{id}', status_code=status.HTTP_200_OK, tags=["Accounts"])
async def get_account(
        account_id: AccountID,
        user: User = Depends(user_auth.get_current_user)
) -> Response[AccountSchemaResponse]:
    obj = await Account.extract(user=user).filter(id=account_id).afirst()
    if obj is None:
        raise AccountNotFound(account_id)
    return Response[AccountSchemaResponse](data=obj)


@router.get(path="/accounts/{id}/posts", status_code=status.HTTP_200_OK, tags=["Posts"])
async def get_posts(
        account_id: AccountID,
        params: ParamsInput = Depends(),
        user: User = Depends(user_auth.get_current_user)
) -> PaginationResponse[PostSchemaResponse, PageInfo]:
    queryset = Post.extract(user=user).filter(
        account_id=account_id,
    )
    return await paginate(queryset, params, PostSchemaResponse)


@router.post(path="/accounts/{id}/tags", status_code=status.HTTP_201_CREATED, tags=["Tags"])
async def create_tag(
        account_id: AccountID,
        body: TagSchemaRequest,
        user: User = Depends(user_auth.get_current_user)
) -> TagSchemaRequest:
    async with AsyncAtomicContextManager():
        obj, value = await Tag.objects.aget_or_create(**body.model_dump())
        subscription = await UserSubscription.objects.aget(
            user=user,
            account_id=account_id
        )
        if obj in await sync_to_async(subscription.follow_tags.all)():
            raise TagAlreadyExists(obj.title)
        await subscription.follow_tags.aadd(obj)
        return TagSchemaResponse.model_validate(obj)


@router.get(
    path="/tags",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(user_auth.get_current_user)],
    tags=["Tags"],
)
async def get_tags(
        q: str = Query(None, title="Search by tag title"),
        params: ParamsInput = Depends(),
) -> PaginationResponse[TagSchemaResponse, PageInfo]:
    """Get a list of tags the user is subscribed to"""
    queryset = Tag.objects.all()
    if q:
        queryset = queryset.filter(title__icontains=q)
    return await paginate(queryset, params, TagSchemaResponse)
