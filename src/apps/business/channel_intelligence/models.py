from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ChannelSource(Base):
    """TikTok 渠道账号数据源表。"""

    __tablename__ = "channel_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop: Mapped[str] = mapped_column(String(64), nullable=False)
    account: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    source_url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_collected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )


class CollectionRun(Base):
    """TikTok 渠道采集任务执行记录表。"""

    __tablename__ = "collection_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    collected_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class ChannelVideo(Base):
    """TikTok 渠道视频指标表。"""

    __tablename__ = "channel_videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(nullable=False, index=True)
    shop: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    video_title: Mapped[str] = mapped_column(Text, nullable=False)
    video_url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(default=0, nullable=False)
    views: Mapped[int] = mapped_column(default=0, nullable=False)
    likes: Mapped[int] = mapped_column(default=0, nullable=False)
    comments: Mapped[int] = mapped_column(default=0, nullable=False)
    shares: Mapped[int] = mapped_column(default=0, nullable=False)
    saves: Mapped[int] = mapped_column(default=0, nullable=False)
    engagement_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )
