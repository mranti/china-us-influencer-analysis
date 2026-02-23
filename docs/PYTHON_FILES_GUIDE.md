# Python 程序文件说明

所有爬虫和报告生成程序的说明文档。

---

## 🌟 主要程序（推荐使用）

### 1. `complete_full_platform_report.py` (美国网红)
**美国网红完整5平台报告生成器** ⭐ **推荐使用**
- **功能**: 整合 YouTube + Podcast + X/Twitter + TikTok + Instagram
- **数据质量**:
  - ✅ YouTube: 真实API数据
  - ✅ Instagram: 真实爬取数据 (instaloader)
  - ✅ TikTok: 真实爬取数据
  - ⚠️ Podcast: 估算值 (Spotify独家)
  - ⚠️ X/Twitter: 估算值 (被封)
- **输出**: 完整的TXT报告 + JSON数据
- **运行**: `python3 complete_full_platform_report.py`

### 2. `china_full_platform_report.py` (中国网红) ⭐ NEW
**中国网红完整5平台报告生成器** ⭐ **推荐使用**
- **功能**: 整合 Bilibili + Weibo + Douyin + 微信公众号 + 微信视频号
- **网红**: 李子柒, 司马南, 胡锡进
- **数据质量**:
  - ✅ Bilibili: 李子柒真实API数据 (1000万+粉丝)
  - ⚠️ Bilibili: 司马南/胡锡进估算 (UID待确认)
  - ⚠️ Weibo: 估算值 (需要登录)
  - ⚠️ Douyin: 估算值 (需要签名算法)
  - ⚠️ 微信公众号/视频号: 估算值 (无公开API)
- **输出**: 完整的TXT报告 + JSON数据
- **运行**: `python3 china_full_platform_report.py`

---

## 📊 其他核心程序

### 2. `final_complete_system.py`
**完整整合系统 (中美网红)**
- 同时处理美国3网红 + 中国3网红
- 平台: YouTube, Bilibili, 估算值
- 包含影响力分数计算和排名

### 3. `multi_platform_scraper.py`
**美国网红多平台爬虫**
- 抓取 MKBHD, MrBeast, Joe Rogan
- 平台: YouTube, Twitter/X, TikTok, Instagram
- YouTube使用API，其他使用估算或爬取

### 4. `china_multi_platform.py`
**中国网红多平台爬虫**
- 抓取 李子柒, 司马南, 胡锡进
- 平台: Bilibili (真实API), 微博/抖音 (估算)
- Bilibili数据100%真实

---

## 🔧 专项爬虫程序

### 5. `crawler_real_data_v2.py`
**真实数据爬虫 (Instagram/TikTok成功版)**
- ✅ Instagram: 100%成功率 (instaloader)
- ✅ TikTok: 100%成功率 (网页抓取)
- ❌ X/Twitter: 被封，无法获取
- 输出详细的JSON数据包括最近帖子

### 6. `x_free_crawler.py`
**X/Twitter 免费方法尝试**
- 尝试20+种免费方法爬取Twitter
- 包括: Nitter镜像, RSS桥接, 第三方服务, 缓存服务
- **结论**: 所有免费方法均失败

### 7. `x_last_resort.py`
**X/Twitter 最后尝试**
- 尝试创意方法: 搜索引擎, Wikipedia, 学术数据库
- DuckDuckGo, Bing, Yandex, OpenAlex
- **结论**: 无法获取真实数据

---

## 📈 生成的报告文件

运行程序后会生成以下类型的文件:

| 文件类型 | 命名格式 | 内容 |
|:---|:---|:---|
| 完整报告 | `COMPLETE_FULL_REPORT_YYYYMMDD_HHMMSS.txt` | 人可读的详细报告 |
| JSON数据 | `COMPLETE_FULL_DATA_YYYYMMDD_HHMMSS.json` | 结构化数据 |
| 真实数据 | `REAL_DATA_V2_YYYYMMDD_HHMMSS.json` | Instagram/TikTok真实数据 |

---

## 🚀 快速开始

### 运行完整5平台报告:
```bash
cd "/Users/olivia/Library/CloudStorage/Dropbox/哈佛"
python3 complete_full_platform_report.py
```

### 运行美国网红爬虫:
```bash
python3 multi_platform_scraper.py
```

### 运行中国网红爬虫 (完整版):
```bash
python3 china_full_platform_report.py
```

### 运行中国网红爬虫 (简化版):
```bash
python3 china_multi_platform.py
```

---

## ⚠️ 已知限制

### 美国平台
| 平台 | 状态 | 说明 |
|:---|:---|:---|
| X/Twitter | ❌ 无法获取 | 所有免费方法被封，只能使用估算值 |
| Podcast | ⚠️ 估算 | Spotify独家数据，无法直接API获取 |

### 中国平台
| 平台 | 状态 | 说明 |
|:---|:---|:---|
| Bilibili (李子柒) | ✅ 真实数据 | 免费API，1000万+粉丝实时数据 |
| Bilibili (其他) | ⚠️ 估算 | 司马南/胡锡进UID待确认 |
| 微博 | ⚠️ 估算 | 需要登录，数据基于公开信息估算 |
| 抖音 | ⚠️ 估算 | 需要签名算法，数据基于互动率估算 |
| 微信公众号 | ⚠️ 估算 | 无公开API，基于行业数据估算 |
| 微信视频号 | ⚠️ 估算 | 无公开API，基于行业数据估算 |

---

## 📁 工作区原始文件位置

所有 `.py` 文件的原始位置:
```
/Users/olivia/.openclaw/workspace/
```

这个文件夹里有全部54个Python文件，哈佛folder里只复制了最核心的7个。

---

*文档生成时间: 2026-02-15*
