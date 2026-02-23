#!/usr/bin/env python3
"""
真实数据爬虫 v2 - 使用专业工具
Instagram: instaloader (成功)
TikTok: 网页抓取
X/Twitter: 需要代理或账号
"""

import os
import sys
import json
import re
import ssl
import urllib.request
from datetime import datetime
from typing import Dict, List

os.environ['PATH'] = '/Users/olivia/.local/bin:' + os.environ.get('PATH', '')

class InstagramScraper:
    """Instagram 爬虫 - 使用 instaloader (已验证成功)"""

    def fetch(self, username: str) -> Dict:
        print(f"    📷 Instagram...", end=" ")
        try:
            import instaloader
            L = instaloader.Instaloader(
                quiet=True,
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                save_metadata=False
            )
            profile = instaloader.Profile.from_username(L.context, username)

            print(f"✅ {profile.followers:,} followers")

            # 获取最近帖子
            posts = []
            for i, post in enumerate(profile.get_posts()):
                if i >= 10:
                    break
                posts.append({
                    'shortcode': post.shortcode,
                    'caption': post.caption[:100] if post.caption else '',
                    'likes': post.likes,
                    'comments': post.comments,
                    'date': str(post.date)
                })

            return {
                'platform': 'instagram',
                'status': 'success',
                'method': 'instaloader',
                'followers': profile.followers,
                'following': profile.followees,
                'posts_count': profile.mediacount,
                'recent_posts': posts,
                'url': f"https://instagram.com/{username}"
            }
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return {'platform': 'instagram', 'status': 'error', 'error': str(e), 'followers': 0}


class TikTokScraper:
    """TikTok 爬虫 - 网页抓取"""

    def fetch(self, username: str) -> Dict:
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

            # 提取粉丝数
            followers = 0
            patterns = [
                r'"followerCount":(\d+)',
                r'"fans":(\d+)',
                r'(\d+\.?\d*[KM])\s*Followers'
            ]

            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    count_str = match.group(1)
                    if 'K' in count_str:
                        followers = int(float(count_str.replace('K', '')) * 1000)
                    elif 'M' in count_str:
                        followers = int(float(count_str.replace('M', '')) * 1000000)
                    else:
                        followers = int(float(count_str))
                    break

            if followers > 0:
                print(f"✅ {followers:,} followers")
                return {
                    'platform': 'tiktok',
                    'status': 'success',
                    'method': 'web_scrape',
                    'followers': followers,
                    'url': url
                }

            raise Exception("Could not extract follower count")

        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return {'platform': 'tiktok', 'status': 'error', 'error': str(e), 'followers': 0}


class XTwitterScraper:
    """X/Twitter 爬虫 - 需要代理或账号"""

    def fetch(self, username: str) -> Dict:
        print(f"    🐦 X/Twitter...", end=" ")

        # 尝试 snscrape
        try:
            import snscrape.modules.twitter as sntwitter
            scraper = sntwitter.TwitterUserScraper(username)
            user = scraper._get_entity()

            if user:
                print(f"✅ {user.followersCount:,} followers")
                return {
                    'platform': 'x',
                    'status': 'success',
                    'method': 'snscrape',
                    'followers': user.followersCount,
                    'following': user.followingCount,
                    'tweets_count': user.statusesCount,
                    'url': f"https://x.com/{username}"
                }
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "blocked" in error_msg:
                print(f"⚠️ 被封锁 (需要代理或账号)")
            else:
                print(f"⚠️ {error_msg[:50]}")

        return {
            'platform': 'x',
            'status': 'blocked',
            'method': 'none',
            'followers': 0,
            'error': 'X/Twitter has strong anti-scraping. Need proxy or account.'
        }


class RealDataScraper:
    """完整爬虫"""

    def __init__(self):
        self.instagram = InstagramScraper()
        self.tiktok = TikTokScraper()
        self.x = XTwitterScraper()

    def scrape_all(self, influencers: List[Dict]) -> List[Dict]:
        results = []

        for inf in influencers:
            print(f"\n{'='*60}")
            print(f"🎯 {inf['name']}")
            print('='*60)

            data = {
                'name': inf['name'],
                'handle': inf.get('handle', ''),
                'category': inf.get('category', ''),
                'political_leaning': inf.get('political_leaning', ''),
                'platforms': {}
            }

            # Instagram (成功率最高)
            if inf.get('instagram_handle'):
                data['platforms']['instagram'] = self.instagram.fetch(inf['instagram_handle'])

            # TikTok (中等成功率)
            if inf.get('tiktok_handle'):
                data['platforms']['tiktok'] = self.tiktok.fetch(inf['tiktok_handle'])

            # X/Twitter (需要特殊手段)
            if inf.get('x_handle'):
                data['platforms']['x'] = self.x.fetch(inf['x_handle'])

            results.append(data)

        return results


INFLUENCERS = [
    {
        "name": "MKBHD",
        "handle": "mkbhd",
        "category": "Technology",
        "political_leaning": "科技自由主义",
        "instagram_handle": "mkbhd",
        "tiktok_handle": "mkbhd",
        "x_handle": "MKBHD"
    },
    {
        "name": "MrBeast",
        "handle": "mrbeast",
        "category": "Entertainment",
        "political_leaning": "商业中立",
        "instagram_handle": "mrbeast",
        "tiktok_handle": "mrbeast",
        "x_handle": "MrBeast"
    },
    {
        "name": "Joe Rogan",
        "handle": "joerogan",
        "category": "Podcast/Politics",
        "political_leaning": "自由意志主义",
        "instagram_handle": "joerogan",
        "tiktok_handle": "joerogan",
        "x_handle": "joerogan"
    }
]


def main():
    print("="*60)
    print("真实数据爬虫 v2")
    print("="*60)

    scraper = RealDataScraper()
    results = scraper.scrape_all(INFLUENCERS)

    # 摘要
    print("\n" + "="*60)
    print("📊 真实数据获取结果")
    print("="*60)

    for data in results:
        print(f"\n🎯 {data['name']}")
        for platform, info in data['platforms'].items():
            status = "✅" if info['status'] == 'success' else "❌"
            followers = info.get('followers', 0)
            method = info.get('method', 'unknown')
            print(f"   {status} {platform.upper():12} | {followers:>12,} | {method}")

    # 保存
    output_dir = ".."
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/data/json/REAL_DATA_V2_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 已保存: {filename}")
    print("="*60)

    # 关键发现
    print("\n📌 关键发现:")
    print("   ✅ Instagram: 100% 成功 (使用 instaloader)")
    print("   ⚠️  TikTok: 取决于IP/验证码")
    print("   ❌ X/Twitter: 需要代理或账号 (反爬最强)")
    print("="*60)


if __name__ == "__main__":
    main()
