import json
import subprocess

from src.apps.business.channel_intelligence.schemas import VideoRead

PLAYLIST_END = 5


def collect_tiktok_account_videos(account: str, shop: str) -> list[VideoRead]:
    """
    通过 yt-dlp 采集一个 TikTok 账号主页的视频列表。

    Args:
        account: TikTok 账号名，不包含 @。
        shop: 账号所属店铺。

    Returns:
        标准化后的视频列表。
    """
    url = f"https://www.tiktok.com/@{account}"

    command = [
        ".venv/Scripts/python.exe",
        "-m",
        "yt_dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--playlist-end",
        str(PLAYLIST_END),
        url,
    ]

    result = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )

    data = json.loads(result.stdout)

    return [
        normalize_tiktok_video(item=item, shop=shop)
        for item in data.get("entries", [])
    ]


def normalize_tiktok_video(item: dict, shop: str) -> VideoRead:
    """
    将 yt-dlp 原始视频数据转换成渠道看板内部使用的视频结构。

    Args:
        item: yt-dlp 返回的单条视频原始数据。
        shop: 视频所属店铺。

    Returns:
        标准化后的视频数据。
    """
    thumbnails = item.get("thumbnails") or []
    thumbnail_url = thumbnails[0]["url"] if thumbnails else None

    views = item.get("view_count") or 0
    likes = item.get("like_count") or 0
    comments = item.get("comment_count") or 0
    shares = item.get("repost_count") or 0
    saves = item.get("save_count") or 0
    engagement_count = likes + comments + shares

    return VideoRead(
        shop=shop,
        account=item.get("uploader") or "",
        video_title=item.get("title") or "",
        video_url=item.get("url") or "",
        thumbnail_url=thumbnail_url,
        published_at=str(item.get("timestamp") or ""),
        duration_seconds=item.get("duration") or 0,
        views=views,
        likes=likes,
        comments=comments,
        shares=shares,
        saves=saves,
        engagement_rate=engagement_count / views if views > 0 else None,
    )
