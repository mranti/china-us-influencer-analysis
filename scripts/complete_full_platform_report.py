#!/usr/bin/env python3
"""
完整全平台报告生成器
整合: YouTube + Podcast + Twitter/X + TikTok + Instagram
"""

import os
import json
import re
import ssl
import urllib.request
from datetime import datetime
from typing import Dict, List

os.environ['PATH'] = '/Users/olivia/.local/bin:' + os.environ.get('PATH', '')

# 输出目录
OUTPUT_DIR = ".."
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', 'AIzaSyAiSo5FPoUbLkird3MgsM8GnBXY_XEsMAo')

# ==================== 平台权重配置 ====================
PLATFORM_WEIGHTS = {
    "youtube": {"weight": 1.0, "engagement": 0.05, "region": "US"},
    "podcast": {"weight": 0.6, "engagement": 0.08, "region": "US"},
    "twitter": {"weight": 0.25, "engagement": 0.02, "region": "US"},
    "tiktok": {"weight": 0.35, "engagement": 0.15, "region": "US"},
    "instagram": {"weight": 0.3, "engagement": 0.03, "region": "US"},
}

# ==================== YouTube 抓取 ====================
class YouTubeScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def get_channel_stats(self, channel_id: str) -> Dict:
        """获取频道统计信息"""
        url = f"{self.base_url}/channels?part=statistics,snippet&id={channel_id}&key={self.api_key}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            if data.get('items'):
                item = data['items'][0]
                stats = item['statistics']
                snippet = item['snippet']
                return {
                    'status': 'success',
                    'subscribers': int(stats.get('subscriberCount', 0)),
                    'views': int(stats.get('viewCount', 0)),
                    'videos': int(stats.get('videoCount', 0)),
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', '')[:200],
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
        return {'status': 'no_data'}

    def get_latest_videos(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """获取最近视频"""
        search_url = f"{self.base_url}/search?part=snippet&channelId={channel_id}&order=date&maxResults={max_results}&key={self.api_key}"
        try:
            req = urllib.request.Request(search_url)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            videos = []
            for item in data.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    snippet = item['snippet']
                    videos.append({
                        'video_id': item['id']['videoId'],
                        'title': snippet.get('title', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', '')
                    })
            return videos
        except Exception as e:
            return []

    def get_video_stats(self, video_ids: List[str]) -> Dict[str, Dict]:
        """获取视频统计数据"""
        ids_str = ','.join(video_ids)
        url = f"{self.base_url}/videos?part=statistics&id={ids_str}&key={self.api_key}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            stats = {}
            for item in data.get('items', []):
                stats[item['id']] = {
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0)),
                }
            return stats
        except Exception as e:
            return {}

    def fetch_full_data(self, channel_id: str) -> Dict:
        """获取完整YouTube数据"""
        print(f"    📺 YouTube...", end=" ")

        # 基础信息
        stats = self.get_channel_stats(channel_id)
        if stats.get('status') != 'success':
            print(f"❌ {stats.get('error', 'Unknown')}")
            return {'platform': 'youtube', 'status': 'error', 'error': stats.get('error')}

        # 最近视频
        videos = self.get_latest_videos(channel_id)
        video_ids = [v['video_id'] for v in videos]
        video_stats = self.get_video_stats(video_ids)

        # 合并数据
        for video in videos:
            vid = video['video_id']
            if vid in video_stats:
                video.update(video_stats[vid])

        # 计算平均互动
        avg_views = sum(v.get('views', 0) for v in videos) / len(videos) if videos else 0
        avg_likes = sum(v.get('likes', 0) for v in videos) / len(videos) if videos else 0

        print(f"✅ {stats['subscribers']:,} subscribers")

        return {
            'platform': 'youtube',
            'status': 'success',
            'subscribers': stats['subscribers'],
            'total_views': stats['views'],
            'videos_count': stats['videos'],
            'channel_title': stats['title'],
            'avg_video_views': int(avg_views),
            'avg_video_likes': int(avg_likes),
            'recent_videos': videos[:5],
            'url': f"https://youtube.com/channel/{channel_id}"
        }

# ==================== Podcast 抓取 ====================
class PodcastScraper:
    """Podcast 数据抓取 (使用 Spotify + RSS)"""

    def fetch_jre_podcast(self) -> Dict:
        """获取 Joe Rogan Experience Podcast 数据"""
        print(f"    🎙️  Podcast...", end=" ")
        try:
            # Spotify JRE 数据 (通过公开页面估算)
            # JRE 是 Spotify 独家，我们可以用估算值或尝试抓取

            # 尝试 ListenNotes API (免费层)
            listennotes_key = os.environ.get('LISTENNOTES_API_KEY', '')

            if listennotes_key:
                url = "https://listen-api.listennotes.com/api/v2/podcasts/0e3538ad3b81428788c07b2401dc96c2"
                headers = {'X-ListenAPI-Key': listennotes_key}
                req = urllib.request.Request(url, headers=headers)

                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode('utf-8'))

                return {
                    'platform': 'podcast',
                    'status': 'success',
                    'title': data.get('title', 'The Joe Rogan Experience'),
                    'episodes_count': data.get('total_episodes', 2300),
                    'latest_episode': data.get('latest_episode_title', ''),
                    'listen_score': data.get('listen_score', 95),
                    'url': 'https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk'
                }
            else:
                # 使用已知数据估算
                return {
                    'platform': 'podcast',
                    'status': 'estimated',
                    'title': 'The Joe Rogan Experience',
                    'episodes_count': 2300,
                    'estimated_listeners': 11000000,  # 约1100万每集
                    'avg_duration_minutes': 150,
                    'note': 'Spotify独家数据，使用估算值',
                    'url': 'https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk'
                }
        except Exception as e:
            print(f"⚠️ 使用估算值")
            return {
                'platform': 'podcast',
                'status': 'estimated',
                'title': 'The Joe Rogan Experience',
                'episodes_count': 2300,
                'estimated_listeners': 11000000,
                'note': f'抓取失败，使用估算值: {str(e)[:30]}',
                'url': 'https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk'
            }

    def fetch(self, podcast_name: str) -> Dict:
        if 'rogan' in podcast_name.lower():
            result = self.fetch_jre_podcast()
            if result.get('status') in ['success', 'estimated']:
                listeners = result.get('estimated_listeners', result.get('listen_score', 0) * 100000)
                print(f"✅ ~{listeners:,} listeners")
            return result

        return {
            'platform': 'podcast',
            'status': 'not_available',
            'error': 'Podcast data not configured'
        }

