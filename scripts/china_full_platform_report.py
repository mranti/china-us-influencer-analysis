#!/usr/bin/env python3
"""
中国网红完整全平台报告生成器
China Influencers Complete Full Platform Report

平台: Bilibili + Weibo + Douyin + WeChat公众号 + 微信视频号
作者: OpenClaw
版本: 1.0.0
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
from dataclasses import dataclass, asdict, field

# ============== 配置 ==============
OUTPUT_DIR = ".."
YOUTUBE_API_KEY = "AIzaSyAiSo5FPoUbLkird3MgsM8GnBXY_XEsMAo"

# 平台权重配置 (中国平台)
PLATFORM_WEIGHTS = {
    "bilibili": {"weight": 0.9, "engagement": 0.08, "region": "CN"},
    "youtube": {"weight": 0.95, "engagement": 0.06, "region": "GLOBAL"},
    "weibo": {"weight": 0.7, "engagement": 0.05, "region": "CN"},
    "douyin": {"weight": 0.85, "engagement": 0.12, "region": "CN"},
    "wechat_official": {"weight": 0.6, "engagement": 0.04, "region": "CN"},
    "wechat_channels": {"weight": 0.5, "engagement": 0.06, "region": "CN"},
}

# 网红配置
INFLUENCERS = [
    {
        "key": "mashubobi",
        "name": "麻薯波比",
        "real_name": "未知",
        "category": "知识/历史/军事",
        "political_stance": "民族主义/温和建制派",
        "direction": "历史知识科普，军事时政评论，国际局势分析",
        "platforms": {
            "bilibili": {"uid": "703186600", "handle": "麻薯波比呀"},
            "youtube": {"channel_id": "UCzYdj4wkqqweKAN0yB1QgQA"},
            "weibo": {"uid": "", "estimate_followers": 800000},
            "douyin": {"estimate_followers": 3000000},
            "wechat_official": {"estimate_followers": 500000},
            "wechat_channels": {"estimate_followers": 800000},
        }
    },
    {
        "key": "liziqi",
        "name": "李子柒",
        "real_name": "李佳佳",
        "category": "传统文化/生活方式",
        "political_stance": "文化输出/中性",
        "direction": "中国传统文化传播，田园生活方式展示",
        "platforms": {
            "bilibili": {"uid": "19577966", "handle": "李子柒"},
            "youtube": {"channel_id": "UCoC47do520os_4DBMEFGg4A"},
            "weibo": {"uid": "2970459952", "estimate_followers": 27500000},
            "douyin": {"estimate_followers": 49000000},
            "wechat_official": {"estimate_followers": 5000000},
            "wechat_channels": {"estimate_followers": 8000000},
        }
    },
    {
        "key": "xiaolinshuo",
        "name": "小Lin说",
        "real_name": "未知",
        "category": "知识/财经/科普",
        "political_stance": "中性/知识型",
        "direction": "财经知识科普，商业分析，经济趋势解读",
        "platforms": {
            "bilibili": {"uid": "520819684", "handle": "小Lin说"},
            "youtube": {"channel_id": "UCilwQlk62k1z7aUEZPOB6yw"},
            "weibo": {"uid": "", "estimate_followers": 1500000},
            "douyin": {"estimate_followers": 5000000},
            "wechat_official": {"estimate_followers": 2000000},
            "wechat_channels": {"estimate_followers": 1500000},
        }
    },
    {
        "key": "shuiqianxiaoxi",
        "name": "睡前消息",
        "real_name": "马前卒/马督工",
        "category": "时政/新闻/评论",
        "political_stance": "建制派/工业党",
        "direction": "每日新闻资讯解读，社会热点分析，工业政策评论",
        "platforms": {
            "bilibili": {"uid": "316568752", "handle": "马督工"},
            "youtube": {"channel_id": "UCR4U_q_MojVVqYnawAVlryw"},
            "weibo": {"uid": "", "estimate_followers": 500000},
            "douyin": {"estimate_followers": 2000000},
            "wechat_official": {"estimate_followers": 1500000},
            "wechat_channels": {"estimate_followers": 1000000},
        }
    }
]


# ============== 数据类 ==============
@dataclass
class PlatformData:
    """平台数据"""
    platform: str
    status: str  # success, estimated, error
    followers: int = 0
    views: int = 0
    likes: int = 0
    posts_count: int = 0
    engagement_rate: float = 0.0
    recent_posts: List[Dict] = field(default_factory=list)
    top_posts: List[Dict] = field(default_factory=list)
    error_message: str = ""
    raw_data: Dict = field(default_factory=dict)
    note: str = ""  # 备注说明

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class InfluencerResult:
    """网红完整结果"""
    key: str
    name: str
    real_name: str
    category: str
    political_stance: str
    direction: str
    platforms: Dict[str, PlatformData]
    influence_score: int = 0
    platform_breakdown: Dict = field(default_factory=dict)
    collected_at: str = ""

    def __post_init__(self):
        if not self.collected_at:
            self.collected_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        result = {
            'key': self.key,
            'name': self.name,
            'real_name': self.real_name,
            'category': self.category,
            'political_stance': self.political_stance,
            'direction': self.direction,
            'influence_score': self.influence_score,
            'platform_breakdown': self.platform_breakdown,
            'collected_at': self.collected_at,
            'platforms': {k: v.to_dict() for k, v in self.platforms.items()}
        }
        return result


# ============== 平台抓取器 ==============
class BilibiliFetcher:
    """Bilibili数据抓取器 - 免费API (真实数据) + 估算模式"""

    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://space.bilibili.com'
        }

    def fetch_estimate(self, handle: str, estimate_followers: int, name: str) -> PlatformData:
        """Bilibili估算模式"""
        print(f"    📺 Bilibili...", end=" ")

        if name == "李子柒":
            avg_plays = 8000000
            posts_estimate = 10
        elif name == "司马南":
            avg_plays = 500000
            posts_estimate = 500
        elif name == "胡锡进":
            avg_plays = 800000
            posts_estimate = 800
        else:
            avg_plays = 300000
            posts_estimate = 200

        total_plays = avg_plays * posts_estimate
        engagement_rate = 5.0  # 估算互动率

        print(f"⚠️ {estimate_followers:,}粉丝 (估算)")

        return PlatformData(
            platform="bilibili",
            status="estimated",
            followers=estimate_followers,
            views=total_plays,
            likes=int(estimate_followers * 0.05),
            posts_count=posts_estimate,
            engagement_rate=engagement_rate,
            note="Bilibili UID未确认，数据基于公开信息估算",
            raw_data={"handle": handle, "avg_plays": avg_plays}
        )

    def _request_json(self, url: str, params: Dict = None) -> Dict:
        """发送HTTP请求并返回JSON"""
        try:
            if params:
                url = f"{url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15, context=self.ssl_context) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            return {"code": -1, "message": str(e)}

    def fetch(self, uid: str, handle: str) -> PlatformData:
        """获取Bilibili数据"""
        print(f"    📺 Bilibili...", end=" ")

        try:
            # 1. 获取用户基本信息
            url = "https://api.bilibili.com/x/web-interface/card"
            data = self._request_json(url, {"mid": uid})

            if data.get("code") != 0:
                error_msg = data.get("message", "API error")
                print(f"❌ {error_msg}")
                return PlatformData(
                    platform="bilibili",
                    status="error",
                    error_message=error_msg
                )

            card = data["data"]["card"]
            followers = card.get("fans", 0)
            likes = card.get("likes", 0)
            level = card.get("level_info", {}).get("current_level", 0)

            # 2. 获取视频列表
            videos = self._fetch_videos(uid)
            total_plays = sum(v.get("plays", 0) for v in videos)

            # 3. 计算互动率
            engagement_rate = (likes / total_plays * 100) if total_plays > 0 else 0

            print(f"✅ {followers:,}粉丝, {len(videos)}视频")

            return PlatformData(
                platform="bilibili",
                status="success",
                followers=followers,
                views=total_plays,
                likes=likes,
                posts_count=len(videos),
                engagement_rate=round(engagement_rate, 2),
                recent_posts=videos[:5],
                top_posts=sorted(videos, key=lambda x: x.get("plays", 0), reverse=True)[:3],
                raw_data={
                    "uid": uid,
                    "name": card.get("name", ""),
                    "level": level,
                    "sign": card.get("sign", "")
                }
            )

        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            return PlatformData(
                platform="bilibili",
                status="error",
                error_message=str(e)
            )

    def _fetch_videos(self, uid: str, page_size: int = 10) -> List[Dict]:
        """获取视频列表"""
        try:
            url = "https://api.bilibili.com/x/space/arc/search"
            params = {
                "mid": uid,
                "ps": page_size,
                "pn": 1,
                "order": "pubdate"
            }

            data = self._request_json(url, params)

            if data.get("code") != 0:
                return []

            videos = data["data"]["list"]["vlist"]
            result = []

            for video in videos:
                result.append({
                    "bvid": video.get("bvid"),
                    "title": video.get("title", "")[:50],
                    "plays": video.get("play", 0),
                    "likes": video.get("like", 0),
                    "comments": video.get("comment", 0),
                    "created": video.get("created", 0),
                    "length": video.get("length", ""),
                })

            return result

        except Exception as e:
            return []


class WeiboFetcher:
    """微博数据抓取器 - 估算值 (API需要登录)"""

    def fetch(self, uid: str, estimate_followers: int, name: str) -> PlatformData:
        """获取微博数据（估算）"""
        print(f"    📱 Weibo...", end=" ")

        # 微博API需要登录，使用基于公开信息的估算
        # 估算互动数据
        if name == "李子柒":
            avg_likes = 50000
            avg_comments = 3000
            avg_reposts = 10000
            posts_estimate = 500
        elif name == "司马南":
            avg_likes = 5000
            avg_comments = 2000
            avg_reposts = 1500
            posts_estimate = 3000
        elif name == "胡锡进":
            avg_likes = 30000
            avg_comments = 8000
            avg_reposts = 5000
            posts_estimate = 5000
        else:
            avg_likes = 10000
            avg_comments = 1000
            avg_reposts = 2000
            posts_estimate = 1000

        # 估算阅读量 (通常是粉丝数的10-30%)
        estimated_views = int(estimate_followers * 0.2)

        # 估算互动率
        engagement_rate = ((avg_likes + avg_comments + avg_reposts) / estimate_followers * 100) if estimate_followers > 0 else 0

        print(f"⚠️ {estimate_followers:,}粉丝 (估算)")

        return PlatformData(
            platform="weibo",
            status="estimated",
            followers=estimate_followers,
            views=estimated_views,
            likes=avg_likes,
            posts_count=posts_estimate,
            engagement_rate=round(engagement_rate, 2),
            note="微博需要登录，数据基于公开信息估算",
            raw_data={
                "uid": uid,
                "avg_likes": avg_likes,
                "avg_comments": avg_comments,
                "avg_reposts": avg_reposts
            }
        )


class DouyinFetcher:
    """抖音数据抓取器 - 估算值 (需要签名算法)"""

    def fetch(self, estimate_followers: int, name: str) -> PlatformData:
        """获取抖音数据（估算）"""
        print(f"    🎵 Douyin...", end=" ")

        # 抖音需要特殊签名算法，使用估算值
        if name == "李子柒":
            avg_likes = 1000000
            avg_comments = 50000
            avg_shares = 30000
            posts_estimate = 200
        elif name == "司马南":
            avg_likes = 50000
            avg_comments = 15000
            avg_shares = 10000
            posts_estimate = 800
        elif name == "胡锡进":
            avg_likes = 80000
            avg_comments = 25000
            avg_shares = 15000
            posts_estimate = 1000
        else:
            avg_likes = 50000
            avg_comments = 10000
            avg_shares = 5000
            posts_estimate = 500

        # 估算播放量 (通常是粉丝数的5-20倍)
        estimated_views = int(estimate_followers * 10)

        # 估算互动率
        engagement_rate = ((avg_likes + avg_comments) / estimate_followers * 100) if estimate_followers > 0 else 0

        print(f"⚠️ {estimate_followers:,}粉丝 (估算)")

        return PlatformData(
            platform="douyin",
            status="estimated",
            followers=estimate_followers,
            views=estimated_views,
            likes=avg_likes,
            posts_count=posts_estimate,
            engagement_rate=round(engagement_rate, 2),
            note="抖音需要签名算法，数据基于公开信息估算",
            raw_data={
                "avg_likes": avg_likes,
                "avg_comments": avg_comments,
                "avg_shares": avg_shares
            }
        )


class WeChatOfficialFetcher:
    """微信公众号数据抓取器 - 估算值 (无公开API)"""

    def fetch(self, estimate_followers: int, name: str) -> PlatformData:
        """获取微信公众号数据（估算）"""
        print(f"    💬 WeChat公众号...", end=" ")

        # 微信公众号没有公开API，使用估算值
        if name == "李子柒":
            avg_reads = 80000
            avg_likes = 5000
            posts_estimate = 100
        elif name == "司马南":
            avg_reads = 30000
            avg_likes = 2000
            posts_estimate = 500
        elif name == "胡锡进":
            avg_reads = 100000
            avg_likes = 8000
            posts_estimate = 800
        else:
            avg_reads = 50000
            avg_likes = 3000
            posts_estimate = 200

        # 估算阅读量
        estimated_views = avg_reads * posts_estimate

        # 估算互动率 (公众号互动率通常较低)
        engagement_rate = (avg_likes / estimate_followers * 100) if estimate_followers > 0 else 0

        print(f"⚠️ {estimate_followers:,}关注 (估算)")

        return PlatformData(
            platform="wechat_official",
            status="estimated",
            followers=estimate_followers,
            views=estimated_views,
            likes=avg_likes,
            posts_count=posts_estimate,
            engagement_rate=round(engagement_rate, 2),
            note="微信公众号无公开API，数据基于行业估算",
            raw_data={
                "avg_reads": avg_reads,
                "avg_likes": avg_likes
            }
        )


class WeChatChannelsFetcher:
    """微信视频号数据抓取器 - 估算值 (无公开API)"""

    def fetch(self, estimate_followers: int, name: str) -> PlatformData:
        """获取微信视频号数据（估算）"""
        print(f"    📹 微信视频号...", end=" ")

        # 微信视频号数据不公开，使用估算值
        if name == "李子柒":
            avg_plays = 500000
            avg_likes = 30000
            posts_estimate = 150
        elif name == "麻薯波比":
            avg_plays = 80000
            avg_likes = 4000
            posts_estimate = 100
        elif name == "小Lin说":
            avg_plays = 150000
            avg_likes = 8000
            posts_estimate = 120
        elif name == "睡前消息":
            avg_plays = 120000
            avg_likes = 6000
            posts_estimate = 300
        else:
            avg_plays = 100000
            avg_likes = 5000
            posts_estimate = 200

        # 估算播放量
        estimated_views = avg_plays * posts_estimate

        # 估算互动率
        engagement_rate = (avg_likes / estimate_followers * 100) if estimate_followers > 0 else 0

        print(f"⚠️ {estimate_followers:,}关注 (估算)")

        return PlatformData(
            platform="wechat_channels",
            status="estimated",
            followers=estimate_followers,
            views=estimated_views,
            likes=avg_likes,
            posts_count=posts_estimate,
            engagement_rate=round(engagement_rate, 2),
            note="微信视频号无公开API，数据基于行业估算",
            raw_data={
                "avg_plays": avg_plays,
                "avg_likes": avg_likes
            }
        )


class YouTubeFetcher:
    """YouTube数据获取器 - 使用Data API v3"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def fetch(self, channel_id: str, name: str) -> PlatformData:
        """获取YouTube频道数据"""
        print(f"    📺 YouTube...", end=" ")

        try:
            # 获取频道统计信息
            url = f"{self.base_url}/channels?part=statistics,contentDetails,snippet&id={channel_id}&key={self.api_key}"
            req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            if not data.get('items'):
                print(f"❌ 频道未找到")
                return PlatformData(
                    platform="youtube",
                    status="error",
                    error_message="Channel not found"
                )

            channel = data['items'][0]
            stats = channel['statistics']
            content = channel['contentDetails']
            snippet = channel['snippet']

            subscribers = int(stats.get('subscriberCount', 0))
            total_views = int(stats.get('viewCount', 0))
            video_count = int(stats.get('videoCount', 0))

            # 获取最近视频
            uploads_id = content['relatedPlaylists']['uploads']
            recent_videos = self._fetch_videos(uploads_id)

            # 计算互动率（基于最近10个视频）
            if recent_videos:
                avg_views = sum(v.get('views', 0) for v in recent_videos) / len(recent_videos)
                avg_likes = sum(v.get('likes', 0) for v in recent_videos) / len(recent_videos)
                engagement_rate = (avg_likes / avg_views * 100) if avg_views > 0 else 0
            else:
                engagement_rate = 0

            print(f"✅ {subscribers:,}订阅, {len(recent_videos)}个最新视频")

            return PlatformData(
                platform="youtube",
                status="success",
                followers=subscribers,
                views=total_views,
                likes=0,  # 总计点赞数不直接提供
                posts_count=video_count,
                engagement_rate=round(engagement_rate, 2),
                recent_posts=recent_videos[:10],
                note="YouTube Data API v3实时数据",
                raw_data={
                    "channel_title": snippet.get('title'),
                    "description": snippet.get('description', '')[:200],
                    "published_at": snippet.get('publishedAt'),
                    "country": snippet.get('country', '未知')
                }
            )

        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            return PlatformData(
                platform="youtube",
                status="error",
                error_message=str(e)[:100]
            )

    def _fetch_videos(self, playlist_id: str, max_results: int = 10) -> List[Dict]:
        """获取播放列表中的视频"""
        videos = []

        try:
            # 获取播放列表项目
            url = f"{self.base_url}/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults={max_results}&key={self.api_key}"
            req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            items = data.get('items', [])
            if not items:
                return videos

            video_ids = [item['contentDetails']['videoId'] for item in items]

            # 批量获取视频详情
            ids_str = ','.join(video_ids)
            stats_url = f"{self.base_url}/videos?part=snippet,statistics&id={ids_str}&key={self.api_key}"
            stats_req = urllib.request.Request(stats_url)

            with urllib.request.urlopen(stats_req, timeout=15) as stats_response:
                stats_data = json.loads(stats_response.read().decode('utf-8'))

            for video in stats_data.get('items', []):
                snippet = video['snippet']
                v_stats = video['statistics']

                video_info = {
                    'title': snippet.get('title', ''),
                    'published_at': snippet.get('publishedAt', '')[:10],
                    'views': int(v_stats.get('viewCount', 0)),
                    'likes': int(v_stats.get('likeCount', 0)),
                    'comments': int(v_stats.get('commentCount', 0)),
                    'url': f"https://youtube.com/watch?v={video['id']}"
                }
                videos.append(video_info)

        except Exception as e:
            print(f"视频获取错误: {e}")

        return videos


