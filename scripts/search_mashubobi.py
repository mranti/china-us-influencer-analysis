#!/usr/bin/env python3
"""
搜索 麻薯波比 全平台数据
使用现有的完整报告工具
"""

import os
import sys
import json
import ssl
import time
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List

# 输出目录
OUTPUT_DIR = ".."

# 麻薯波比配置
MASHUBOBI = {
    "key": "mashubobi",
    "name": "麻薯波比",
    "real_name": "未知",
    "category": "知识/历史/军事",
    "political_stance": "民族主义/温和建制派",
    "direction": "历史知识科普，军事时政评论，国际局势分析",
    "bilibili_uid": "703186600",  # 从搜索获取
    "estimated_followers": {
        "bilibili": 2500000,  # 估算
        "weibo": 800000,
        "douyin": 3000000,
        "wechat_official": 500000,
        "wechat_channels": 800000
    }
}


class BilibiliFetcher:
    """Bilibili数据抓取器"""

    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://space.bilibili.com'
        }

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

    def fetch(self, uid: str) -> Dict:
        """获取Bilibili数据"""
        print(f"    📺 Bilibili (UID: {uid})...", end=" ")

        try:
            # 获取用户基本信息
            url = "https://api.bilibili.com/x/web-interface/card"
            data = self._request_json(url, {"mid": uid})

            if data.get("code") != 0:
                error_msg = data.get("message", "API error")
                print(f"❌ {error_msg}")
                return None

            card = data["data"]["card"]
            followers = card.get("fans", 0)
            likes = card.get("likes", 0)
            level = card.get("level_info", {}).get("current_level", 0)
            name = card.get("name", "")
            sign = card.get("sign", "")

            # 获取视频列表
            videos = self._fetch_videos(uid)
            total_plays = sum(v.get("play", 0) for v in videos)

            print(f"✅ {followers:,}粉丝, {len(videos)}视频")

            return {
                "platform": "bilibili",
                "status": "success",
                "followers": followers,
                "likes": likes,
                "level": level,
                "name": name,
                "sign": sign,
                "videos_count": len(videos),
                "total_plays": total_plays,
                "recent_videos": videos[:5]
            }

        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
            return None

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
                    "title": video.get("title", ""),
                    "play": video.get("play", 0),
                    "like": video.get("like", 0),
                    "comment": video.get("comment", 0),
                    "created": video.get("created", 0),
                    "length": video.get("length", "")
                })

            return result

        except Exception as e:
            return []


def search_mashubobi():
    """搜索麻薯波比全平台数据"""
    print("="*70)
    print("🔍 搜索 麻薯波比 全平台数据")
    print("="*70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    fetcher = BilibiliFetcher()

    # 1. Bilibili (尝试获取真实数据)
    bilibili_data = fetcher.fetch(MASHUBOBI["bilibili_uid"])

    if bilibili_data and bilibili_data.get("followers", 0) > 0:
        print(f"\n✅ 成功获取Bilibili数据!")
        print(f"   昵称: {bilibili_data['name']}")
        print(f"   粉丝: {bilibili_data['followers']:,}")
        print(f"   获赞: {bilibili_data['likes']:,}")
        print(f"   等级: LV{bilibili_data['level']}")
        print(f"   签名: {bilibili_data['sign'][:50]}...")
        print(f"   视频数: {bilibili_data['videos_count']}")
        print(f"   总播放: {bilibili_data['total_plays']:,}")

        # 显示最近视频
        if bilibili_data.get("recent_videos"):
            print(f"\n   📹 最近视频:")
            for i, v in enumerate(bilibili_data["recent_videos"][:3], 1):
                print(f"      {i}. {v['title'][:40]}... ({v['play']:,}播放)")
    else:
        print(f"\n⚠️ 无法获取Bilibili数据，使用估算值")
        bilibili_data = {
            "platform": "bilibili",
            "status": "estimated",
            "followers": MASHUBOBI["estimated_followers"]["bilibili"],
            "note": "API访问受限，使用估算值"
        }

    # 2. 其他平台 (估算)
    print(f"\n📊 其他平台数据 (基于行业估算):")
    print(f"   📱 微博: {MASHUBOBI['estimated_followers']['weibo']:,} 粉丝 (估算)")
    print(f"   🎵 抖音: {MASHUBOBI['estimated_followers']['douyin']:,} 粉丝 (估算)")
    print(f"   💬 微信公众号: {MASHUBOBI['estimated_followers']['wechat_official']:,} 关注 (估算)")
    print(f"   📹 微信视频号: {MASHUBOBI['estimated_followers']['wechat_channels']:,} 关注 (估算)")

    # 计算总影响力
    total_followers = sum(MASHUBOBI['estimated_followers'].values())
    if bilibili_data and bilibili_data.get("status") == "success":
        total_followers = bilibili_data["followers"] + sum([
            MASHUBOBI['estimated_followers']['weibo'],
            MASHUBOBI['estimated_followers']['douyin'],
            MASHUBOBI['estimated_followers']['wechat_official'],
            MASHUBOBI['estimated_followers']['wechat_channels']
        ])

    print(f"\n" + "="*70)
    print(f"📈 麻薯波比 全平台数据摘要")
    print("="*70)
    print(f"   类别: {MASHUBOBI['category']}")
    print(f"   政治倾向: {MASHUBOBI['political_stance']}")
    print(f"   内容方向: {MASHUBOBI['direction']}")
    print(f"   估算总粉丝: {total_followers:,}")
    print("="*70)

    # 保存结果
    result_data = {
        "name": MASHUBOBI['name'],
        "category": MASHUBOBI['category'],
        "political_stance": MASHUBOBI['political_stance'],
        "bilibili": bilibili_data,
        "other_platforms": {
            "weibo": {"followers": MASHUBOBI['estimated_followers']['weibo'], "status": "estimated"},
            "douyin": {"followers": MASHUBOBI['estimated_followers']['douyin'], "status": "estimated"},
            "wechat_official": {"followers": MASHUBOBI['estimated_followers']['wechat_official'], "status": "estimated"},
            "wechat_channels": {"followers": MASHUBOBI['estimated_followers']['wechat_channels'], "status": "estimated"}
        },
        "total_estimated_followers": total_followers,
        "searched_at": datetime.now().isoformat()
    }

    # 保存到文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{OUTPUT_DIR}/data/json/SEARCH_MASHUBOBI_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 数据已保存: {filename}")
    print("\n" + "="*70)
    print("✅ 搜索完成!")
    print("="*70)

    return result_data


if __name__ == "__main__":
    search_mashubobi()
