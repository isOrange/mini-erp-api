from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.business.channel_intelligence.models import (
    ChannelSource,
    ChannelVideo,
    CollectionRun,
)


class ChannelSourceRepository:
    """渠道数据源数据库访问层。"""

    def __init__(self, db: AsyncSession):
        """
        初始化渠道数据源 repository。

        Args:
            db: 当前请求使用的数据库会话。
        """
        self.db = db

    async def create(self, source: ChannelSource) -> ChannelSource:
        """
        创建渠道数据源。

        Args:
            source: 待保存的数据源模型。

        Returns:
            保存后的数据源模型。
        """
        self.db.add(source)
        await self.db.commit()
        await self.db.refresh(source)
        return source

    async def get_all(self) -> list[ChannelSource]:
        """
        查询所有渠道数据源。

        Returns:
            渠道数据源列表。
        """
        result = await self.db.execute(
            select(ChannelSource).order_by(ChannelSource.id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, source_id: int) -> ChannelSource | None:
        """
        根据 id 查询渠道数据源。

        Args:
            source_id: 数据源 id。

        Returns:
            找到时返回数据源模型，否则返回 None。
        """
        return await self.db.get(ChannelSource, source_id)

    async def get_by_account(self, account: str) -> ChannelSource | None:
        """
        根据账号查询渠道数据源。

        Args:
            account: TikTok 账号名。

        Returns:
            找到时返回数据源模型，否则返回 None。
        """
        result = await self.db.execute(
            select(ChannelSource).where(ChannelSource.account == account)
        )
        return result.scalar_one_or_none()

    async def get_by_source_url(self, source_url: str) -> ChannelSource | None:
        """
        根据主页 URL 查询渠道数据源。

        Args:
            source_url: TikTok 账号主页 URL。

        Returns:
            找到时返回数据源模型，否则返回 None。
        """
        result = await self.db.execute(
            select(ChannelSource).where(ChannelSource.source_url == source_url)
        )
        return result.scalar_one_or_none()


class CollectionRunRepository:
    """采集任务执行记录数据库访问层。"""

    def __init__(self, db: AsyncSession):
        """
        初始化采集任务执行记录 repository。

        Args:
            db: 当前请求使用的数据库会话。
        """
        self.db = db

    async def create(self, run: CollectionRun) -> CollectionRun:
        """
        创建采集任务执行记录。

        Args:
            run: 待保存的采集任务执行记录模型。

        Returns:
            保存后的采集任务执行记录模型。
        """
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_all(self) -> list[CollectionRun]:
        """
        查询所有采集任务执行记录。

        Returns:
            采集任务执行记录列表。
        """
        result = await self.db.execute(
            select(CollectionRun).order_by(CollectionRun.id.desc())
        )
        return list(result.scalars().all())


class ChannelVideoRepository:
    """渠道视频指标数据库访问层。"""

    def __init__(self, db: AsyncSession):
        """
        初始化渠道视频 repository。

        Args:
            db: 当前请求使用的数据库会话。
        """
        self.db = db

    async def get_by_video_url(self, video_url: str) -> ChannelVideo | None:
        """
        根据视频 URL 查询视频指标。

        Args:
            video_url: TikTok 视频 URL。

        Returns:
            找到时返回视频指标模型，否则返回 None。
        """
        result = await self.db.execute(
            select(ChannelVideo).where(ChannelVideo.video_url == video_url)
        )
        return result.scalar_one_or_none()

    async def upsert(self, video: ChannelVideo) -> ChannelVideo:
        """
        按 video_url 新增或更新视频指标。

        Args:
            video: 本次采集得到的视频指标模型。

        Returns:
            新增或更新后的视频指标模型。
        """
        existing_video = await self.get_by_video_url(video.video_url)

        if existing_video is None:
            self.db.add(video)
            await self.db.commit()
            await self.db.refresh(video)
            return video

        existing_video.source_id = video.source_id
        existing_video.shop = video.shop
        existing_video.account = video.account
        existing_video.video_title = video.video_title
        existing_video.thumbnail_url = video.thumbnail_url
        existing_video.published_at = video.published_at
        existing_video.duration_seconds = video.duration_seconds
        existing_video.views = video.views
        existing_video.likes = video.likes
        existing_video.comments = video.comments
        existing_video.shares = video.shares
        existing_video.saves = video.saves
        existing_video.engagement_rate = video.engagement_rate
        existing_video.last_collected_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(existing_video)
        return existing_video
