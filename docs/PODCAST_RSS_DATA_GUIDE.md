# Podcast RSS Feed 数据获取指南

## 概述

通过 **RSS Feed** 可以免费获取Joe Rogan Experience播客的完整数据，无需API Key，完全免费！

---

## 能获取哪些数据？

### 1. 播客元数据
```json
{
  "podcast_name": "The Joe Rogan Experience",
  "podcast_description": "完整描述...",
  "total_episodes": 2639,
  "rss_url": "https://feeds.feedburner.com/JoeRoganExperience"
}
```

### 2. 单集详细数据 (每集)
```json
{
  "title": "#2454 - Robert Malone, MD",
  "published": "Fri, 13 Feb 2026 18:00:00",
  "description": "完整节目描述...",
  "duration_minutes": 159,
  "duration_seconds": 9532,
  "link": "",
  "guest": "Robert Malone, MD"
}
```

### 3. 数据字段说明

| 字段 | 说明 | 示例 |
|:---|:---|:---|
| `title` | 节目标题 | "#2454 - Robert Malone, MD" |
| `published` | 发布日期 | "Fri, 13 Feb 2026 18:00:00" |
| `description` | 节目描述 | 嘉宾介绍、话题概述 |
| `duration` | 时长 | 9532秒 (约159分钟) |
| `link` | 音频链接 | 可直接播放的MP3链接 |
| `guest` | 嘉宾姓名 | 从标题提取 |

---

## 使用的RSS源

### 主RSS源 (推荐)
```
https://feeds.feedburner.com/JoeRoganExperience
```

### 备用RSS源
```
https://rss.art19.com/the-joe-rogan-experience
```

---

## 数据获取示例

### 最新10集数据

| 集数 | 嘉宾 | 发布日期 | 时长 |
|:---:|:---|:---:|---:|
| #2454 | Robert Malone, MD | 2026-02-13 | 159分钟 |
| #2453 | Evan Hafer | 2026-02-12 | 180分钟 |
| #2452 | Roger Avary | 2026-02-11 | 191分钟 |
| #2451 | Cheryl Hines | 2026-02-10 | 190分钟 |
| #2450 | Tommy Wood | 2026-02-06 | 137分钟 |
| #2449 | Raul Bilecky | 2026-02-05 | 157分钟 |
| #2448 | Andrew Doyle | 2026-02-04 | 165分钟 |
| #2447 | Mike Benz | 2026-02-03 | 165分钟 |
| #2446 | Greg Fitzsimmons | 2026-01-31 | 163分钟 |
| #2445 | Bert Kreischer | 2026-01-29 | 173分钟 |

**平均时长**: 167分钟 (约2.8小时)

---

## 如何使用

### 方法1: 直接运行程序
```bash
cd /Users/olivia/Library/CloudStorage/Dropbox/哈佛
python3 complete_report_with_podcast.py
```

### 方法2: 单独获取Podcast数据
```python
import feedparser

rss_url = "https://feeds.feedburner.com/JoeRoganExperience"
feed = feedparser.parse(rss_url)

# 获取总集数
total_episodes = len(feed.entries)

# 获取最新一集
latest = feed.entries[0]
print(f"标题: {latest.title}")
print(f"发布: {latest.published}")
print(f"时长: {latest.itunes_duration}")
print(f"描述: {latest.summary[:200]}")
```

---

## 数据限制

### ❌ RSS Feed无法提供的数据

| 数据项 | 说明 | 替代方案 |
|:---|:---|:---|
| **听众数** | RSS不返回订阅者数量 | 使用估算值1100万 |
| **下载量** | 无法追踪播放/下载次数 | 无 |
| **评分** | 无评分数据 | 无 |
| **评论** | 无评论数据 | 无 |
| **地理位置** | 无听众位置数据 | 无 |

### ⚠️ 限制原因
RSS Feed是内容分发协议，设计初衷就是不追踪用户数据，保护隐私。

---

## 与其他数据对比

### YouTube vs Podcast

| 数据 | YouTube | Podcast RSS |
|:---|:---:|:---:|
| 订阅者/听众 | ✅ 2070万 | ⚠️ 估算1100万 |
| 观看/下载数 | ✅ 有 | ❌ 无 |
| 视频/音频 | ✅ 视频 | ✅ 音频 |
| 评论数 | ✅ 有 | ❌ 无 |
| 点赞数 | ✅ 有 | ❌ 无 |
| 发布日期 | ✅ 有 | ✅ 有 |
| 时长 | ✅ 有 | ✅ 有 |
| 标题/描述 | ✅ 有 | ✅ 有 |

---

## 代码实现

### 核心代码 (fetch_jre_podcast.py)

```python
import feedparser

rss_url = "https://feeds.feedburner.com/JoeRoganExperience"
feed = feedparser.parse(rss_url)

episodes = []
for entry in feed.entries[:10]:
    episode = {
        'title': entry.title,
        'published': entry.published,
        'description': entry.summary[:300],
        'duration': entry.itunes_duration
    }
    episodes.append(episode)

print(f"获取到 {len(feed.entries)} 集")
```

---

## 总结

### ✅ Podcast RSS能提供的免费数据
1. **完整节目列表** - 2639集
2. **每集标题** - 包含集数和嘉宾
3. **发布日期** - 精确到秒
4. **节目描述** - 嘉宾介绍和话题
5. **音频时长** - 精确到秒
6. **音频链接** - 可直接播放

### ❌ 无法获取的数据
1. **听众数量** - 需使用估算值
2. **播放数据** - RSS协议不追踪
3. **互动数据** - 无评论/点赞

### 💡 建议
- **RSS Feed**最适合获取：节目内容、发布时间、时长
- **YouTube数据**补充：观看量、互动数据
- **结合使用**可获得最完整的JRE数据分析

---

*文档更新: 2026-02-15*
*RSS源测试状态: ✅ 正常工作*
