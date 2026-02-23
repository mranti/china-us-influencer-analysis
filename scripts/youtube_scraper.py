#!/usr/bin/env python3
"""
YouTube Scraper - 使用 YouTube Data API v3
需要: export YOUTUBE_API_KEY='your_api_key'
安装依赖: pip install google-api-python-client
"""

import os
import sys
import json
import re
from datetime import datetime

try:
    from googleapiclient.discovery import build
except ImportError:
    print("请先安装 google-api-python-client: pip install google-api-python-client")
    sys.exit(1)


def get_api_key():
    """从环境变量获取 API Key"""
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("错误: 请设置环境变量 YOUTUBE_API_KEY")
        print("例如: export YOUTUBE_API_KEY='your_api_key'")
        sys.exit(1)
    return api_key


def extract_video_id(url):
    """从各种 YouTube URL 格式中提取 video ID"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'  # 直接是 video ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_info(video_id, api_key):
    """使用 YouTube Data API 获取视频信息"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    try:
        # 获取视频详情
        video_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()
        
        if not video_response['items']:
            print(f"错误: 找不到视频 ID: {video_id}")
            return None
        
        video = video_response['items'][0]
        snippet = video['snippet']
        content = video['contentDetails']
        stats = video['statistics']
        
        # 获取频道信息
        channel_id = snippet.get('channelId', '')
        channel_title = snippet.get('channelTitle', 'N/A')
        
        result = {
            'video_id': video_id,
            'title': snippet.get('title', 'N/A'),
            'description': snippet.get('description', 'N/A'),
            'published_at': snippet.get('publishedAt', 'N/A'),
            'channel_id': channel_id,
            'channel_title': channel_title,
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId', 'N/A'),
            'duration': content.get('duration', 'N/A'),
            'dimension': content.get('dimension', 'N/A'),
            'definition': content.get('definition', 'N/A'),
            'caption': content.get('caption', 'false'),
            'view_count': int(stats.get('viewCount', 0)),
            'like_count': int(stats.get('likeCount', 0)) if 'likeCount' in stats else 0,
            'comment_count': int(stats.get('commentCount', 0)) if 'commentCount' in stats else 0,
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', 'N/A')
        }
        
        return result
        
    except Exception as e:
        print(f"错误: API 请求失败 - {e}")
        return None


def format_duration(iso_duration):
    """将 ISO 8601 时长格式转换为可读格式"""
    # PT4M13S -> 4:13
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if not match:
        return iso_duration
    
    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


def format_video_info(info):
    """格式化视频信息用于显示"""
    if not info:
        return "无法获取视频信息"
    
    duration_formatted = format_duration(info['duration']) if info['duration'] != 'N/A' else 'N/A'
    
    output = []
    output.append("=" * 60)
    output.append(f"🎬 标题: {info['title']}")
    output.append(f"👤 频道: {info['channel_title']}")
    output.append(f"⏱️  时长: {duration_formatted} ({info['duration']})")
    output.append(f"📺 画质: {info['definition'].upper()}")
    output.append(f"👁️  观看: {info['view_count']:,}")
    output.append(f"👍 点赞: {info['like_count']:,}")
    output.append(f"💬 评论: {info['comment_count']:,}")
    output.append(f"📅 发布: {info['published_at']}")
    output.append(f"🔗 链接: {info['url']}")
    output.append(f"🆔 ID: {info['video_id']}")
    
    if info['tags']:
        output.append(f"🏷️  标签: {', '.join(info['tags'][:10])}")  # 只显示前10个标签
    
    output.append("=" * 60)
    output.append("\n📝 简介:")
    # 限制简介长度
    desc = info['description'][:500] + "..." if len(info['description']) > 500 else info['description']
    output.append(desc)
    
    return '\n'.join(output)


def save_to_json(info, filename=None):
    """保存视频信息到 JSON 文件"""
    if not filename:
        filename = f"../data/json/youtube_{info['video_id']}_info.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存到: {filename}")
    return filename


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
用法:
    export YOUTUBE_API_KEY='your_api_key'
    python3 youtube_scraper.py <YouTube_URL_or_Video_ID>
    
示例:
    export YOUTUBE_API_KEY='AIzaSy...'
    python3 youtube_scraper.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    python3 youtube_scraper.py dQw4w9WgXcQ
        """)
        sys.exit(1)
    
    api_key = get_api_key()
    url_or_id = sys.argv[1]
    
    video_id = extract_video_id(url_or_id)
    if not video_id:
        print(f"错误: 无法从 '{url_or_id}' 提取视频 ID")
        sys.exit(1)
    
    print(f"🔍 正在获取视频信息: {video_id}")
    print(f"🔑 使用 API Key: {api_key[:15]}...")
    print("-" * 60)
    
    info = get_video_info(video_id, api_key)
    
    if info:
        print(format_video_info(info))
        
        # 自动保存 JSON
        json_file = save_to_json(info)
        print(f"\n💾 JSON 数据已保存: {json_file}")
    else:
        print("❌ 获取视频信息失败")
        sys.exit(1)


if __name__ == "__main__":
    main()