# ==================== Instagram 抓取 ====================
class InstagramScraper:
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

            posts = []
            for i, post in enumerate(profile.get_posts()):
                if i >= 5:
                    break
                posts.append({
                    'caption': post.caption[:80] if post.caption else '',
                    'likes': post.likes,
                    'comments': post.comments,
                    'date': str(post.date)
                })

            return {
                'platform': 'instagram',
                'status': 'success',
                'followers': profile.followers,
                'following': profile.followees,
                'posts_count': profile.mediacount,
                'recent_posts': posts,
                'url': f"https://instagram.com/{username}"
            }
        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            return {'platform': 'instagram', 'status': 'error', 'error': str(e)}

# ==================== TikTok 抓取 ====================
class TikTokScraper:
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
                    'followers': followers,
                    'url': url
                }

            raise Exception("Could not extract follower count")

        except Exception as e:
            print(f"❌ {str(e)[:40]}")
            return {'platform': 'tiktok', 'status': 'error', 'error': str(e)}

# ==================== X/Twitter 抓取 ====================
class XScraper:
    def fetch(self, username: str) -> Dict:
        print(f"    🐦 X/Twitter...", end=" ")
        # 使用配置值 (因为所有免费方法都被封锁)
        configured_values = {
            'MKBHD': 3100000,
            'MrBeast': 31000000,
            'joerogan': 14800000,
        }

        followers = configured_values.get(username, 0)
        if followers > 0:
            print(f"⚠️ 使用估算值 {followers:,}")
        else:
            print(f"⚠️ 无数据")

        return {
            'platform': 'twitter',
            'status': 'estimated',
            'followers': followers,
            'note': 'X/Twitter已封锁所有免费抓取方法，使用估算值',
            'url': f"https://x.com/{username}"
        }

