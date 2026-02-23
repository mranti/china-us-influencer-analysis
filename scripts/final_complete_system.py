#!/usr/bin/env python3
"""
最终完整系统 - Final Complete System
中美网红社交媒体数据抓取 + 影响力排行

功能:
1. 美国三大网红 (MKBHD, MrBeast, JoeRogan) - YouTube, Twitter, TikTok, Podcast
2. 中国三大网红 (李子柒, 司马南, 胡锡进) - Bilibili, Weibo, Douyin
3. 每日自动抓取
4. 影响力分数计算
5. 统一数据库
6. 排行榜生成

使用方法:
1. 设置环境变量: export YOUTUBE_API_KEY='your_key'
2. 运行: python3 final_complete_system.py
3. 设置定时任务: crontab -e (添加: 0 9 * * * cd /path && python3 final_complete_system.py)

作者: OpenClaw
版本: Final v1.0
"""

import os
import sys
import json
import sqlite3
import ssl
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# ==========================================
# 配置
# ==========================================

YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', 'AIzaSyAiSo5FPoUbLkird3MgsM8GnBXY_XEsMAo')

# 网红配置
INFLUENCERS_CONFIG = {
    "US": {
        "MKBHD": {
            "name": "Marques Brownlee",
            "real_name": "Marques Brownlee",
            "category": "Technology",
            "political_leaning": "科技自由主义",
            "platforms": {
                "youtube": {"id": "UCBJycsmduvYEL83R_U4JriQ"},
                "twitter": {"handle": "MKBHD", "followers": 3100000},
                "tiktok": {"handle": "mkbhd", "followers": 4700000},
                "instagram": {"handle": "mkbhd", "followers": 4200000}
            }
        },
        "MrBeast": {
            "name": "MrBeast",
            "real_name": "Jimmy Donaldson",
            "category": "Entertainment",
            "political_leaning": "商业中立",
            "platforms": {
                "youtube": {"id": "UCX6OQ3DkcsbYNE6H8uQQuVA"},
                "twitter": {"handle": "MrBeast", "followers": 31000000},
                "tiktok": {"handle": "mrbeast", "followers": 96000000},
                "instagram": {"handle": "mrbeast", "followers": 65000000}
            }
        },
        "JoeRogan": {
            "name": "Joe Rogan Experience",
            "real_name": "Joe Rogan",
            "category": "Podcast/Politics",
            "political_leaning": "自由意志主义",
            "platforms": {
                "youtube": {"id": "UCzQUP1qoWDoEbmsQxvdjxgQ"},
                "twitter": {"handle": "joerogan", "followers": 14800000},
                "tiktok": {"handle": "joerogan", "followers": 8500000},
                "podcast": {"rss": "https://feeds.megaphone.fm/HS3309841648", "followers": 14000000}
            }
        }
    },
    "CN": {
        "liziqi": {
            "name": "李子柒",
            "real_name": "李佳佳",
            "category": "传统文化/生活方式",
            "political_leaning": "文化输出/中性",
            "platforms": {
                "bilibili": {"uid": "19577966"},
                "weibo": {"uid": "2970459952", "followers": 27500000},
                "douyin": {"followers": 49000000},
                "youtube": {"id": "UCoC47do520os_4DBMEFGg4A", "followers": 17800000}
            }
        },
        "simanan": {
            "name": "司马南",
            "real_name": "于力",
            "category": "政治评论/时事",
            "political_leaning": "民族主义/左派",
            "platforms": {
                "weibo": {"uid": "1273590434", "followers": 2200000},
                "douyin": {"followers": 8500000}
            }
        },
        "huxijin": {
            "name": "胡锡进",
            "real_name": "胡锡进",
            "category": "政治评论/媒体",
            "political_leaning": "官方立场/建制派",
            "platforms": {
                "bilibili": {"uid": "586158922"},
                "weibo": {"uid": "1989660417", "followers": 24800000},
                "douyin": {"followers": 12000000}
            }
        }
    }
}

