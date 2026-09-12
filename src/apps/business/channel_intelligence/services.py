import csv
from pathlib import Path
from statistics import median

from src.apps.business.channel_intelligence.schemas import (
    AccountSummaryRead,
    ChannelDashboardRead,
    ChannelSummaryRead,
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