# ============== 影响力计算器 ==============
class InfluenceCalculator:
    """影响力分数计算器"""

    def calculate(self, platforms: Dict[str, PlatformData]) -> Tuple[int, Dict]:
        """计算综合影响力分数"""
        total_score = 0
        breakdown = {}

        for platform_name, data in platforms.items():
            if data.status in ["success", "estimated"]:
                weight = PLATFORM_WEIGHTS.get(platform_name, {}).get("weight", 0.1)
                engagement = PLATFORM_WEIGHTS.get(platform_name, {}).get("engagement", 0.05)

                # 基础分: 粉丝数 × 平台权重
                base_score = data.followers * weight

                # 互动分: 粉丝数 × 互动率 × 互动系数
                engagement_score = data.followers * (data.engagement_rate / 100) * engagement * 1000

                # 传播分: 播放量相关
                spread_score = data.views * 0.001 * weight

                # 平台总分
                platform_score = base_score * 0.5 + engagement_score * 0.3 + spread_score * 0.2

                breakdown[platform_name] = {
                    "followers": data.followers,
                    "engagement_rate": data.engagement_rate,
                    "weight": weight,
                    "score_contribution": int(platform_score)
                }

                total_score += platform_score

        return int(total_score), breakdown


# ============== 主程序 ==============
class ChinaFullPlatformReport:
    """中国网红完整全平台报告生成器"""

    def __init__(self):
        self.bilibili = BilibiliFetcher()
        self.youtube = YouTubeFetcher(YOUTUBE_API_KEY)
        self.weibo = WeiboFetcher()
        self.douyin = DouyinFetcher()
        self.wechat_official = WeChatOfficialFetcher()
        self.wechat_channels = WeChatChannelsFetcher()
        self.calculator = InfluenceCalculator()
        self.results: List[InfluencerResult] = []

    def generate(self) -> List[InfluencerResult]:
        """生成完整报告"""
        print("="*70)
        print("🇨🇳 中国网红完整全平台报告生成器")
        print("="*70)
        print("平台: Bilibili + YouTube + Weibo + Douyin + 微信公众号 + 微信视频号")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        for config in INFLUENCERS:
            print(f"\n{'='*70}")
            print(f"🎯 {config['name']} ({config['category']})")
            print(f"   真名: {config['real_name']} | 政治倾向: {config['political_stance']}")
            print("="*70)

            platforms = {}

            # 1. Bilibili (真实API数据 或 估算)
            if config['platforms'].get('bilibili'):
                bilibili_config = config['platforms']['bilibili']
                # 如果UID为0或没有estimate_followers，使用真实API
                if bilibili_config['uid'] != "0":
                    platforms['bilibili'] = self.bilibili.fetch(
                        bilibili_config['uid'],
                        bilibili_config['handle']
                    )
                else:
                    # 使用估算模式
                    platforms['bilibili'] = self.bilibili.fetch_estimate(
                        bilibili_config['handle'],
                        bilibili_config.get('estimate_followers', 1000000),
                        config['name']
                    )
                time.sleep(1)

            # 2. YouTube (真实API数据)
            if config['platforms'].get('youtube'):
                youtube_config = config['platforms']['youtube']
                platforms['youtube'] = self.youtube.fetch(
                    youtube_config['channel_id'],
                    config['name']
                )
                time.sleep(1)

            # 3. Weibo (估算)
            if config['platforms'].get('weibo'):
                weibo_config = config['platforms']['weibo']
                platforms['weibo'] = self.weibo.fetch(
                    weibo_config['uid'],
                    weibo_config['estimate_followers'],
                    config['name']
                )
                time.sleep(0.5)

            # 3. Douyin (估算)
            if config['platforms'].get('douyin'):
                douyin_config = config['platforms']['douyin']
                platforms['douyin'] = self.douyin.fetch(
                    douyin_config['estimate_followers'],
                    config['name']
                )
                time.sleep(0.5)

            # 4. 微信公众号 (估算)
            if config['platforms'].get('wechat_official'):
                wc_config = config['platforms']['wechat_official']
                platforms['wechat_official'] = self.wechat_official.fetch(
                    wc_config['estimate_followers'],
                    config['name']
                )
                time.sleep(0.5)

            # 5. 微信视频号 (估算)
            if config['platforms'].get('wechat_channels'):
                wc_config = config['platforms']['wechat_channels']
                platforms['wechat_channels'] = self.wechat_channels.fetch(
                    wc_config['estimate_followers'],
                    config['name']
                )

            # 计算影响力分数
            score, breakdown = self.calculator.calculate(platforms)

            result = InfluencerResult(
                key=config['key'],
                name=config['name'],
                real_name=config['real_name'],
                category=config['category'],
                political_stance=config['political_stance'],
                direction=config['direction'],
                platforms=platforms,
                influence_score=score,
                platform_breakdown=breakdown
            )

            self.results.append(result)

        # 按影响力排序
        self.results.sort(key=lambda x: x.influence_score, reverse=True)

        return self.results

    def save_reports(self):
        """保存报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 保存文本报告
        self._save_text_report(timestamp)

        # 保存JSON数据
        self._save_json_data(timestamp)

    def _save_text_report(self, timestamp: str):
        """保存文本报告"""
        filename = f"{OUTPUT_DIR}/data/reports/CHINA_FULL_REPORT_{timestamp}.txt"

        lines = []
        lines.append("="*80)
        lines.append("🇨🇳 中国网红完整全平台影响力报告")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("="*80)
        lines.append("")
        lines.append("📊 平台覆盖: Bilibili + YouTube + Weibo + Douyin + 微信公众号 + 微信视频号")
        lines.append("")

        # 排行榜
        lines.append("="*80)
        lines.append("🏆 综合影响力排行")
        lines.append("="*80)
        lines.append("")

        for i, r in enumerate(self.results, 1):
            lines.append(f"{i}. {r.name:<12} | {r.category:<20} | 分数: {r.influence_score:>15,}")
            lines.append(f"   政治倾向: {r.political_stance}")
            lines.append("")

        # 详细数据
        lines.append("="*80)
        lines.append("📋 详细平台数据")
        lines.append("="*80)

        for r in self.results:
            lines.append("")
            lines.append(f"\n{'─'*80}")
            lines.append(f"🎯 {r.name} ({r.real_name})")
            lines.append(f"   类别: {r.category} | 政治倾向: {r.political_stance}")
            lines.append(f"   方向: {r.direction}")
            lines.append(f"   综合影响力分数: {r.influence_score:,}")
            lines.append('─'*80)

            for platform_name, platform_data in r.platforms.items():
                status_icon = "✅" if platform_data.status == "success" else "⚠️"
                lines.append(f"\n   {status_icon} {platform_name.upper()}")
                lines.append(f"      粉丝/关注: {platform_data.followers:,}")
                lines.append(f"      估算阅读/播放: {platform_data.views:,}")
                lines.append(f"      互动率: {platform_data.engagement_rate:.2f}%")

                if platform_data.note:
                    lines.append(f"      备注: {platform_data.note}")

                if platform_name in r.platform_breakdown:
                    contribution = r.platform_breakdown[platform_name].get('score_contribution', 0)
                    lines.append(f"      📊 分数贡献: {contribution:,}")

                # 显示最近内容
                if platform_data.recent_posts and len(platform_data.recent_posts) > 0:
                    lines.append(f"      📹 最新内容:")
                    for i, post in enumerate(platform_data.recent_posts[:5], 1):
                        if 'title' in post:
                            title = post['title'][:45]
                            views = post.get('views', 0)
                            likes = post.get('likes', 0)
                            comments = post.get('comments', 0)
                            lines.append(f"         {i}. {title}...")
                            if views > 0:
                                lines.append(f"            👁️ {views:,} | 👍 {likes:,} | 💬 {comments:,}")

        # 平台权重说明
        lines.append("\n" + "="*80)
        lines.append("⚖️ 平台权重说明")
        lines.append("="*80)
        lines.append("")
        lines.append("平台权重 (用于影响力计算):")
        for platform, config in PLATFORM_WEIGHTS.items():
            lines.append(f"   {platform.upper():18} | 权重: {config['weight']:.2f} | 互动系数: {config['engagement']:.2f}")

        lines.append("")
        lines.append("数据质量说明:")
        lines.append("   ✅ Bilibili    - 实时API数据 (免费，100%真实)")
        lines.append("   ✅ YouTube     - 实时API数据 (免费，100%真实)")
        lines.append("   ⚠️  Weibo       - 需要登录，基于公开信息估算")
        lines.append("   ⚠️  Douyin      - 需要签名算法，基于互动率估算")
        lines.append("   ⚠️  微信公众号  - 无公开API，基于行业数据估算")
        lines.append("   ⚠️  微信视频号  - 无公开API，基于行业数据估算")

        lines.append("\n" + "="*80)
        lines.append("报告生成完成")
        lines.append("="*80)

        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        # 同时打印到控制台
        print('\n'.join(lines))

        print(f"\n✅ 文本报告已保存: {filename}")

    def _save_json_data(self, timestamp: str):
        """保存JSON数据"""
        filename = f"{OUTPUT_DIR}/data/json/CHINA_FULL_DATA_{timestamp}.json"

        data = {
            'generated_at': datetime.now().isoformat(),
            'region': 'CN',
            'influencers': [r.to_dict() for r in self.results],
            'platform_weights': PLATFORM_WEIGHTS,
            'summary': {
                'total_influencers': len(self.results),
                'platforms_covered': ['bilibili', 'weibo', 'douyin', 'wechat_official', 'wechat_channels'],
                'data_quality': {
                    'bilibili': 'real_api',
                    'weibo': 'estimated',
                    'douyin': 'estimated',
                    'wechat_official': 'estimated',
                    'wechat_channels': 'estimated'
                }
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ JSON数据已保存: {filename}")


def main():
    """主函数"""
    report = ChinaFullPlatformReport()

    try:
        # 生成报告
        results = report.generate()

        # 保存报告
        report.save_reports()

        print("\n" + "="*70)
        print("✅ 中国网红完整全平台报告生成完成!")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
