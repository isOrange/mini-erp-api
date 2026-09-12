from pydantic import BaseModel


class ChannelSummaryRead(BaseModel):
    """渠道看板总览数据。"""

    shop_count: int
    account_count: int
    video_count: int
    total_views: int
    median_views: float
    average_duration_seconds: float


class ShopSummaryRead(BaseModel):
    """店铺汇总数据。"""

    shop: str
    account_count: int
    video_count: int
    total_views: int


class AccountSummaryRead(BaseModel):
    """账号汇总数据。"""

    account: str
    shop: str
    video_count: int
    total_views: int
    median_views: float
    engagement_rate: float | None = None


class VideoRead(BaseModel):
    """视频明细数据。"""

    shop: str
    account: str
    video_title: str
    video_url: str
    published_at: str
    duration_seconds: int
    views: int
    likes: int
    comments: int
    shares: int
    saves: int
    engagement_rate: float | None = None


class ContentSignalRead(BaseModel):
    """内容信号数据。"""

    top_view_video: VideoRead | None = None
    top_engagement_video: VideoRead | None = None
    latest_video: VideoRead | None = None
    average_duration_seconds: float


class VideoListRead(BaseModel):
    """视频列表分页结果。"""

    total: int
    items: list[VideoRead]


class FilterOptionsRead(BaseModel):
    """看板筛选项。"""

    shops: list[str]
    accounts: list[str]


class ChannelDashboardRead(BaseModel):
    """渠道看板首页数据。"""

    summary: ChannelSummaryRead
    shops: list[ShopSummaryRead]
    accounts: list[AccountSummaryRead]
    signals: ContentSignalRead


class ChannelSourceRead(BaseModel):
    """渠道账号数据源返回模型。"""

    id: int
    shop: str
    account: str
    source_url: str
    is_active: bool
    last_collected_at: str | None = None


class ChannelSourceCreate(BaseModel):
    """渠道账号数据源创建入参。"""

    shop: str
    account: str
    source_url: str
    is_active: bool = True


class CollectionRunRead(BaseModel):
    """采集任务执行记录。"""

    id: int
    source_id: int
    status: str
    collected_count: int
    error_message: str | None = None
