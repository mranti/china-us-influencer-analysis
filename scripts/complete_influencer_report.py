#!/usr/bin/env python3
"""
完整网红数据报告生成器
Complete Influencer Report Generator

包含:
- 订阅数、浏览量、粉丝数
- 前10热门视频/帖子详细数据
- 标题、观看量、点赞数、评论数
- 总体方向和政治倾向
- 跨平台对比分析

作者: OpenClaw
"""

import os
import sys
import json
import ssl
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

os.environ['PATH'] = '/Users/olivia/.local/bin:' + os.environ.get('PATH', '')

OUTPUT_DIR = ".."
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', 'AIzaSyAiSo5FPoUbLkird3MgsM8GnBXY_XEsMAo')


# ============== 数据类 ==============
@dataclass
class PostData:
    """帖子/视频数据"""
    title: str
    content: str = ""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    published_at: str = ""
    url: str = ""
    thumbnail: str = ""
    platform: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PlatformData:
    """平台数据"""
    platform: str
    status: str  # success, estimated, error
    followers: int = 0
    total_views: int = 0
    total_likes: int = 0
    posts_count: int = 0
    engagement_rate: float = 0.0
    top_posts: List[PostData] = field(default_factory=list)
    recent_posts: List[PostData] = field(default_factory=list)
    error_message: str = ""
    note: str = ""

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['top_posts'] = [p.to_dict() for p in self.top_posts]
        result['recent_posts'] = [p.to_dict() for p in self.recent_posts]
        return result


@dataclass
class InfluencerReport:
    """网红完整报告"""
    name: str
    real_name: str
    category: str
    political_leaning: str
    direction: str
    platforms: Dict[str, PlatformData]
    total_followers: int = 0
    total_views: int = 0
    influence_score: float = 0.0
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()
        self.calculate_totals()

    def calculate_totals(self):
        """计算总数据"""
        self.total_followers = sum(
            p.followers for p in self.platforms.values()
            if p.status in ['success', 'estimated']
        )
        self.total_views = sum(
            p.total_views for p in self.platforms.values()
            if p.status in ['success', 'estimated']
        )

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'real_name': self.real_name,
            'category': self.category,
            'political_leaning': self.political_leaning,
            'direction': self.direction,
            'total_followers': self.total_followers,
            'total_views': self.total_views,
            'influence_score': self.influence_score,
            'generated_at': self.generated_at,
            'platforms': {k: v.to_dict() for k, v in self.platforms.items()}
        }


# ============== 网红配置 ==============
INFLUENCERS_CONFIG = {
    "MKBHD": {
        "name": "MKBHD",
        "real_name": "Marques Brownlee",
        "category": "科技评测",
        "political_leaning": "科技自由主义 / 温和左派",
        "direction": "消费电子产品评测，科技趋势分析，关注科技与社会交叉议题",
        "youtube_channel": "UCBJycsmduvYEL83R_U4JriQ",
        "instagram_handle": "mkbhd",
        "tiktok_handle": "mkbhd",
        "twitter_handle": "MKBHD"
    },
    "MrBeast": {
        "name": "MrBeast",
        "real_name": "Jimmy Donaldson",
        "category": "娱乐/慈善",
        "political_leaning": "商业中立 / 温和中间派",
        "direction": "极限挑战视频，大规模慈善活动，关注气候变化和饥饿问题",
        "youtube_channel": "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "instagram_handle": "mrbeast",
        "tiktok_handle": "mrbeast",
        "twitter_handle": "MrBeast"
    },
    "JoeRogan": {
        "name": "Joe Rogan Experience",
        "real_name": "Joe Rogan",
        "category": "播客/时政",
        "political_leaning": "自由意志主义 / 文化自由主义",
        "direction": "长篇访谈播客，涵盖政治、文化、健康、UF0等多元话题，观点偏向反建制",
        "youtube_channel": "UCzQUP1qoWDoEbmsQxvdjxgQ",
        "instagram_handle": "joerogan",
        "tiktok_handle": "joerogan",
        "twitter_handle": "joerogan",
        "has_podcast": True
    },
    "李子柒": {
        "name": "李子柒",
        "real_name": "李佳佳",
        "category": "传统文化/生活方式",
        "political_leaning": "文化输出/官方认可的中性立场",
        "direction": "中国传统美食与手工艺，田园生活方式，被官方媒体认可的文化传播者",
        "bilibili_uid": "19577966",
        "weibo_estimate": 27500000,
        "douyin_estimate": 49000000
    },
    "麻薯波比": {
        "name": "麻薯波比",
        "real_name": "未知",
        "category": "知识/历史/军事",
        "political_leaning": "民族主义/温和建制派",
        "direction": "国际局势分析，军事历史科普，地缘政治评论，观点偏向中国立场",
        "bilibili_uid": "703186600",
        "weibo_estimate": 790000,
        "douyin_estimate": 3800000
    }
}