# ==================== 影响力计算 ====================
class InfluenceCalculator:
    def calculate(self, platforms: Dict[str, Dict]) -> Dict:
        """计算综合影响力分数"""
        total_score = 0
        platform_scores = {}

        # YouTube (核心平台)
        if 'youtube' in platforms and platforms['youtube'].get('status') == 'success':
            yt = platforms['youtube']
            subs = yt.get('subscribers', 0)
            views = yt.get('total_views', 0)
            avg_views = yt.get('avg_video_views', 0)

            # 基础分: 订阅数权重
            base_score = subs * PLATFORM_WEIGHTS['youtube']['weight']
            # 传播分: 平均观看量
            spread_score = avg_views * PLATFORM_WEIGHTS['youtube']['engagement'] * 100
            # 总权重分
            score = (base_score * 0.4 + spread_score * 0.4 + subs * 0.2 * PLATFORM_WEIGHTS['youtube']['weight'])

            platform_scores['youtube'] = {
                'subscribers': subs,
                'total_views': views,
                'score_contribution': int(score),
                'details': f"{subs:,} subscribers, {views:,} total views"
            }
            total_score += score

        # Podcast
        if 'podcast' in platforms and platforms['podcast'].get('status') in ['success', 'estimated']:
            pod = platforms['podcast']
            listeners = pod.get('estimated_listeners', pod.get('listen_score', 0) * 100000)

            score = listeners * PLATFORM_WEIGHTS['podcast']['weight']

            platform_scores['podcast'] = {
                'estimated_listeners': listeners,
                'episodes': pod.get('episodes_count', 0),
                'score_contribution': int(score),
                'details': f"~{listeners:,} listeners per episode"
            }
            total_score += score

        # Instagram
        if 'instagram' in platforms and platforms['instagram'].get('status') == 'success':
            ig = platforms['instagram']
            followers = ig.get('followers', 0)
            posts = ig.get('posts_count', 0)

            score = followers * PLATFORM_WEIGHTS['instagram']['weight']

            platform_scores['instagram'] = {
                'followers': followers,
                'posts': posts,
                'score_contribution': int(score),
                'details': f"{followers:,} followers, {posts:,} posts"
            }
            total_score += score

        # TikTok
        if 'tiktok' in platforms and platforms['tiktok'].get('status') == 'success':
            tt = platforms['tiktok']
            followers = tt.get('followers', 0)

            score = followers * PLATFORM_WEIGHTS['tiktok']['weight']

            platform_scores['tiktok'] = {
                'followers': followers,
                'score_contribution': int(score),
                'details': f"{followers:,} followers"
            }
            total_score += score

        # X/Twitter
        if 'twitter' in platforms and platforms['twitter'].get('status') in ['success', 'estimated']:
            x = platforms['twitter']
            followers = x.get('followers', 0)

            score = followers * PLATFORM_WEIGHTS['twitter']['weight']

            platform_scores['twitter'] = {
                'followers': followers,
                'score_contribution': int(score),
                'note': '使用估算值',
                'details': f"{followers:,} followers (estimated)"
            }
            total_score += score

        return {
            'total_score': int(total_score),
            'platforms': platform_scores
        }

