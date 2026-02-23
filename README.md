# 中美网红社交媒体数据分析系统

[English](README_EN.md) | 简体中文

一个用于抓取和分析中美两国顶级网红（KOL）多平台社交媒体数据的 Python 项目。

## 📋 项目简介

本项目用于自动化抓取中美网红在多个社交媒体平台的数据，包括：

- **美国网红**: MrBeast、MKBHD、Joe Rogan
- **中国网红**: 李子柒、司马南、胡锡进

**覆盖平台**:
- YouTube、Bilibili、微博、抖音
- Twitter/X、Instagram、TikTok
- Podcast (Spotify)、微信公众号

## 🗂️ 目录结构

```
.
├── .env                        # 环境变量配置文件 (需自行创建)
├── .env.example                # 环境变量配置示例
├── .gitignore                  # Git 忽略文件配置
├── README.md                   # 项目说明文档
│
├── scripts/                    # Python 爬虫和报告脚本
│   ├── youtube_scraper.py      # YouTube 数据抓取
│   ├── china_multi_platform.py # 中国平台数据抓取
│   ├── final_complete_system.py # 完整系统（主入口）
│   └── ...                     # 其他爬虫和报告生成脚本
│
├── data/
│   ├── json/                   # JSON 格式原始数据
│   └── reports/                # 文本格式报告
│
├── database/                   # SQLite 数据库文件
│   ├── influence_ranking.db    # 影响力排行数据库
│   └── ...                     # 其他数据库
│
├── docs/                       # 文档和指南
│   ├── DATA_SERVICES_GUIDE.md  # 数据服务指南
│   ├── PYTHON_FILES_GUIDE.md   # Python 文件说明
│   └── ...                     # 其他文档
│
├── config/                     # 配置文件
│   ├── requirements.txt        # Python 依赖
│   └── influencer_config.json  # 网红配置
│
└── archive/                    # 归档文件
    └── 中美网红.odt            # 原始文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r config/requirements.txt
```

或手动安装核心依赖：

```bash
pip install google-api-python-client instaloader python-dotenv
```

### 2. 配置环境变量

复制示例配置文件并填写你的 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写你的 API Key：

```bash
# 必需: YouTube Data API Key
YOUTUBE_API_KEY=your_youtube_api_key_here

# 可选: ListenNotes API Key (用于播客数据)
LISTENNOTES_API_KEY=your_listennotes_key_here
```

> **获取 YouTube API Key**: 访问 [Google Cloud Console](https://console.cloud.google.com/apis/credentials)，启用 YouTube Data API v3，创建 API 密钥。

### 3. 运行主程序

```bash
# 在项目根目录执行
python3 scripts/final_complete_system.py
```

## 📊 功能模块

### 爬虫模块

| 脚本 | 功能 | 平台 |
|------|------|------|
| `youtube_scraper.py` | YouTube 视频/频道数据 | YouTube |
| `china_multi_platform.py` | 中国网红多平台数据 | Bilibili、微博、抖音 |
| `x_free_crawler.py` | X/Twitter 数据抓取 | Twitter/X |
| `podcast_nuclear_hunter.py` | 播客数据抓取 | Spotify |
| `multi_platform_scraper.py` | 多平台综合抓取 | 全平台 |

### 报告生成模块

| 脚本 | 功能 |
|------|------|
| `complete_full_platform_report.py` | 生成完整全平台报告 |
| `china_full_platform_report.py` | 生成中国网红报告 |
| `free_version_report.py` | 免费版报告（无需 API） |
| `complete_report_with_podcast.py` | 包含播客数据的完整报告 |

## 📈 输出文件说明

### JSON 数据文件 (`data/json/`)

- `COMPLETE_FULL_DATA_*.json` - 完整网红数据
- `CHINA_FULL_DATA_*.json` - 中国网红数据
- `FINAL_DATA_*.json` - 最终综合数据
- `CN_INFLUENCERS_*.json` - 中国网红档案
- `*_COMPLETE_DATA_*.json` - 单个网红完整数据

### 报告文件 (`data/reports/`)

- `COMPLETE_FULL_REPORT_*.txt` - 完整全平台报告
- `CHINA_FULL_REPORT_*.txt` - 中国网红报告
- `FINAL_REPORT_*.txt` - 每日影响力排行
- `*_complete_report.txt` - 单个网红详细报告

### 数据库 (`database/`)

- `influence_ranking.db` - 影响力排行数据库
- `influencer_data.db` - 网红基础数据
- `complete_influence.db` - 完整影响力数据

## ⚙️ 配置说明

### 环境变量 (.env 文件)

项目使用 `.env` 文件管理环境变量。复制 `.env.example` 为 `.env` 并填写你的配置：

```bash
cp .env.example .env
```

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 Key | 是 |
| `LISTENNOTES_API_KEY` | ListenNotes API Key (播客) | 否 |
| `HTTP_PROXY` | HTTP 代理地址 | 否 |
| `HTTPS_PROXY` | HTTPS 代理地址 | 否 |
| `LOG_LEVEL` | 日志级别 (DEBUG/INFO/WARNING/ERROR) | 否 |

### 获取 YouTube API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 **YouTube Data API v3**
4. 进入 **凭据** 页面
5. 点击 **创建凭据** → **API 密钥**
6. 复制密钥并粘贴到 `.env` 文件中

```bash
YOUTUBE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🎯 使用示例

### 抓取单个 YouTube 视频

```bash
python3 scripts/youtube_scraper.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 抓取中国网红数据

```bash
python3 scripts/china_multi_platform.py
```

### 生成完整报告

```bash
python3 scripts/complete_full_platform_report.py
```

### 运行完整系统（推荐）

```bash
python3 scripts/final_complete_system.py
```

## ⏰ 定时任务

添加每日自动抓取任务：

```bash
crontab -e
```

添加以下行：

```
0 9 * * * cd /path/to/project && python3 scripts/final_complete_system.py >> logs/cron.log 2>&1
```

## 📝 数据说明

### 数据获取方式

| 平台 | 数据来源 | 准确性 |
|------|----------|--------|
| YouTube | API | 精确 |
| Bilibili | API | 精确 |
| Instagram | 网页抓取 | 较高 |
| TikTok | 网页抓取 | 较高 |
| Twitter/X | 估算值 | 估算 |
| 微博 | 估算值 | 估算 |
| 抖音 | 估算值 | 估算 |
| 微信 | 无公开 API | 无法获取 |

### 影响力计算公式

```
影响力分数 = Σ (平台粉丝数 × 平台权重 × 互动系数)

平台权重：
- YouTube: 1.0
- Podcast: 0.6
- Bilibili: 0.8
- TikTok: 0.35
- Instagram: 0.3
- Twitter: 0.25
- 微博: 0.25
- 抖音: 0.4
```

## 🛠️ 技术栈

- **Python 3.8+**
- **YouTube Data API v3** - YouTube 数据
- **SQLite** - 本地数据存储
- **urllib** - 网页抓取
- **instaloader** - Instagram 数据

## ⚠️ 注意事项

1. **API 限制**: YouTube API 有每日配额限制，请合理使用
2. **反爬机制**: Twitter/X、微博、抖音有严格的反爬机制，部分数据使用估算值
3. **数据隐私**: 本项目仅抓取公开的社交媒体数据
4. **网络环境**: 部分中国平台需要在对应网络环境下访问

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 📧 联系

如有问题，请通过 GitHub Issues 联系。

---

**最后更新**: 2025年2月
