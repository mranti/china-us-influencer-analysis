#!/usr/bin/env python3
"""
X/Twitter 最后尝试 - 创意方法
使用搜索引擎、社交媒体聚合等非常规手段
"""

import urllib.request
import urllib.parse
import re
import ssl
import json
from datetime import datetime

def try_duckduckgo(username: str):
    """使用 DuckDuckGo 搜索"""
    print("    尝试 DuckDuckGo...", end=" ")
    try:
        query = f"twitter.com/{username} followers"
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=15, context=context) as r:
            html = r.read().decode('utf-8', errors='ignore')

        # 查找粉丝数
        patterns = [
            rf'{username}.*?([\d,.]+[KMB]?)\s*followers',
            rf'@?{username}.*?([\d,.]+)\s*followers',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                count = match.group(1).replace(',', '')
                if 'K' in count:
                    return int(float(count.replace('K', '')) * 1000)
                elif 'M' in count:
                    return int(float(count.replace('M', '')) * 1000000)
                else:
                    return int(float(count))
    except Exception as e:
        print(f"❌")
    return None

def try_bing_search(username: str):
    """使用 Bing 搜索"""
    print("    尝试 Bing...", end=" ")
    try:
        query = f"site:twitter.com {username} followers"
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        req = urllib.request.Request(url, headers=headers)

        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=15, context=context) as r:
            html = r.read().decode('utf-8', errors='ignore')

        # 查找模式
        patterns = [
            rf'{username}.*?([\d,.]+[KMB]?) followers',
            rf'([\d,.]+)\s*followers.*?{username}',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                count = match.group(1).replace(',', '')
                if 'K' in count:
                    return int(float(count.replace('K', '')) * 1000)
                elif 'M' in count:
                    return int(float(count.replace('M', '')) * 1000000)
                else:
                    try:
                        return int(float(count))
                    except:
                        pass
    except Exception as e:
        print(f"❌")
    return None

def try_yandex_search(username: str):
    """使用 Yandex 搜索 (俄罗斯搜索引擎)"""
    print("    尝试 Yandex...", end=" ")
    try:
        url = f"https://yandex.com/search/?text=twitter.com/{username}+followers"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=15, context=context) as r:
            html = r.read().decode('utf-8', errors='ignore')

        # 查找
        match = re.search(rf'{username}.*?([\d,.]+[KMB]?) followers', html, re.IGNORECASE)
        if match:
            count = match.group(1).replace(',', '')
            if 'K' in count:
                return int(float(count.replace('K', '')) * 1000)
            elif 'M' in count:
                return int(float(count.replace('M', '')) * 1000000)
            else:
                try:
                    return int(float(count))
                except:
                    pass
    except Exception as e:
        print(f"❌")
    return None

def try_openalex(username: str):
    """使用 OpenAlex 学术数据库 (可能收录研究者)"""
    print("    尝试 OpenAlex...", end=" ")
    try:
        url = f"https://api.openalex.org/authors?search={username}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=10, context=context) as r:
            data = json.loads(r.read().decode('utf-8'))

        # 查找 Twitter 信息
        for result in data.get('results', []):
            twitter = result.get('ids', {}).get('twitter')
            if twitter and username.lower() in twitter.lower():
                # 如果找到，返回估算值
                works = result.get('works_count', 0)
                return None  # OpenAlex 不提供粉丝数
    except Exception as e:
        print(f"❌")
    return None

def try_wikipedia(username: str, name: str):
    """从 Wikipedia 信息框获取"""
    print("    尝试 Wikipedia...", end=" ")
    try:
        # 尝试查找 Wikipedia 页面
        search_terms = [name, username]

        for term in search_terms:
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(term)}&format=json"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Research Project)'
            }
            req = urllib.request.Request(url, headers=headers)

            context = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=10, context=context) as r:
                data = json.loads(r.read().decode('utf-8'))

            # 查找相关页面
            for result in data.get('query', {}).get('search', []):
                page_title = result.get('title', '')

                # 获取页面内容
                page_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={urllib.parse.quote(page_title)}&rvprop=content&format=json"
                req2 = urllib.request.Request(page_url, headers=headers)

                with urllib.request.urlopen(req2, timeout=10, context=context) as r2:
                    page_data = json.loads(r2.read().decode('utf-8'))

                # 在页面内容中查找 Twitter 粉丝数
                pages = page_data.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    revisions = page_info.get('revisions', [])
                    if revisions:
                        content = revisions[0].get('*', '')
                        # 查找 twitter followers 模式
                        match = re.search(r'twitter.*?followers?.*?=\s*([\d,]+)', content, re.IGNORECASE)
                        if match:
                            return int(match.group(1).replace(',', ''))
    except Exception as e:
        print(f"❌")
    return None

def crawl_x_free(username: str, name: str = None):
    """尝试所有最后的免费方法"""
    print(f"\n🐦 最后尝试: @{username}")
    print("-" * 50)

    results = []

    # 尝试各种方法
    methods = [
        ("DuckDuckGo", try_duckduckgo),
        ("Bing", try_bing_search),
        ("Yandex", try_yandex_search),
    ]

    if name:
        methods.append(("Wikipedia", lambda u: try_wikipedia(u, name)))

    for method_name, method_func in methods:
        result = method_func(username)
        if result:
            print(f"✅ {result:,} followers")
            results.append({
                'method': method_name,
                'followers': result
            })
        else:
            print(f"❌")

    return results

# 运行测试
if __name__ == "__main__":
    print("="*60)
    print("🚀 X/Twitter 最后尝试 - 创意方法")
    print("="*60)

    accounts = [
        ("MKBHD", "Marques Brownlee"),
        ("MrBeast", "MrBeast"),
        ("joerogan", "Joe Rogan"),
    ]

    for username, name in accounts:
        results = crawl_x_free(username, name)

        if results:
            print(f"\n✅ @{username} 成功获取数据:")
            for r in results:
                print(f"   {r['method']}: {r['followers']:,}")
        else:
            print(f"\n❌ @{username} 所有方法均失败")

        print()

    print("="*60)
    print("⚠️  结论: Twitter/X 的反爬过于强大")
    print("   免费方法已无法获取数据")
    print("="*60)
