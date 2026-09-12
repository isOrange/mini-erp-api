from fastapi import APIRouter, Query

from src.apps.business.channel_intelligence.schemas import (
    AccountSummaryRead,
    ChannelDashboardRead,
    ChannelSourceCreate,
    ChannelSourceRead,
    ChannelSummaryRead,
    CollectionRunRead,
    ContentSignalRead,
    FilterOptionsRead,
    ShopSummaryRead,
    VideoListRead,
)
from src.apps.business.channel_intelligence.services import (
    create_channel_source,
    create_collection_run,
    get_account_summaries,
    get_channel_dashboard,
    get_channel_sources,
    get_channel_summary,
    get_collection_runs,
    get_content_signals,
    get_filter_options,
    get_shop_summaries,
    get_video_list,
    collect_channel_source,
)

router = APIRouter(
    prefix="/channel-intelligence",
    tags=["Business - Channel Intelligence"],
)


@router.get("/dashboard", response_model=ChannelDashboardRead)
async def read_channel_dashboard():
    return await get_channel_dashboard()


@router.get("/summary", response_model=ChannelSummaryRead)
async def read_channel_summary():
    return await get_channel_summary()


@router.get("/shops", response_model=list[ShopSummaryRead])
async def read_shop_summaries():
    return await get_shop_summaries()


@router.get("/accounts", response_model=list[AccountSummaryRead])
async def read_account_summaries():
    return await get_account_summaries()


@router.get("/videos", response_model=VideoListRead)
async def read_video_list(
        shop: str | None = None,
        account: str | None = None,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
):
    return await get_video_list(
        shop=shop,
        account=account,
        page=page,
        page_size=page_size,
    )


@router.get("/signals", response_model=ContentSignalRead)
async def read_content_signals():
    return await get_content_signals()


@router.get("/filters", response_model=FilterOptionsRead)
async def read_filter_options():
    return await get_filter_options()


@router.post("/sources", response_model=ChannelSourceRead)
async def write_channel_source(source: ChannelSourceCreate):
    return await create_channel_source(source)


@router.get("/sources", response_model=list[ChannelSourceRead])
async def read_channel_sources():
    return await get_channel_sources()


@router.post("/collection-runs", response_model=CollectionRunRead)
async def write_collection_run(
        source_id: int,
        status: str,
        collected_count: int,
        error_message: str | None = None,
):
    return await create_collection_run(
        source_id=source_id,
        status=status,
        collected_count=collected_count,
        error_message=error_message,
    )


@router.get("/collection-runs", response_model=list[CollectionRunRead])
async def read_collection_runs():
    return await get_collection_runs()


@router.post("/sources/{source_id}/collect", response_model=CollectionRunRead)
async def write_channel_source_collection(source_id: int):
    return await collect_channel_source(source_id)
