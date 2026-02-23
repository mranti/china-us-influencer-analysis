#!/usr/bin/env python3
"""
ListenNotes API 播客数据获取器
免费额度: 每月10,000次请求

可以获取:
- 播客详细信息
- 所有集数列表
- 搜索特定嘉宾
- 排行榜数据

注册: https://www.listennotes.com/api/
"""

import os
import json
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional

OUTPUT_DIR = ".."

# JRE在ListenNotes上的ID
JRE_PODCAST_ID = "4d3fe717742d4963a85562e9f84d8c79"


class ListenNotesFetcher:
    """ListenNotes API获取器"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://listen-api.listennotes.com/api/v2"
        self.headers = {
            'X-ListenAPI-Key': api_key,
            'Content-Type': 'application/json'
        }

    def _request(self, endpoint: str) -> Optional[Dict]:
        """发送API请求"""
        try:
            url = f"{self.base_url}{endpoint}"
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req, timeout=15) as response:
                return json.loads(response.read().decode('utf-8'))

        except Exception as e:
            print(f"API请求失败: {e}")
            return None

    def get_podcast_info(self, podcast_id: str = JRE_PODCAST_ID) -> Optional[Dict]:
        """获取播客详细信息"""
        print(f"🔍 获取播客信息...")

        data = self._request(f"/podcasts/{podcast_id}")

        if data:
            print(f"✅ 成功!")
            print(f"   标题: {data.get('title', 'N/A')}")
            print(f"   集数: {data.get('total_episodes', 'N/A')}")
            print(f"   评分: {data.get('listen_score', 'N/A')}/100")
            print(f"   语言: {data.get('language', 'N/A')}")
            print(f"   国家: {data.get('country', 'N/A')}")

            return {
                'podcast_id': data.get('id'),
                'title': data.get('title'),
                'description': data.get('description', '')[:500],
                'publisher': data.get('publisher'),
                'total_episodes': data.get('total_episodes'),
                'listen_score': data.get('listen_score'),
                'listen_score_global_rank': data.get('listen_score_global_rank'),
                'language': data.get('language'),
                'country': data.get('country'),
                'rss_feed': data.get('rss'),
                'website': data.get('website'),
                'itunes_id': data.get('itunes_id'),
                'explicit_content': data.get('explicit_content'),
                'latest_episode_date': data.get('latest_pub_date_ms'),
                'earliest_episode_date': data.get('earliest_pub_date_ms'),
                'update_frequency_hours': data.get('update_frequency_hours'),
                'episodes_count': len(data.get('episodes', []))
            }

        return None

    def get_all_episodes(self, podcast_id: str = JRE_PODCAST_ID, limit: int = 100) -> List[Dict]:
        """获取所有集数"""
        print(f"🎧 获取最近 {limit} 集...")

        # 注意: 免费版有请求限制
        data = self._request(f"/podcasts/{podcast_id}?sort=recent_first")

        if data and 'episodes' in data:
            episodes = []
            for ep in data['episodes'][:limit]:
                episodes.append({
                    'id': ep.get('id'),
                    'title': ep.get('title'),
                    'description': ep.get('description', '')[:300],
                    'pub_date_ms': ep.get('pub_date_ms'),
                    'audio_length_sec': ep.get('audio_length_sec'),
                    'audio_length_min': ep.get('audio_length_sec', 0) // 60 if ep.get('audio_length_sec') else 0,
                    'explicit_content': ep.get('explicit_content'),
                    'maybe_audio_invalid': ep.get('maybe_audio_invalid'),
                    'listennotes_url': ep.get('listennotes_url'),
                    'audio': ep.get('audio'),
                    'thumbnail': ep.get('thumbnail')
                })

            print(f"✅ 获取到 {len(episodes)} 集")
            return episodes

        return []

    def search_in_podcast(self, query: str, podcast_id: str = JRE_PODCAST_ID) -> List[Dict]:
        """在播客中搜索特定内容"""
        print(f"🔍 在JRE中搜索: '{query}'...")

        # 构造搜索URL
        encoded_query = urllib.parse.quote(query)
        endpoint = f"/search?q={encoded_query}&type=episode&podcast_id={podcast_id}"

        data = self._request(endpoint)

        if data and 'results' in data:
            results = []
            for result in data['results']:
                episode = result.get('episode', {})
                results.append({
                    'title': episode.get('title'),
                    'description': episode.get('description', '')[:200],
                    'pub_date': episode.get('pub_date_ms'),
                    'audio_length': episode.get('audio_length_sec'),
                    'link': episode.get('listennotes_url')
                })

            print(f"✅ 找到 {len(results)} 个相关集数")
            return results

        return []

    def get_best_episodes(self, podcast_id: str = JRE_PODCAST_ID) -> List[Dict]:
        """获取最热门的集数"""
        print(f"⭐ 获取热门集数...")

        # 使用搜索功能获取评分最高的
        data = self._request(f"/podcasts/{podcast_id}")

        if data and 'episodes' in data:
            # 按发布时间排序，获取最热门的10集
            # ListenNotes没有直接的"热门"排序，我们用最近10集
            episodes = []
            for ep in data['episodes'][:10]:
                episodes.append({
                    'title': ep.get('title'),
                    'pub_date': datetime.fromtimestamp(ep.get('pub_date_ms', 0) / 1000).strftime('%Y-%m-%d'),
                    'duration_min': ep.get('audio_length_sec', 0) // 60 if ep.get('audio_length_sec') else 0,
                    'link': ep.get('listennotes_url')
                })

            return episodes

        return []


def main():
    """主程序"""
    print("="*70)
    print("🎧 ListenNotes API 播客数据获取器")
    print("="*70)
    print("免费额度: 每月10,000次请求")
    print("注册: https://www.listennotes.com/api/")
    print("="*70)

    # 获取API Key
    api_key = os.environ.get('LISTENNOTES_API_KEY', '')

    if not api_key:
        print("\n⚠️  需要ListenNotes API Key")
        print("\n获取步骤:")
        print("  1. 访问 https://www.listennotes.com/api/")
        print("  2. 注册账号")
        print("  3. 在Dashboard获取API Key")
        print("  4. 设置环境变量: export LISTENNOTES_API_KEY='你的key'")

        api_key = input("\n请输入API Key (或按回车跳过): ").strip()

        if not api_key:
            print("\n❌ 未提供API Key，演示模式...")

            # 演示: 显示可以获取哪些数据
            print("\n" + "="*70)
            print("📋 使用ListenNotes API可以获取的数据:")
            print("="*70)

            demo_data = {
                'podcast_info': {
                    'title': 'The Joe Rogan Experience',
                    'total_episodes': 2639,
                    'listen_score': 95,  # ListenNotes评分
                    'listen_score_global_rank': '前0.01%',
                    'language': 'English',
                    'country': 'United States',
                    'update_frequency': '每周多期',
                    'rss_feed': '可用',
                    'website': 'https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk'
                },
                'episodes': [
                    {'title': '#2454 - Robert Malone, MD', 'duration': 159, 'date': '2026-02-13'},
                    {'title': '#2453 - Evan Hafer', 'duration': 180, 'date': '2026-02-12'},
                    {'title': '#2452 - Roger Avary', 'duration': 191, 'date': '2026-02-11'},
                ],
                'search_capability': [
                    '搜索特定嘉宾',
                    '搜索特定话题',
                    '按日期过滤',
                    '获取相关播客推荐'
                ]
            }

            print("\n播客信息:")
            for k, v in demo_data['podcast_info'].items():
                print(f"  • {k}: {v}")

            print("\n可以搜索:")
            for item in demo_data['search_capability']:
                print(f"  • {item}")

            print("\n💡 建议: 申请免费API Key以获取完整数据")
            return

    # 初始化获取器
    fetcher = ListenNotesFetcher(api_key)

    print("\n" + "="*70)
    print("🎯 获取 Joe Rogan Experience 数据")
    print("="*70)

    # 获取播客信息
    podcast_info = fetcher.get_podcast_info()

    if podcast_info:
        # 保存基本信息
        data = {
            'podcast_info': podcast_info,
            'fetched_at': datetime.now().isoformat()
        }

        # 获取最近集数
        episodes = fetcher.get_all_episodes(limit=50)
        if episodes:
            data['recent_episodes'] = episodes

        # 保存到文件
        filename = f"{OUTPUT_DIR}/data/json/LISTENNOTES_JRE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 数据已保存: {filename}")

        # 搜索示例
        print("\n" + "="*70)
        print("🔍 搜索示例: 查找Elon Musk相关集数")
        print("="*70)
        search_results = fetcher.search_in_podcast("Elon Musk")

        if search_results:
            print(f"\n找到 {len(search_results)} 集:")
            for i, result in enumerate(search_results[:5], 1):
                print(f"  {i}. {result['title'][:60]}...")
    else:
        print("\n❌ 获取失败，请检查API Key是否有效")


if __name__ == "__main__":
    main()
