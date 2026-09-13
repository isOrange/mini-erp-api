from datetime import datetime
from statistics import median

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.business.channel_intelligence.collectors import collect_tiktok_account_videos
from src.apps.business.channel_intelligence.models import (
    ChannelSource,
    ChannelVideo,
    CollectionRun,
)
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


def to_video_read(video: ChannelVideo) -> VideoRead:
    """
    将数据库视频模型转换成接口视频返回模型。

    Args:
        video: 数据库中的视频指标模型。

    Returns:
        接口使用的视频返回模型。
    """
    return VideoRead(
        shop=video.shop,
        account=video.account,
        video_title=video.video_title,
        video_url=video.video_url,
        thumbnail_url=video.thumbnail_url,
        published_at=video.published_at.isoformat()
        if video.published_at is not None
        else "",
        duration_seconds=video.duration_seconds,
        views=video.views,
        likes=video.likes,
        comments=video.comments,
        shares=video.shares,
        saves=video.saves,
        engagement_rate=video.engagement_rate,
    )


async def get_channel_summary(db: AsyncSession) -> ChannelSummaryRead:
    """
    从数据库聚合渠道看板总览数据。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        渠道看板总览数据。
    """
    repository = ChannelVideoRepository(db)
    videos = await repository.get_all()

    if not videos:
        return ChannelSummaryRead(
            shop_count=0,
            account_count=0,
            video_count=0,
            total_views=0,
            median_views=0,
            average_duration_seconds=0,
        )

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


async def get_shop_summaries(db: AsyncSession) -> list[ShopSummaryRead]:
    """
    从数据库按店铺聚合视频指标。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        店铺汇总数据列表。
    """
    repository = ChannelVideoRepository(db)
    videos = await repository.get_all()

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


async def get_account_summaries(db: AsyncSession) -> list[AccountSummaryRead]:
    """
    从数据库按账号聚合视频指标。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        账号汇总数据列表。
    """
    repository = ChannelVideoRepository(db)
    videos = await repository.get_all()

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
    db: AsyncSession,
    shop: str | None = None,
    account: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> VideoListRead:
    """
    分页查询视频指标列表。

    Args:
        db: 当前请求使用的数据库会话。
        shop: 店铺筛选条件。
        account: 账号筛选条件。
        page: 页码，从 1 开始。
        page_size: 每页数量。

    Returns:
        视频列表分页结果。
    """
    repository = ChannelVideoRepository(db)
    total = await repository.count(shop=shop, account=account)
    videos = await repository.get_page(
        shop=shop,
        account=account,
        page=page,
        page_size=page_size,
    )

    return VideoListRead(
        total=total,
        items=[to_video_read(video) for video in videos],
    )


async def get_filter_options(db: AsyncSession) -> FilterOptionsRead:
    """
    从数据库查询看板筛选项。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        看板筛选项。
    """
    repository = ChannelVideoRepository(db)

    return FilterOptionsRead(
        shops=await repository.get_distinct_shops(),
        accounts=await repository.get_distinct_accounts(),
    )


async def get_content_signals(db: AsyncSession) -> ContentSignalRead:
    """
    从数据库提取内容信号。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        内容信号数据。
    """
    repository = ChannelVideoRepository(db)
    videos = await repository.get_all()
    durations = [video.duration_seconds for video in videos]
    top_view_video = await repository.get_top_view_video()
    top_engagement_video = await repository.get_top_engagement_video()
    latest_video = await repository.get_latest_video()

    return ContentSignalRead(
        top_view_video=to_video_read(top_view_video)
        if top_view_video is not None
        else None,
        top_engagement_video=to_video_read(top_engagement_video)
        if top_engagement_video is not None
        else None,
        latest_video=to_video_read(latest_video) if latest_video is not None else None,
        average_duration_seconds=sum(durations) / len(durations) if durations else 0,
    )


async def get_channel_dashboard(db: AsyncSession) -> ChannelDashboardRead:
    """
    从数据库组装渠道看板首页数据。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        渠道看板首页数据。
    """
    return ChannelDashboardRead(
        summary=await get_channel_summary(db),
        shops=await get_shop_summaries(db),
        accounts=await get_account_summaries(db),
        signals=await get_content_signals(db),
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
        collected_count = 0

        for video in videos:
            if not video.video_url:
                continue

            await video_repository.upsert(
                to_channel_video_model(
                    video=video,
                    source_id=source.id,
                )
            )
            collected_count += 1

        source.last_collected_at = datetime.now()

        return await create_collection_run(
            source_id=source.id,
            status="success",
            collected_count=collected_count,
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
