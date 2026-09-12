import csv
from pathlib import Path
from statistics import median

from fastapi import HTTPException

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


async def create_channel_source(source: ChannelSourceCreate) -> ChannelSourceRead:
    """
    创建 TikTok 渠道账号数据源配置。

    Args:
        source: 客户端提交的数据源配置，包括店铺、账号、主页 URL 和启用状态。

    Returns:
        创建后的数据源配置，包含系统分配的 id。
    """
    global next_source_id

    for existing_source in channel_sources_db:
        if existing_source.account == source.account:
            raise HTTPException(
                status_code=400,
                detail="Channel source account already exists"
            )

        if existing_source.source_url == source.source_url:
            raise HTTPException(
                status_code=400,
                detail="Channel source URL already exists"
            )

    new_source = ChannelSourceRead(
        id=next_source_id,
        shop=source.shop,
        account=source.account,
        source_url=source.source_url,
        is_active=source.is_active,
        last_collected_at=None,
    )

    channel_sources_db.append(new_source)
    next_source_id += 1

    return new_source


async def get_channel_sources() -> list[ChannelSourceRead]:
    """
    查询所有 TikTok 渠道账号数据源配置。

    Returns:
        当前系统中的数据源配置列表。
    """
    return channel_sources_db
