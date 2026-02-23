#!/usr/bin/env python3
"""
X/Twitter 免费爬虫 - 终极尝试
尝试所有可能的免费方法，不依赖API
"""

import os
import sys
import json
import re
import ssl
import time
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional

class XFreeCrawler:
    """X/Twitter 免费爬虫"""

    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.results = []

    def _get_headers(self, mobile=False) -> Dict:
        """获取请求头"""
        if mobile:
            return {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
        else:
            return {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

    def _parse_number(self, text: str) -> int:
        """解析数字"""
        if not text:
            return 0
        text = text.lower().replace(',', '').strip()
        multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000}
        for suffix, multiplier in multipliers.items():
            if suffix in text:
                try:
                    return int(float(text.replace(suffix, '').strip()) * multiplier)
                except:
                    return 0
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            try:
                return int(float(numbers[0]))
            except:
                pass
        return 0

    # ============ 方法1: 最新Nitter镜像 ============
    def try_nitter_mirrors(self, username: str) -> Dict:
        """尝试最新的Nitter镜像"""
        print(f"    尝试 Nitter 镜像...")

        # 2024年最新Nitter镜像列表
        nitter_instances = [
            "https://nitter.net",
            "https://nitter.privacydev.net",
            "https://nitter.freedit.eu",
            "https://nitter.poast.org",
            "https://nitter.datura.network",
            "https://nitter.projectsegfault.com",
            "https://nitter.perennialte.ch",
            "https://nitter.moomoo.me",
            "https://nitter.42l.fr",
            "https://nitter.nixnet.services",
            "https://nitter.pussthecat.org",
            "https://nitter.nohost.network",
            "https://nitter.tux.pizza",
            "https://nitter.foss.frederic.moe",
            "https://nitter.eu",
            "https://nitter.cz",
            "https://nitter.it",
            "https://nitter.es",
            "https://nitter.se",
            "https://nitter.nl",
        ]

        for instance in nitter_instances:
            try:
                url = f"{instance}/{username}"
                req = urllib.request.Request(url, headers=self._get_headers())

                with urllib.request.urlopen(req, timeout=10, context=self.ssl_context) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                # 检查是否被拦截
                if any(x in html.lower() for x in ['rate limit', 'captcha', 'blocked', 'cloudflare']):
                    continue

                # 提取粉丝数
                followers_match = re.search(r'([\d,.]+[KMBk]?)\s*followers?', html, re.IGNORECASE)
                followers = self._parse_number(followers_match.group(1)) if followers_match else 0

                # 提取推文数
                tweets_match = re.search(r'([\d,.]+[KMBk]?)\s*tweets?', html, re.IGNORECASE)
                tweets = self._parse_number(tweets_match.group(1)) if tweets_match else 0

                # 提取最近推文
                recent_tweets = self._extract_tweets_from_nitter(html)

                if followers > 0:
                    return {
                        'status': 'success',
                        'method': 'nitter',
                        'source': instance,
                        'followers': followers,
                        'tweets_count': tweets,
                        'recent_tweets': recent_tweets,
                        'url': url
                    }

            except Exception as e:
                continue

        return {'status': 'failed', 'method': 'nitter', 'error': 'All mirrors blocked'}

    def _extract_tweets_from_nitter(self, html: str) -> List[Dict]:
        """从Nitter HTML提取推文"""
        tweets = []
        try:
            # Nitter推文通常在.timeline-item中
            tweet_pattern = r'<div class="timeline-item"[^>]*>.*?<div class="tweet-content"[^>]*>(.*?)</div>.*?</div>'
            matches = re.findall(tweet_pattern, html, re.DOTALL)

            for match in matches[:10]:
                # 提取文本
                text_match = re.search(r'<div class="tweet-content media-body"[^>]*>(.*?)</div>', match, re.DOTCASE)
                if text_match:
                    text = re.sub(r'<[^>]+>', '', text_match.group(1))
                    tweets.append({
                        'text': text[:200],
                        'date': 'unknown'
                    })
        except:
            pass
        return tweets

    # ============ 方法2: RSS桥接服务 ============
    def try_rss_bridges(self, username: str) -> Dict:
        """尝试RSS桥接服务"""
        print(f"    尝试 RSS 桥接...")

        rss_services = [
            f"https://r.jina.ai/http://twitter.com/{username}",
            f"https://r.jina.ai/http://nitter.net/{username}",
            f"https://r.jina.ai/http://x.com/{username}",
        ]

        for url in rss_services:
            try:
                req = urllib.request.Request(url, headers=self._get_headers())

                with urllib.request.urlopen(req, timeout=15, context=self.ssl_context) as response:
                    content = response.read().decode('utf-8', errors='ignore')

                # 尝试提取粉丝数
                follower_patterns = [
                    r'([\d,.]+[KMBk]?)\s*followers?',
                    r'Followers?\s*:?\s*([\d,.]+[KMBk]?)',
                    r'([\d,]+)\s*followers',
                ]

                for pattern in follower_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        followers = self._parse_number(match.group(1))
                        if followers > 1000:  # 确保是合理的数字
                            return {
                                'status': 'success',
                                'method': 'rss_bridge',
                                'source': url.split('/')[2],
                                'followers': followers,
                                'content_preview': content[:500],
                                'url': f"https://twitter.com/{username}"
                            }

            except Exception as e:
                continue

        return {'status': 'failed', 'method': 'rss_bridge', 'error': 'No data found'}

    # ============ 方法3: 第三方聚合服务 ============
    def try_third_party_services(self, username: str) -> Dict:
        """尝试第三方聚合服务"""
        print(f"    尝试第三方服务...")

        services = [
            # Social Blade
            f"https://socialblade.com/twitter/user/{username}",
            # SimilarWeb
            f"https://www.similarweb.com/website/twitter.com/#{username}",
        ]

        for url in services:
            try:
                req = urllib.request.Request(url, headers=self._get_headers())

                with urllib.request.urlopen(req, timeout=15, context=self.ssl_context) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                # Social Blade 模式
                if 'socialblade' in url:
                    match = re.search(r'([\d,]+)\s*Followers', html)
                    if match:
                        followers = int(match.group(1).replace(',', ''))
                        return {
                            'status': 'success',
                            'method': 'socialblade',
                            'followers': followers,
                            'url': url
                        }

            except Exception as e:
                continue

        return {'status': 'failed', 'method': 'third_party', 'error': 'Services unavailable'}

    # ============ 方法4: 直接网页抓取 (移动端) ============
    def try_mobile_web(self, username: str) -> Dict:
        """尝试移动端网页"""
        print(f"    尝试移动端网页...")

        urls = [
            f"https://mobile.twitter.com/{username}",
            f"https://m.twitter.com/{username}",
            f"https://twitter.com/i/user/{username}",
        ]

        for url in urls:
            try:
                req = urllib.request.Request(url, headers=self._get_headers(mobile=True))

                with urllib.request.urlopen(req, timeout=10, context=self.ssl_context) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                # 尝试提取粉丝数
                patterns = [
                    r'([\d,.]+[KMBk]?)\s*[Ff]ollowers?',
                    r'"followers_count":(\d+)',
                    r'"user_followers":(\d+)',
                ]

                for pattern in patterns:
                    match = re.search(pattern, html)
                    if match:
                        followers = self._parse_number(match.group(1))
                        if followers > 1000:
                            return {
                                'status': 'success',
                                'method': 'mobile_web',
                                'followers': followers,
                                'url': url
                            }

            except Exception as e:
                continue

        return {'status': 'failed', 'method': 'mobile_web', 'error': 'Blocked or changed'}

    # ============ 方法5: 缓存服务 ============
    def try_cache_services(self, username: str) -> Dict:
        """尝试缓存服务"""
        print(f"    尝试缓存服务...")

        cache_urls = [
            f"https://webcache.googleusercontent.com/search?q=twitter.com/{username}",
            f"https://web.archive.org/web/2024*/https://twitter.com/{username}",
        ]

        for url in cache_urls:
            try:
                req = urllib.request.Request(url, headers=self._get_headers())

                with urllib.request.urlopen(req, timeout=15, context=self.ssl_context) as response:
                    html = response.read().decode('utf-8', errors='ignore')

                # 提取粉丝数
                match = re.search(r'([\d,.]+[KMBk]?)\s*[Ff]ollowers?', html)
                if match:
                    followers = self._parse_number(match.group(1))
                    if followers > 1000:
                        return {
                            'status': 'success',
                            'method': 'cache',
                            'source': 'google_cache' if 'google' in url else 'wayback',
                            'followers': followers,
                            'note': 'Data may be outdated',
                            'url': url
                        }

            except Exception as e:
                continue

        return {'status': 'failed', 'method': 'cache', 'error': 'No cached data'}

    # ============ 主抓取函数 ============
    def fetch(self, username: str) -> Dict:
        """尝试所有免费方法"""
        print(f"\n{'='*60}")
        print(f"🐦 抓取 X/Twitter: @{username}")
        print('='*60)

        methods = [
            ("Nitter镜像", self.try_nitter_mirrors),
            ("RSS桥接", self.try_rss_bridges),
            ("第三方服务", self.try_third_party_services),
            ("移动端网页", self.try_mobile_web),
            ("缓存服务", self.try_cache_services),
        ]

        for method_name, method_func in methods:
            print(f"\n  方法: {method_name}")
            result = method_func(username)

            if result.get('status') == 'success':
                print(f"  ✅ 成功!")
                print(f"     粉丝: {result.get('followers', 0):,}")
                print(f"     方法: {result.get('method', 'unknown')}")
                if result.get('source'):
                    print(f"     来源: {result.get('source')}")
                return result
            else:
                print(f"  ❌ {result.get('error', 'Failed')}")

        # 全部失败
        print(f"\n  ⚠️  所有免费方法都失败了")
        return {
            'status': 'failed',
            'followers': 0,
            'error': 'All free methods failed. X/Twitter anti-scraping is too strong.'
        }


def main():
    """主函数"""
    print("="*70)
    print("🚀 X/Twitter 免费爬虫 - 终极尝试")
    print("尝试所有可能的免费方法")
    print("="*70)

    usernames = ['MKBHD', 'MrBeast', 'joerogan']
    crawler = XFreeCrawler()
    results = []

    for username in usernames:
        result = crawler.fetch(username)
        results.append({
            'username': username,
            'result': result
        })
        time.sleep(2)  # 礼貌延迟

    # 保存结果
    output_dir = ".."
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/data/json/X_CRAWLER_RESULTS_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 摘要
    print("\n" + "="*70)
    print("📊 结果摘要")
    print("="*70)

    for r in results:
        status = "✅" if r['result']['status'] == 'success' else "❌"
        followers = r['result'].get('followers', 0)
        method = r['result'].get('method', 'failed')
        print(f"{status} @{r['username']:<15} | {followers:>12,} | {method}")

    print(f"\n💾 结果已保存: {filename}")
    print("="*70)


if __name__ == "__main__":
    main()