# ==================== 主程序 ====================
INFLUENCERS = [
    {
        "name": "MKBHD",
        "full_name": "Marques Brownlee",
        "category": "Technology",
        "political_leaning": "科技自由主义",
        "youtube_channel": "UCBJycsmduvYEL83R_U4JriQ",
        "instagram_handle": "mkbhd",
        "tiktok_handle": "mkbhd",
        "x_handle": "MKBHD",
        "has_podcast": False
    },
    {
        "name": "MrBeast",
        "full_name": "Jimmy Donaldson",
        "category": "Entertainment",
        "political_leaning": "商业中立",
        "youtube_channel": "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "instagram_handle": "mrbeast",
        "tiktok_handle": "mrbeast",
        "x_handle": "MrBeast",
        "has_podcast": False
    },
    {
        "name": "Joe Rogan Experience",
        "full_name": "Joe Rogan",
        "category": "Podcast/Politics",
        "political_leaning": "自由意志主义",
        "youtube_channel": "UCzQUP1qoWDoEbmsQxvdjxgQ",  # PowerfulJRE
        "instagram_handle": "joerogan",
        "tiktok_handle": "joerogan",
        "x_handle": "joerogan",
        "has_podcast": True,
        "podcast_name": "The Joe Rogan Experience"
    }
]


def generate_full_report():
    """生成完整全平台报告"""
    print("="*70)
    print("📊 完整全平台报告生成器")
    print("平台: YouTube + Podcast + X/Twitter + TikTok + Instagram")
    print("="*70)

    # 初始化爬虫
    yt_scraper = YouTubeScraper(YOUTUBE_API_KEY)
    pod_scraper = PodcastScraper()
    ig_scraper = InstagramScraper()
    tt_scraper = TikTokScraper()
    x_scraper = XScraper()
    calculator = InfluenceCalculator()

    results = []

    for influencer in INFLUENCERS:
        print(f"\n{'='*70}")
        print(f"🎯 {influencer['name']}")
        print('='*70)

        platforms = {}

        # 1. YouTube
        if influencer.get('youtube_channel'):
            platforms['youtube'] = yt_scraper.fetch_full_data(influencer['youtube_channel'])

        # 2. Podcast (仅 Joe Rogan)
        if influencer.get('has_podcast'):
            platforms['podcast'] = pod_scraper.fetch(influencer['podcast_name'])

        # 3. Instagram
        if influencer.get('instagram_handle'):
            platforms['instagram'] = ig_scraper.fetch(influencer['instagram_handle'])

        # 4. TikTok
        if influencer.get('tiktok_handle'):
            platforms['tiktok'] = tt_scraper.fetch(influencer['tiktok_handle'])

        # 5. X/Twitter
        if influencer.get('x_handle'):
            platforms['twitter'] = x_scraper.fetch(influencer['x_handle'])

        # 计算影响力
        influence = calculator.calculate(platforms)

        results.append({
            'name': influencer['name'],
            'full_name': influencer.get('full_name', ''),
            'category': influencer['category'],
            'political_leaning': influencer['political_leaning'],
            'platforms': platforms,
            'influence_score': influence['total_score'],
            'platform_breakdown': influence['platforms']
        })

    # 排序
    results.sort(key=lambda x: x['influence_score'], reverse=True)

    # 生成报告
    generate_text_report(results)
    save_json_data(results)

    return results


