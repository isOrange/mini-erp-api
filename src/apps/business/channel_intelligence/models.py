from datetime import datetime

from sqlalchemy import DateTime, String
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