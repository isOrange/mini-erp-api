import csv
from datetime import datetime
from pathlib import Path
from statistics import median

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.business.channel_intelligence.collectors import collect_tiktok_account_videos
from src.apps.business.channel_intelligence.models import ChannelSource, CollectionRun, ChannelVideo
from src.apps.business.channel_intelligence.repositories import (
    ChannelSourceRepository,
    ChannelVideoRepository,
    CollectionRunRepository,
)
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
    VideoRead,
)

CSV_PATH = Path("data/tiktok-dashboard.csv")

CSV_COLUMNS = [
    "shop",
    "account",
    "video_title",
    "video_url",
    "published_at",
    "duration_seconds",
    "views",
    "likes",
    "comments",
    "shares",
    "saves",
    "engagement_rate",
]

# 临时内存数据源配置。后续接入数据库后，这里会替换成 sources 表。
channel_sources_db: list[ChannelSourceRead] = []

# 临时内存采集记录。后续接入数据库后，这里会替换成 collection_runs 表。
collection_runs_db: list[CollectionRunRead] = []

next_source_id: int = 1

next_run_id: int = 1


def to_int(value: str) -> int:
    if value == "":
        return 0

    return int(float(value))


def to_float(value: str) -> float | None:
    if value == "":
        return None

    return float(value)


def load_videos() -> list[VideoRead]:
    videos: list[VideoRead] = []

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            data = dict(zip(CSV_COLUMNS, row))

            videos.append(
                VideoRead(
                    shop=data["shop"],
                    account=data["account"],
                    video_title=data["video_title"],
                    video_url=data["video_url"],
                    published_at=data["published_at"],
                    duration_seconds=to_int(data["duration_seconds"]),
                    views=to_int(data["views"]),
                    likes=to_int(data["likes"]),
                    comments=to_int(data["comments"]),
                    shares=to_int(data["shares"]),
                    saves=to_int(data["saves"]),
                    engagement_rate=to_float(data["engagement_rate"]),
                )
            )

    return videos


async def get_channel_summary() -> ChannelSummaryRead:
    videos = load_videos()

    views = [video.views for video in videos]
    durations = [video.duration_seconds for video in videos]

    return ChannelSummaryRead(
        shop_count=len({video.shop for video in videos}),
        account_count=len({video.account for video in videos}),
        video_count=len(videos),
        total_views=sum(views),
        median_views=median(views),
        average_duration_seconds=sum(durations) / len(durations),
    )


async def get_shop_summaries() -> list[ShopSummaryRead]:
    videos = load_videos()

    shops = sorted({video.shop for video in videos})
    results: list[ShopSummaryRead] = []

    for shop in shops:
        shop_videos = [video for video in videos if video.shop == shop]

        results.append(
            ShopSummaryRead(
                shop=shop,
                account_count=len({video.account for video in shop_videos}),
                video_count=len(shop_videos),
                total_views=sum(video.views for video in shop_videos),
            )
        )

    return results


async def get_account_summaries() -> list[AccountSummaryRead]:
    videos = load_videos()

    accounts = sorted({video.account for video in videos})
    results: list[AccountSummaryRead] = []

    for account in accounts:
        account_videos = [video for video in videos if video.account == account]
        views = [video.views for video in account_videos]
        engagement_rates = [
            video.engagement_rate
            for video in account_videos
            if video.engagement_rate is not None
        ]

        results.append(
            AccountSummaryRead(
                account=account,
                shop=account_videos[0].shop,
                video_count=len(account_videos),
                total_views=sum(views),
                median_views=median(views),
                engagement_rate=sum(engagement_rates) / len(engagement_rates)
                if engagement_rates
                else None,
            )
        )

    return sorted(results, key=lambda item: item.median_views, reverse=True)


async def get_video_list(
        shop: str | None = None,
        account: str | None = None,
        page: int = 1,
        page_size: int = 20,
) -> VideoListRead:
    videos = load_videos()

    if shop is not None:
        videos = [video for video in videos if video.shop == shop]

    if account is not None:
        videos = [video for video in videos if video.account == account]

    videos = sorted(videos, key=lambda video: video.views, reverse=True)

    start = (page - 1) * page_size
    end = start + page_size

    return VideoListRead(
        total=len(videos),
        items=videos[start:end],
    )


async def get_filter_options() -> FilterOptionsRead:
    videos = load_videos()

    return FilterOptionsRead(
        shops=sorted({video.shop for video in videos}),
        accounts=sorted({video.account for video in videos}),
    )


async def get_content_signals() -> ContentSignalRead:
    videos = load_videos()

    videos_with_engagement_rate = [
        video for video in videos if video.engagement_rate is not None
    ]

    durations = [video.duration_seconds for video in videos]

    return ContentSignalRead(
        top_view_video=max(videos, key=lambda video: video.views),
        top_engagement_video=max(
            videos_with_engagement_rate,
            key=lambda video: video.engagement_rate,
        ),
        latest_video=max(videos, key=lambda video: video.published_at),
        average_duration_seconds=sum(durations) / len(durations),
    )


async def get_channel_dashboard() -> ChannelDashboardRead:
    return ChannelDashboardRead(
        summary=await get_channel_summary(),
        shops=await get_shop_summaries(),
        accounts=await get_account_summaries(),
        signals=await get_content_signals(),
    )


async def create_channel_source(
        source: ChannelSourceCreate,
        db: AsyncSession,
) -> ChannelSourceRead:
    """
    创建 TikTok 渠道账号数据源配置。

    Args:
        source: 客户端提交的数据源配置，包括店铺、账号、主页 URL 和启用状态。
        db: 当前请求使用的数据库会话。

    Returns:
        创建后的数据源配置，包含系统分配的 id。
    """
    repository = ChannelSourceRepository(db)

    existing_source = await repository.get_by_account(source.account)
    if existing_source is not None:
        raise HTTPException(
            status_code=400,
            detail="Channel source account already exists",
        )

    existing_source = await repository.get_by_source_url(source.source_url)
    if existing_source is not None:
        raise HTTPException(
            status_code=400,
            detail="Channel source URL already exists",
        )

    new_source = ChannelSource(
        shop=source.shop,
        account=source.account,
        source_url=source.source_url,
        is_active=source.is_active,
    )

    created_source = await repository.create(new_source)

    return ChannelSourceRead(
        id=created_source.id,
        shop=created_source.shop,
        account=created_source.account,
        source_url=created_source.source_url,
        is_active=created_source.is_active,
        last_collected_at=created_source.last_collected_at.isoformat()
        if created_source.last_collected_at is not None
        else None,
    )


async def get_channel_sources(db: AsyncSession) -> list[ChannelSourceRead]:
    """
    查询所有 TikTok 渠道账号数据源配置。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        当前系统中的数据源配置列表。
    """
    repository = ChannelSourceRepository(db)
    sources = await repository.get_all()

    return [
        ChannelSourceRead(
            id=source.id,
            shop=source.shop,
            account=source.account,
            source_url=source.source_url,
            is_active=source.is_active,
            last_collected_at=source.last_collected_at.isoformat()
            if source.last_collected_at is not None
            else None,
        )
        for source in sources
    ]


def to_channel_video_model(
        video: VideoRead,
        source_id: int,
) -> ChannelVideo:
    """
    将采集到的视频返回模型转换成数据库视频模型。

    Args:
        video: 采集器返回的视频数据。
        source_id: 视频所属的数据源 id。

    Returns:
        可写入数据库的视频模型。
    """
    return ChannelVideo(
        source_id=source_id,
        shop=video.shop,
        account=video.account,
        video_title=video.video_title,
        video_url=video.video_url,
        thumbnail_url=video.thumbnail_url,
        published_at=datetime.fromtimestamp(int(video.published_at))
        if video.published_at
        else None,
        duration_seconds=video.duration_seconds,
        views=video.views,
        likes=video.likes,
        comments=video.comments,
        shares=video.shares,
        saves=video.saves,
        engagement_rate=video.engagement_rate,
        last_collected_at=datetime.now(),
    )


async def collect_channel_source(
        source_id: int,
        db: AsyncSession,
) -> CollectionRunRead:
    """
    触发指定 TikTok 渠道账号数据源的采集任务。

    Args:
        source_id: 要采集的数据源 id。

    Returns:
        本次采集任务执行记录。
    """
    source_repository = ChannelSourceRepository(db)
    source = await source_repository.get_by_id(source_id)

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Channel source not found",
        )

    if not source.is_active:
        raise HTTPException(
            status_code=400,
            detail="Channel source is inactive",
        )

    try:
        videos = collect_tiktok_account_videos(
            account=source.account,
            shop=source.shop,
        )

        video_repository = ChannelVideoRepository(db)

        for video in videos:
            await video_repository.upsert(
                to_channel_video_model(
                    video=video,
                    source_id=source.id,
                )
            )

        return await create_collection_run(
            source_id=source.id,
            status="success",
            collected_count=len(videos),
            db=db,
        )
    except Exception as error:
        return await create_collection_run(
            source_id=source.id,
            status="failed",
            collected_count=0,
            db=db,
            error_message=str(error),
        )


async def create_collection_run(
        source_id: int,
        status: str,
        collected_count: int,
        db: AsyncSession,
        error_message: str | None = None,
) -> CollectionRunRead:
    """
    创建一次采集任务执行记录。

    Args:
        source_id: 被采集的数据源 id。
        status: 采集状态，例如 success 或 failed。
        collected_count: 本次采集到的视频数量。
        db: 当前请求使用的数据库会话。
        error_message: 采集失败时的错误信息。

    Returns:
        创建后的采集任务执行记录。
    """
    repository = CollectionRunRepository(db)

    new_run = CollectionRun(
        source_id=source_id,
        status=status,
        collected_count=collected_count,
        error_message=error_message,
    )

    created_run = await repository.create(new_run)

    return CollectionRunRead(
        id=created_run.id,
        source_id=created_run.source_id,
        status=created_run.status,
        collected_count=created_run.collected_count,
        error_message=created_run.error_message,
    )


async def get_collection_runs(db: AsyncSession) -> list[CollectionRunRead]:
    """
    查询所有采集任务执行记录。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        当前系统中的采集任务执行记录列表。
    """
    repository = CollectionRunRepository(db)
    runs = await repository.get_all()

    return [
        CollectionRunRead(
            id=run.id,
            source_id=run.source_id,
            status=run.status,
            collected_count=run.collected_count,
            error_message=run.error_message,
        )
        for run in runs
    ]