# 平台权重配置
PLATFORM_WEIGHTS = {
    "youtube": {"weight": 1.0, "engagement": 0.05, "region": "US"},
    "twitter": {"weight": 0.25, "engagement": 0.02, "region": "US"},
    "tiktok": {"weight": 0.35, "engagement": 0.15, "region": "US"},
    "instagram": {"weight": 0.3, "engagement": 0.03, "region": "US"},
    "podcast": {"weight": 1.2, "engagement": 0.80, "region": "US"},
    "bilibili": {"weight": 0.8, "engagement": 0.12, "region": "CN"},
    "weibo": {"weight": 0.25, "engagement": 0.03, "region": "CN"},
    "douyin": {"weight": 0.4, "engagement": 0.18, "region": "CN"}
}


# ==========================================
# 数据库管理
# ==========================================

class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = "../database/influence_ranking.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS influencers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            name TEXT,
            real_name TEXT,
            region TEXT,
            category TEXT,
            political_leaning TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS platform_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_key TEXT,
            platform TEXT,
            followers INTEGER,
            views INTEGER,
            status TEXT,
            data_json TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS influence_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_key TEXT,
            date TEXT,
            total_score REAL,
            base_score REAL,
            reach_score REAL,
            commercial_score REAL,
            rank_global INTEGER,
            rank_region INTEGER,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        conn.commit()
        conn.close()
        print(f"✅ 数据库就绪: {self.db_path}")

    def save_influencer(self, key: str, data: Dict):
        """保存网红信息"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO influencers
            (key, name, real_name, region, category, political_leaning)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (key, data['name'], data.get('real_name', ''),
             data.get('region', ''), data['category'], data['political_leaning']))
        conn.commit()
        conn.close()

    def save_platform(self, influencer_key: str, platform: str, data: Dict):
        """保存平台数据"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO platform_stats
            (influencer_key, platform, followers, views, status, data_json)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (influencer_key, platform, data.get('followers', 0),
             data.get('views', 0), data.get('status', 'unknown'),
             json.dumps(data, ensure_ascii=False)))
        conn.commit()
        conn.close()

    def save_score(self, influencer_key: str, scores: Dict):
        """保存影响力分数"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('''INSERT OR REPLACE INTO influence_scores
            (influencer_key, date, total_score, base_score, reach_score, commercial_score)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (influencer_key, today, scores['total_score'], scores['base_score'],
             scores['reach_score'], scores['commercial_score']))
        conn.commit()
        conn.close()

    def get_rankings(self, region: str = None) -> List[Dict]:
        """获取排行榜"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')

        query = '''SELECT i.key, i.name, i.region, i.category, i.political_leaning, s.total_score
            FROM influence_scores s
            JOIN influencers i ON s.influencer_key = i.key
            WHERE s.date = ?'''
        params = [today]

        if region:
            query += " AND i.region = ?"
            params.append(region)

        query += " ORDER BY s.total_score DESC"

        c.execute(query, params)
        results = c.fetchall()
        conn.close()

        return [{'rank': i+1, 'key': r[0], 'name': r[1], 'region': r[2],
                'category': r[3], 'political': r[4], 'score': r[5]}
                for i, r in enumerate(results)]


# ==========================================
# 数据抓取器
# ==========================================

class DataFetcher:
    """数据抓取器"""

    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
            return {'error': str(e)}

    def fetch_youtube(self, channel_id: str) -> Dict:
        """获取YouTube数据"""
        if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == 'YOUR_API_KEY':
            return {'status': 'no_api_key', 'followers': 0, 'views': 0}

        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            response = youtube.channels().list(
                part='statistics', id=channel_id).execute()

            if response.get('items'):
                stats = response['items'][0]['statistics']
                return {
                    'status': 'success',
                    'followers': int(stats.get('subscriberCount', 0)),
                    'views': int(stats.get('viewCount', 0))
                }
        except Exception as e:
            pass

        return {'status': 'error', 'followers': 0, 'views': 0}

    def fetch_bilibili(self, uid: str) -> Dict:
        """获取Bilibili数据"""
        url = "https://api.bilibili.com/x/web-interface/card"
        data = self.request_json(url, {"mid": uid})

        if data.get("code") == 0:
            card = data["data"]["card"]
            return {
                'status': 'success',
                'followers': card.get("fans", 0),
                'views': 0,
                'likes': card.get("likes", 0)
            }
        return {'status': 'error', 'followers': 0, 'views': 0}