def generate_text_report(results: List[Dict]):
    """生成文本报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{OUTPUT_DIR}/data/reports/COMPLETE_FULL_REPORT_{timestamp}.txt"

    lines = []
    lines.append("="*80)
    lines.append("📈 完整全平台影响力报告")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("="*80)
    lines.append("")
    lines.append("📊 平台覆盖: YouTube + Podcast + X/Twitter + TikTok + Instagram")
    lines.append("")

    # 排行榜
    lines.append("="*80)
    lines.append("🏆 综合影响力排行")
    lines.append("="*80)
    lines.append("")

    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['name']:<25} | {r['category']:<18} | 分数: {r['influence_score']:>15,}")
        lines.append(f"   政治倾向: {r['political_leaning']}")
        lines.append("")

    # 详细数据
    lines.append("="*80)
    lines.append("📋 详细平台数据")
    lines.append("="*80)

    for r in results:
        lines.append("")
        lines.append(f"\n{'─'*80}")
        lines.append(f"🎯 {r['name']} ({r['full_name']})")
        lines.append(f"   类别: {r['category']} | 政治倾向: {r['political_leaning']}")
        lines.append(f"   综合影响力分数: {r['influence_score']:,}")
        lines.append('─'*80)

        for platform_name, platform_data in r['platforms'].items():
            if platform_data.get('status') in ['success', 'estimated']:
                lines.append(f"\n   📌 {platform_name.upper()}")

                if platform_name == 'youtube':
                    lines.append(f"      订阅者: {platform_data.get('subscribers', 0):,}")
                    lines.append(f"      总观看: {platform_data.get('total_views', 0):,}")
                    lines.append(f"      视频数: {platform_data.get('videos_count', 0):,}")
                    lines.append(f"      平均观看/视频: {platform_data.get('avg_video_views', 0):,}")
                    if platform_data.get('recent_videos'):
                        lines.append(f"      最新视频: {platform_data['recent_videos'][0].get('title', '')[:50]}...")

                elif platform_name == 'podcast':
                    listeners = platform_data.get('estimated_listeners', platform_data.get('listen_score', 0) * 100000)
                    lines.append(f"      估算听众: {listeners:,} / 集")
                    lines.append(f"      总集数: {platform_data.get('episodes_count', 'N/A')}")
                    if platform_data.get('status') == 'estimated':
                        lines.append(f"      ⚠️ 注意: 使用估算值 (Spotify独家数据)")

                elif platform_name == 'instagram':
                    lines.append(f"      粉丝: {platform_data.get('followers', 0):,}")
                    lines.append(f"      关注: {platform_data.get('following', 0):,}")
                    lines.append(f"      帖子: {platform_data.get('posts_count', 0):,}")
                    if platform_data.get('recent_posts'):
                        top_post = max(platform_data['recent_posts'], key=lambda x: x.get('likes', 0))
                        lines.append(f"      最高赞帖子: {top_post.get('likes', 0):,} likes")

                elif platform_name == 'tiktok':
                    lines.append(f"      粉丝: {platform_data.get('followers', 0):,}")

                elif platform_name == 'twitter':
                    lines.append(f"      粉丝: {platform_data.get('followers', 0):,}")
                    if platform_data.get('status') == 'estimated':
                        lines.append(f"      ⚠️ 注意: X/Twitter已封锁所有免费抓取，使用估算值")

                # 分数贡献
                if platform_name in r['platform_breakdown']:
                    contribution = r['platform_breakdown'][platform_name].get('score_contribution', 0)
                    lines.append(f"      📊 分数贡献: {contribution:,}")

    # 平台权重说明
    lines.append("\n" + "="*80)
    lines.append("⚖️ 平台权重说明")
    lines.append("="*80)
    lines.append("")
    lines.append("平台权重 (用于影响力计算):")
    for platform, config in PLATFORM_WEIGHTS.items():
        lines.append(f"   {platform.upper():12} | 权重: {config['weight']:.2f} | 互动系数: {config['engagement']:.2f}")

    lines.append("")
    lines.append("计算公式:")
    lines.append("   影响力分数 = Σ (平台粉丝 × 平台权重 × 互动系数)")
    lines.append("   YouTube订阅权重最高 (1.0)，其次是Podcast (0.6)")

    lines.append("\n" + "="*80)
    lines.append(f"报告生成完成 | 保存位置: {filename}")
    lines.append("="*80)

    # 写入文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # 同时打印到控制台
    print('\n'.join(lines))

    print(f"\n✅ 文本报告已保存: {filename}")


def save_json_data(results: List[Dict]):
    """保存JSON数据"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{OUTPUT_DIR}/data/json/COMPLETE_FULL_DATA_{timestamp}.json"

    data = {
        'generated_at': datetime.now().isoformat(),
        'influencers': results,
        'platform_weights': PLATFORM_WEIGHTS,
        'summary': {
            'total_influencers': len(results),
            'platforms_covered': ['youtube', 'podcast', 'twitter', 'tiktok', 'instagram'],
            'data_quality': {
                'youtube': 'real_api',
                'instagram': 'real_scrape',
                'tiktok': 'real_scrape',
                'podcast': 'estimated',
                'twitter': 'estimated (blocked)'
            }
        }
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ JSON数据已保存: {filename}")


if __name__ == "__main__":
    generate_full_report()
