import json
import subprocess
import sys

ACCOUNT = "wardrobepicked"
PLAYLIST_END = 5


def fetch_tiktok_account(account: str) -> dict:
    """调用 yt-dlp 抓取一个 TikTok 账号的视频列表。"""

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

    return json.loads(result.stdout)


def normalize_video(item: dict) -> dict:
    """把 yt-dlp 返回的原始视频数据转换成我们系统统一使用的格式。"""

    thumbnails = item.get("thumbnails") or []
    thumbnail_url = thumbnails[0]["url"] if thumbnails else None

    return {
        "account": item.get("uploader"),
        "video_id": item.get("id"),
        "video_url": item.get("url"),
        "title": item.get("title"),
        "published_at": item.get("timestamp"),
        "duration_seconds": item.get("duration"),
        "views": item.get("view_count") or 0,
        "likes": item.get("like_count") or 0,
        "comments": item.get("comment_count") or 0,
        "shares": item.get("repost_count") or 0,
        "saves": item.get("save_count") or 0,
        "thumbnail_url": thumbnail_url,
    }


def main() -> None:
    """脚本入口：抓取账号视频，并打印标准化后的结果。"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/spike_tiktok_source.py <account>")
        return

    account = sys.argv[1].removeprefix("@")

    data = fetch_tiktok_account(account)
    videos = [normalize_video(item) for item in data.get("entries", [])]

    print(json.dumps(videos, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