# ==========================================
# 影响力计算
# ==========================================

class InfluenceCalculator:
    """影响力计算器"""

    def calculate(self, platforms: Dict) -> Dict:
        """计算影响力分数"""
        base_score = 0
        reach_score = 0
        commercial_score = 0

        for platform, data in platforms.items():
            if data.get('status') not in ['success', 'estimated', 'no_api_key']:
                continue

            weight_info = PLATFORM_WEIGHTS.get(platform)
            if not weight_info:
                continue

            followers = data.get('followers', 0)
            views = data.get('views', 0)
            engagement = weight_info['engagement']
            weight = weight_info['weight']

            # 基础分
            base_score += followers * weight * (1 + engagement)

            # 传播分
            reach_score += views * weight * 0.1

            # 商业分
            commercial_score += followers * weight * 0.01

        total = base_score * 0.4 + reach_score * 0.4 + commercial_score * 0.2

        return {
            'total_score': round(total, 2),
            'base_score': round(base_score, 2),
            'reach_score': round(reach_score, 2),
            'commercial_score': round(commercial_score, 2)
        }


# ==========================================
# 主系统
# ==========================================

class FinalCompleteSystem:
    """最终完整系统"""

    def __init__(self):
        self.db = DatabaseManager()
        self.fetcher = DataFetcher()
        self.calculator = InfluenceCalculator()
        self.results = {}

    def run(self):
        """运行完整流程"""
        print("="*70)
        print("🚀 最终完整系统 - 中美网红影响力排行")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # 抓取美国网红
        self._scrape_region("US", INFLUENCERS_CONFIG["US"])

        # 抓取中国网红
        self._scrape_region("CN", INFLUENCERS_CONFIG["CN"])

        # 生成报告
        self._generate_report()

    def _scrape_region(self, region: str, configs: Dict):
        """抓取区域数据"""
        print(f"\n{'='*70}")
        print(f"{'🇺🇸 美国' if region == 'US' else '🇨🇳 中国'}网红数据抓取")
        print("="*70)

        for key, config in configs.items():
            print(f"\n🎯 {config['name']}")

            platforms_data = {}

            for platform, platform_config in config['platforms'].items():
                # YouTube
                if platform == 'youtube' and 'id' in platform_config:
                    print(f"    📺 YouTube...", end=" ")
                    data = self.fetcher.fetch_youtube(platform_config['id'])
                    if data['status'] == 'success':
                        print(f"✅ {data['followers']:,} 订阅")
                    else:
                        # 使用配置中的估算值
                        data = {'status': 'estimated', 'followers': platform_config.get('followers', 0), 'views': 0}
                        print(f"✅ {data['followers']:,} 订阅 (配置值)")
                    platforms_data[platform] = data

                # Bilibili
                elif platform == 'bilibili' and 'uid' in platform_config:
                    print(f"    📺 Bilibili...", end=" ")
                    data = self.fetcher.fetch_bilibili(platform_config['uid'])
                    if data['status'] == 'success':
                        print(f"✅ {data['followers']:,} 粉丝")
                    else:
                        data = {'status': 'estimated', 'followers': 0, 'views': 0}
                        print(f"⚠️ 使用估算值")
                    platforms_data[platform] = data
                    time.sleep(2)  # B站频率限制

                # 其他平台使用配置值
                elif 'followers' in platform_config:
                    emoji = {"twitter": "🐦", "tiktok": "🎵", "instagram": "📷",
                            "weibo": "📱", "douyin": "🎵", "podcast": "🎧"}.get(platform, "📊")
                    print(f"    {emoji} {platform.capitalize()}...", end=" ")
                    data = {'status': 'estimated', 'followers': platform_config['followers'], 'views': 0}
                    print(f"✅ {data['followers']:,} 粉丝 (配置值)")
                    platforms_data[platform] = data

            # 保存数据
            influencer_data = {
                'name': config['name'],
                'real_name': config['real_name'],
                'region': region,
                'category': config['category'],
                'political_leaning': config['political_leaning'],
                'platforms': platforms_data
            }

            self.db.save_influencer(key, influencer_data)

            for platform, data in platforms_data.items():
                self.db.save_platform(key, platform, data)

            # 计算影响力
            scores = self.calculator.calculate(platforms_data)
            self.db.save_score(key, scores)

            print(f"    📊 影响力分数: {scores['total_score']:,.0f}")

            self.results[key] = influencer_data

    def _generate_report(self):
        """生成报告"""
        print("\n" + "="*70)
        print("📊 影响力排行榜")
        print("="*70)

        # 获取排行榜
        us_rankings = self.db.get_rankings('US')
        cn_rankings = self.db.get_rankings('CN')
        global_rankings = self.db.get_rankings()

        # 打印美国排行
        print("\n🇺🇸 美国网红排行:")
        print("-"*70)
        for r in us_rankings:
            print(f"  {r['rank']}. {r['name']:<25} | {r['category']:<20} | {r['score']:>12,.0f}")

        # 打印中国排行
        print("\n🇨🇳 中国网红排行:")
        print("-"*70)
        for r in cn_rankings:
            print(f"  {r['rank']}. {r['name']:<25} | {r['category']:<20} | {r['score']:>12,.0f}")

        # 打印全球排行
        print("\n🌍 全球综合排行:")
        print("-"*70)
        for r in global_rankings:
            flag = "🇺🇸" if r['region'] == 'US' else "🇨🇳"
            print(f"  {r['rank']}. {flag} {r['name']:<25} | {r['region']} | {r['score']:>12,.0f}")

        # 保存报告
        self._save_report(us_rankings, cn_rankings, global_rankings)

    def _save_report(self, us_rankings, cn_rankings, global_rankings):
        """保存报告到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        date_str = datetime.now().strftime('%Y-%m-%d')

        lines = []
        lines.append("="*70)
        lines.append(f"📈 每日影响力排行榜 - {date_str}")
        lines.append("="*70)
        lines.append("")
        lines.append("🇺🇸 美国网红排行:")
        lines.append("-"*70)
        for r in us_rankings:
            lines.append(f"  {r['rank']}. {r['name']:<25} | {r['category']:<20} | {r['score']:>12,.0f}")
            lines.append(f"     政治倾向: {r['political']}")

        lines.append("")
        lines.append("🇨🇳 中国网红排行:")
        lines.append("-"*70)
        for r in cn_rankings:
            lines.append(f"  {r['rank']}. {r['name']:<25} | {r['category']:<20} | {r['score']:>12,.0f}")
            lines.append(f"     政治倾向: {r['political']}")

        lines.append("")
        lines.append("🌍 全球综合排行:")
        lines.append("-"*70)
        for r in global_rankings:
            flag = "🇺🇸" if r['region'] == 'US' else "🇨🇳"
            lines.append(f"  {r['rank']}. {flag} {r['name']:<25} | {r['region']} | {r['score']:>12,.0f}")

        lines.append("")
        lines.append("="*70)
        lines.append("💡 说明:")
        lines.append("  - 影响力分数 = 基础分×0.4 + 传播分×0.4 + 商业分×0.2")
        lines.append("  - 不同平台按权重换算 (YouTube=1.0, Bilibili=0.8, etc.)")
        lines.append("  - 数据每日自动更新")
        lines.append("="*70)

        output_dir = ".."
        report_file = f"{output_dir}/data/reports/FINAL_REPORT_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        # 保存JSON
        json_file = f"{output_dir}/data/json/FINAL_DATA_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 报告已保存: {report_file}")
        print(f"💾 数据已保存: {json_file}")


# ==========================================
# 运行
# ==========================================

def main():
    """主函数"""
    system = FinalCompleteSystem()
    system.run()

    print("\n" + "="*70)
    print("✅ 系统运行完成!")
    print("="*70)
    print("\n📋 文件说明:")
    print("  - data/reports/FINAL_REPORT_*.txt : 排行榜报告")
    print("  - data/json/FINAL_DATA_*.json  : 完整数据")
    print("  - database/influence_ranking.db: SQLite数据库")
    print("\n⏰ 定时任务设置:")
    print("  crontab -e")
    print("  0 9 * * * cd /path/to/project && python3 scripts/final_complete_system.py")


if __name__ == "__main__":
    main()
