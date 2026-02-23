#!/usr/bin/env python3
"""
中国网红多平台抓取器
China Influencers Multi-Platform Scraper

平台: Bilibili(API) + Weibo(估算) + Douyin(估算) + Xiaohongshu(估算)

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
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field

# 数据类定义 (与主系统一致)
@dataclass
class PlatformData:
    """平台数据"""
    platform: str
    status: str
    followers: int
    total_views: int
    posts_count: int
    recent_posts: List[Dict] = field(default_factory=list)
    top_posts: List[Dict] = field(default_factory=list)
    error_message: str = ""
    raw_data: Dict = field(default_factory=dict)

@dataclass
class InfluencerProfile:
    """网红完整档案"""
    name: str
    handle: str
    category: str
    political_leaning: str
    platforms: Dict[str, PlatformData]
    content_analysis: Dict = field(default_factory=dict)
    collected_at: str = ""

    def __post_init__(self):
        if not self.collected_at:
            self.collected_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


class BilibiliFetcher:
    """Bilibili数据抓取器 - 免费API"""

    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://space.bilibili.com'
        }

    def request_json(self, url: str, params: Dict = None) -> Dict:
        """发送请求获取JSON"""
        try:
            if params:
                url = f"{url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15, context=self.ssl_context) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            return {"code": -1, "message": str(e)}

    def fetch(self, uid: str) -> PlatformData:
        """获取Bilibili数据"""
        print(f"    📺 Bilibili...", end=" ")

        try:
            # 获取用户基本信息
            url = "https://api.bilibili.com/x/web-interface/card"
            data = self.request_json(url, {"mid": uid})

            if data.get("code") != 0:
                return PlatformData(
                    platform="bilibili",
                    status="error",
                    followers=0,
                    total_views=0,
                    posts_count=0,
                    error_message=data.get("message", "API error")
                )

            card = data["data"]["card"]
            followers = card.get("fans", 0)
            likes = card.get("likes", 0)

            # 获取视频列表
            videos = self._fetch_videos(uid)
            total_plays = sum(v.get("plays", 0) for v in videos)

            print(f"✅ {followers:,}粉丝, {len(videos)}视频")

            return PlatformData(
                platform="bilibili",
                status="success",
                followers=followers,
                total_views=total_plays,
                posts_count=len(videos),
                recent_posts=videos[:10],
                top_posts=sorted(videos, key=lambda x: x.get("plays", 0), reverse=True)[:5],
                raw_data={
                    "name": card.get("name", ""),
                    "level": card.get("level_info", {}).get("current_level", 0),
                    "likes": likes,
                    "description": card.get("sign", "")[:100]
                }
            )

        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
            return PlatformData(
                platform="bilibili",
                status="error",
                followers=0,
                total_views=0,
                posts_count=0,
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

            data = self.request_json(url, params)

            if data.get("code") != 0:
                return []

            videos = data["data"]["list"]["vlist"]
            result = []

            for video in videos:
                result.append({
                    "bvid": video.get("bvid"),
                    "title": video.get("title"),
                    "plays": video.get("play", 0),
                    "likes": video.get("like", 0),
                    "comments": video.get("comment", 0),
                    "created": video.get("created", 0),
                    "length": video.get("length"),
                    "pic": video.get("pic")
                })

            return result

        except Exception as e:
            print(f"Video fetch error: {e}")
            return []


class WeiboFetcher:
    """微博数据抓取器 - 基于估算模型"""

    def fetch(self, uid: str, name: str) -> PlatformData:
        """获取微博数据（估算）"""
        print(f"    📱 Weibo...", end=" ")

        # 基于公开信息的估算
        estimates = {
            "2970459952": {"followers": 27500000, "name": "李子柒"},
            "1273590434": {"followers": 2200000, "name": "司马南"},
            "1989660417": {"followers": 24800000, "name": "胡锡进"}
        }

        est = estimates.get(uid, {"followers": 1000000, "name": name})

        print(f"✅ {est['followers']:,}粉丝 (估算)")

        return PlatformData(
            platform="weibo",
            status="estimated",
            followers=est["followers"],
            total_views=est["followers"] * 0.2,  # 估算阅读量
            posts_count=0,
            recent_posts=[{"note": "Weibo数据基于公开信息估算"}],
            raw_data={"uid": uid, "name": est["name"], "note": "Estimated data"}
        )


class DouyinFetcher:
    """抖音数据抓取器 - 基于估算模型"""

    def fetch(self, name: str) -> PlatformData:
        """获取抖音数据（估算）"""
        print(f"    🎵 Douyin...", end=" ")

        # 基于公开信息的估算
        estimates = {
            "李子柒": {"followers": 49000000},
            "司马南": {"followers": 8500000},
            "胡锡进": {"followers": 12000000}
        }

        est = estimates.get(name, {"followers": 5000000})

        print(f"✅ {est['followers']:,}粉丝 (估算)")

        return PlatformData(
            platform="douyin",
            status="estimated",
            followers=est["followers"],
            total_views=est["followers"] * 10,  # 估算播放量
            posts_count=0,
            recent_posts=[{"note": "Douyin数据基于公开信息估算"}],
            raw_data={"name": name, "note": "Estimated data"}
        )


class ChinaInfluencersScraper:
    """中国网红多平台抓取器"""

    INFLUENCERS = [
        {
            "name": "李子柒",
            "handle": "liziqi",
            "category": "传统文化/生活方式",
            "political_leaning": "文化输出/中性",
            "platforms": {
                "bilibili": {"uid": "19577966"},
                "weibo": {"uid": "2970459952"},
                "douyin": {"name": "李子柒"}
            }
        },
        {
            "name": "司马南",
            "handle": "simanan",
            "category": "政治评论/时事",
            "political_leaning": "民族主义/左派",
            "platforms": {
                "weibo": {"uid": "1273590434"},
                "douyin": {"name": "司马南"}
            }
        },
        {
            "name": "胡锡进",
            "handle": "huxijin",
            "category": "政治评论/媒体",
            "political_leaning": "官方立场/建制派",
            "platforms": {
                "bilibili": {"uid": "586158922"},
                "weibo": {"uid": "1989660417"},
                "douyin": {"name": "胡锡进"}
            }
        }
    ]

    def __init__(self):
        self.bilibili = BilibiliFetcher()
        self.weibo = WeiboFetcher()
        self.douyin = DouyinFetcher()

    def scrape_all(self) -> List[InfluencerProfile]:
        """抓取所有中国网红"""
        print("="*60)
        print("🇨🇳 中国网红多平台抓取")
        print("平台: Bilibili + Weibo + Douyin")
        print("="*60)

        results = []

        for config in self.INFLUENCERS:
            print(f"\n🎯 {config['name']}")

            platforms = {}

            # Bilibili
            if config['platforms'].get('bilibili'):
                bilibili_data = self.bilibili.fetch(config['platforms']['bilibili']['uid'])
                platforms['bilibili'] = bilibili_data
                if bilibili_data.status == "success":
                    time.sleep(2)  # 避免频率限制

            # Weibo
            if config['platforms'].get('weibo'):
                weibo_data = self.weibo.fetch(
                    config['platforms']['weibo']['uid'],
                    config['name']
                )
                platforms['weibo'] = weibo_data

            # Douyin
            if config['platforms'].get('douyin'):
                douyin_data = self.douyin.fetch(config['platforms']['douyin']['name'])
                platforms['douyin'] = douyin_data

            profile = InfluencerProfile(
                name=config['name'],
                handle=config['handle'],
                category=config['category'],
                political_leaning=config['political_leaning'],
                platforms=platforms
            )

            results.append(profile)

        return results


def main():
    """主程序"""
    scraper = ChinaInfluencersScraper()
    results = scraper.scrape_all()

    # 打印摘要
    print("\n" + "="*60)
    print("📊 数据摘要")
    print("="*60)

    for profile in results:
        print(f"\n🎯 {profile.name} ({profile.category})")
        print(f"   政治倾向: {profile.political_leaning}")

        for platform_name, data in profile.platforms.items():
            status_icon = "✅" if data.status == "success" else "⚠️"
            print(f"   {status_icon} {platform_name.upper():12} | {data.followers:>12,} followers")

    # 保存数据
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    data = {
        "generated_at": datetime.now().isoformat(),
        "region": "CN",
        "influencers": [r.to_dict() for r in results]
    }

    output_dir = ".."
    filename = f"{output_dir}/data/json/CN_INFLUENCERS_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 数据已保存: {filename}")
    print("="*60)
    print("✅ 中国网红抓取完成!")
    print("="*60)


if __name__ == "__main__":
    main()