# ============== 平台抓取器 ==============
class YouTubeFetcher:
    """YouTube数据获取"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def fetch(self, channel_id: str) -> PlatformData:
        """获取完整YouTube数据"""
        print(f"    📺 YouTube...", end=" ")

        try:
            # 获取频道信息
            url = f"{self.base_url}/channels?part=statistics,snippet,contentDetails&id={channel_id}&key={self.api_key}"
            req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            if not data.get('items'):
                raise Exception("Channel not found")

            channel = data['items'][0]
            stats = channel['statistics']
            snippet = channel['snippet']
            content = channel['contentDetails']

            followers = int(stats.get('subscriberCount', 0))
            total_views = int(stats.get('viewCount', 0))
            video_count = int(stats.get('videoCount', 0))

            # 获取最近视频
            uploads_id = content['relatedPlaylists']['uploads']
            videos = self._fetch_videos(uploads_id)

            # 计算互动率
            avg_views = sum(v.views for v in videos[:10]) / min(10, len(videos)) if videos else 0
            engagement_rate = (avg_views / followers * 100) if followers > 0 else 0

            print(f"✅ {followers:,} subscribers, {len(videos)} videos fetched")

            return PlatformData(
                platform="youtube",
                status="success",
                followers=followers,
                total_views=total_views,
                posts_count=video_count,
                engagement_rate=round(engagement_rate, 2),
                top_posts=sorted(videos, key=lambda x: x.views, reverse=True)[:10],
                recent_posts=videos[:10]
            )

        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return PlatformData(
                platform="youtube",
                status="error",
                error_message=str(e)
            )

    def _fetch_videos(self, playlist_id: str) -> List[PostData]:
        """获取视频列表"""
        videos = []

        try:
            # 获取播放列表
            url = f"{self.base_url}/playlistItems?part=snippet,contentDetails&playlistId={playlist_id}&maxResults=20&key={self.api_key}"
            req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            items = data.get('items', [])
            video_ids = [item['contentDetails']['videoId'] for item in items]

            # 批量获取视频统计
            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i+50]
                ids_str = ','.join(batch)

                stats_url = f"{self.base_url}/videos?part=statistics&id={ids_str}&key={self.api_key}"
                stats_req = urllib.request.Request(stats_url)

                with urllib.request.urlopen(stats_req, timeout=15) as response:
                    stats_data = json.loads(response.read().decode('utf-8'))

                stats_map = {v['id']: v['statistics'] for v in stats_data.get('items', [])}

                for item in items:
                    vid = item['contentDetails']['videoId']
                    snippet = item['snippet']
                    stats = stats_map.get(vid, {})

                    videos.append(PostData(
                        title=snippet.get('title', ''),
                        views=int(stats.get('viewCount', 0)),
                        likes=int(stats.get('likeCount', 0)),
                        comments=int(stats.get('commentCount', 0)),
                        published_at=snippet.get('publishedAt', ''),
                        url=f"https://youtube.com/watch?v={vid}",
                        thumbnail=snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        platform="youtube"
                    ))

        except Exception as e:
            print(f"Video fetch error: {e}")

        return videos


class InstagramFetcher:
    """Instagram数据获取"""

    def fetch(self, username: str) -> PlatformData:
        """获取Instagram数据"""
        print(f"    📷 Instagram...", end=" ")

        try:
            import instaloader
            L = instaloader.Instaloader(
                quiet=True,
                download_pictures=False,
                download_videos=False,
                save_metadata=False
            )
            profile = instaloader.Profile.from_username(L.context, username)

            followers = profile.followers
            posts_count = profile.mediacount

            # 获取最近帖子
            posts = []
            total_likes = 0
            total_comments = 0

            for i, post in enumerate(profile.get_posts()):
                if i >= 10:
                    break

                posts.append(PostData(
                    title=post.caption[:100] if post.caption else "",
                    content=post.caption[:500] if post.caption else "",
                    views=post.video_view_count if post.is_video else post.likes,
                    likes=post.likes,
                    comments=post.comments,
                    published_at=str(post.date),
                    url=f"https://instagram.com/p/{post.shortcode}",
                    thumbnail=post.url,
                    platform="instagram"
                ))

                total_likes += post.likes
                total_comments += post.comments

            engagement_rate = ((total_likes + total_comments) / followers * 100) if followers > 0 else 0

            print(f"✅ {followers:,} followers, {len(posts)} posts")

            return PlatformData(
                platform="instagram",
                status="success",
                followers=followers,
                total_likes=total_likes,
                posts_count=posts_count,
                engagement_rate=round(engagement_rate, 2),
                top_posts=sorted(posts, key=lambda x: x.likes, reverse=True),
                recent_posts=posts
            )

        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return PlatformData(
                platform="instagram",
                status="error",
                error_message=str(e)
            )


class TikTokFetcher:
    """TikTok数据获取"""

    def fetch(self, username: str) -> PlatformData:
        """获取TikTok数据"""
        print(f"    🎵 TikTok...", end=" ")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.tiktok.com/'
            }
            url = f"https://www.tiktok.com/@{username}"
            req = urllib.request.Request(url, headers=headers)
            context = ssl.create_default_context()

            with urllib.request.urlopen(req, timeout=10, context=context) as response:
                html = response.read().decode('utf-8', errors='ignore')

            # 查找粉丝数
            followers_match = re.search(r'"followerCount":(\d+)', html)
            followers = int(followers_match.group(1)) if followers_match else 0

            # 查找点赞数
            likes_match = re.search(r'"heartCount":(\d+)', html)
            total_likes = int(likes_match.group(1)) if likes_match else 0

            print(f"✅ {followers:,} followers")

            return PlatformData(
                platform="tiktok",
                status="success",
                followers=followers,
                total_likes=total_likes,
                note="TikTok不公开详细视频数据"
            )

        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return PlatformData(
                platform="tiktok",
                status="error",
                error_message=str(e)
            )


class BilibiliFetcher:
    """Bilibili数据获取"""

    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://space.bilibili.com'
        }

    def fetch(self, uid: str) -> PlatformData:
        """获取Bilibili数据"""
        print(f"    📺 Bilibili...", end=" ")

        try:
            # 获取用户信息
            url = f"https://api.bilibili.com/x/web-interface/card?mid={uid}"
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req, timeout=15, context=self.ssl_context) as r:
                data = json.loads(r.read().decode('utf-8'))

            if data.get("code") != 0:
                raise Exception("API error")

            card = data["data"]["card"]
            followers = card.get("fans", 0)
            total_likes = card.get("likes", 0)

            # 获取视频
            videos = self._fetch_videos(uid)
            total_views = sum(v.views for v in videos)

            engagement_rate = (total_views / followers * 0.1) if followers > 0 else 0

            print(f"✅ {followers:,} fans, {len(videos)} videos")

            return PlatformData(
                platform="bilibili",
                status="success",
                followers=followers,
                total_views=total_views,
                total_likes=total_likes,
                posts_count=len(videos),
                engagement_rate=round(engagement_rate, 2),
                top_posts=sorted(videos, key=lambda x: x.views, reverse=True)[:10],
                recent_posts=videos[:10]
            )

        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return PlatformData(
                platform="bilibili",
                status="error",
                error_message=str(e)
            )

    def _fetch_videos(self, uid: str) -> List[PostData]:
        """获取视频列表"""
        videos = []

        try:
            url = "https://api.bilibili.com/x/space/arc/search"
            params = {"mid": uid, "ps": 20, "pn": 1, "order": "pubdate"}
            query = f"{url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(query, headers=self.headers)

            with urllib.request.urlopen(req, timeout=15, context=self.ssl_context) as r:
                data = json.loads(r.read().decode('utf-8'))

            if data.get("code") == 0:
                vlist = data["data"]["list"]["vlist"]

                for v in vlist:
                    videos.append(PostData(
                        title=v.get("title", ""),
                        views=v.get("play", 0),
                        likes=v.get("like", 0),
                        comments=v.get("comment", 0),
                        published_at=str(v.get("created", "")),
                        url=f"https://bilibili.com/video/{v.get('bvid', '')}",
                        thumbnail=v.get("pic", ""),
                        platform="bilibili"
                    ))

        except Exception as e:
            print(f"Video fetch error: {e}")

        return videos


# ============== 主报告生成器 ==============
class CompleteReportGenerator:
    """完整报告生成器"""

    def __init__(self):
        self.yt = YouTubeFetcher(YOUTUBE_API_KEY)
        self.ig = InstagramFetcher()
        self.tt = TikTokFetcher()
        self.bl = BilibiliFetcher()
        self.reports: List[InfluencerReport] = []

    def generate_us_reports(self):
        """生成美国网红报告"""
        print("="*70)
        print("🇺🇸 生成美国网红完整报告")
        print("="*70)

        for key in ["MKBHD", "MrBeast", "JoeRogan"]:
            config = INFLUENCERS_CONFIG[key]
            print(f"\n🎯 {config['name']}")
            print("-"*70)

            platforms = {}

            # YouTube (详细数据)
            if config.get('youtube_channel'):
                platforms['youtube'] = self.yt.fetch(config['youtube_channel'])
                time.sleep(0.5)

            # Instagram
            if config.get('instagram_handle'):
                platforms['instagram'] = self.ig.fetch(config['instagram_handle'])
                time.sleep(2)

            # TikTok
            if config.get('tiktok_handle'):
                platforms['tiktok'] = self.tt.fetch(config['tiktok_handle'])
                time.sleep(1)

            # Twitter估算
            if config.get('twitter_handle'):
                platforms['twitter'] = PlatformData(
                    platform="twitter",
                    status="estimated",
                    note="Twitter/X已封锁所有免费API"
                )
                print(f"    🐦 Twitter... ⚠️ 估算 (API被封)")

            # Podcast估算
            if config.get('has_podcast'):
                platforms['podcast'] = PlatformData(
                    platform="podcast",
                    status="estimated",
                    followers=11000000,
                    note="Spotify独家数据"
                )
                print(f"    🎙️  Podcast... ⚠️ 估算 (1100万听众)")

            report = InfluencerReport(
                name=config['name'],
                real_name=config['real_name'],
                category=config['category'],
                political_leaning=config['political_leaning'],
                direction=config['direction'],
                platforms=platforms
            )

            self.reports.append(report)

    def generate_cn_reports(self):
        """生成中国网红报告"""
        print("\n" + "="*70)
        print("🇨🇳 生成中国网红完整报告")
        print("="*70)

        for key in ["李子柒", "麻薯波比"]:
            config = INFLUENCERS_CONFIG[key]
            print(f"\n🎯 {config['name']}")
            print("-"*70)

            platforms = {}

            # Bilibili
            if config.get('bilibili_uid'):
                platforms['bilibili'] = self.bl.fetch(config['bilibili_uid'])
                time.sleep(1)

            # 其他平台估算
            for platform_name, estimate_key in [
                ('weibo', 'weibo_estimate'),
                ('douyin', 'douyin_estimate')
            ]:
                if config.get(estimate_key):
                    platforms[platform_name] = PlatformData(
                        platform=platform_name,
                        status="estimated",
                        followers=config[estimate_key],
                        note="免费方法失败，使用行业估算"
                    )
                    print(f"    ⚠️  {platform_name}: {config[estimate_key]:,} (估算)")

            report = InfluencerReport(
                name=config['name'],
                real_name=config['real_name'],
                category=config['category'],
                political_leaning=config['political_leaning'],
                direction=config['direction'],
                platforms=platforms
            )

            self.reports.append(report)

    def save_text_report(self):
        """保存文本报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{OUTPUT_DIR}/data/reports/COMPLETE_INFLUENCER_REPORT_{timestamp}.txt"

        lines = []
        lines.append("="*80)
        lines.append("📊 网红完整数据报告")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("="*80)
        lines.append("")

        for report in self.reports:
            lines.append("="*80)
            lines.append(f"🎯 {report.name} ({report.real_name})")
            lines.append("="*80)
            lines.append(f"类别: {report.category}")
            lines.append(f"政治倾向: {report.political_leaning}")
            lines.append(f"内容方向: {report.direction}")
            lines.append(f"总粉丝: {report.total_followers:,}")
            lines.append(f"总浏览: {report.total_views:,}")
            lines.append("")

            for platform_name, platform_data in report.platforms.items():
                icon = "✅" if platform_data.status == "success" else "⚠️"
                lines.append(f"{icon} {platform_name.upper()}")
                lines.append(f"   粉丝: {platform_data.followers:,}")
                lines.append(f"   浏览: {platform_data.total_views:,}")

                if platform_data.top_posts:
                    lines.append(f"\n   📹 前10热门内容:")
                    for i, post in enumerate(platform_data.top_posts[:10], 1):
                        lines.append(f"      {i}. {post.title[:60]}...")
                        lines.append(f"         👁️ {post.views:,}  👍 {post.likes:,}  💬 {post.comments:,}")

                lines.append("")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"\n✅ 报告已保存: {filename}")
        return filename

    def save_json_report(self):
        """保存JSON报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{OUTPUT_DIR}/data/json/COMPLETE_INFLUENCER_DATA_{timestamp}.json"

        data = {
            "generated_at": datetime.now().isoformat(),
            "influencers": [r.to_dict() for r in self.reports]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ JSON已保存: {filename}")
        return filename

    def run(self):
        """运行完整报告生成"""
        self.generate_us_reports()
        self.generate_cn_reports()

        text_file = self.save_text_report()
        json_file = self.save_json_report()

        print("\n" + "="*70)
        print("✅ 完整报告生成完成!")
        print("="*70)
        print(f"📄 文本报告: {text_file}")
        print(f"📊 JSON数据: {json_file}")


def main():
    print("="*70)
    print("🚀 网红完整数据报告生成器")
    print("="*70)
    print("包含: 订阅数、浏览量、前10热门视频/帖子、评论数、政治倾向")
    print("="*70)

    generator = CompleteReportGenerator()
    generator.run()


if __name__ == "__main__":
    main()
