# China-US Influencer Social Media Data Analysis System

A Python project for scraping and analyzing multi-platform social media data of top influencers (KOLs) from China and the United States.

## 📋 Project Overview

This project automates the collection of social media data for Chinese and American influencers across multiple platforms:

**US Influencers**: MrBeast, MKBHD, Joe Rogan
**Chinese Influencers**: Li Ziqi (李子柒), Sima Nan (司马南), Hu Xijin (胡锡进)

**Supported Platforms**:
- YouTube, Bilibili, Weibo, Douyin (TikTok China)
- Twitter/X, Instagram, TikTok
- Podcast (Spotify), WeChat Official Accounts

## 🗂️ Directory Structure

```
.
├── .env                        # Environment variables (create manually)
├── .env.example                # Environment variables example
├── .gitignore                  # Git ignore configuration
├── README.md                   # Chinese documentation
├── README_EN.md                # English documentation (this file)
│
├── scripts/                    # Python scrapers and report generators
│   ├── youtube_scraper.py      # YouTube data scraper
│   ├── china_multi_platform.py # Chinese platforms scraper
│   ├── final_complete_system.py # Main entry point (complete system)
│   └── ...                     # Other scrapers and report generators
│
├── data/
│   ├── json/                   # Raw data in JSON format
│   └── reports/                # Text format reports
│
├── database/                   # SQLite database files
│   ├── influence_ranking.db    # Influence ranking database
│   └── ...                     # Other databases
│
├── docs/                       # Documentation and guides
│   ├── DATA_SERVICES_GUIDE.md  # Data services guide
│   ├── PYTHON_FILES_GUIDE.md   # Python files documentation
│   └── ...                     # Other documentation
│
├── config/                     # Configuration files
│   ├── requirements.txt        # Python dependencies
│   └── influencer_config.json  # Influencer configuration
│
└── archive/                    # Archived files
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r config/requirements.txt
```

Or install core dependencies manually:

```bash
pip install google-api-python-client instaloader python-dotenv
```

### 2. Configure Environment Variables

Copy the example configuration file and fill in your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys:

```bash
# Required: YouTube Data API Key
YOUTUBE_API_KEY=your_youtube_api_key_here

# Optional: ListenNotes API Key (for podcast data)
LISTENNOTES_API_KEY=your_listennotes_key_here
```

> **Get YouTube API Key**: Visit [Google Cloud Console](https://console.cloud.google.com/apis/credentials), enable YouTube Data API v3, and create an API key.

### 3. Run the Main Program

```bash
# Run from project root
python3 scripts/final_complete_system.py
```

## 📊 Features

### Scraper Modules

| Script | Function | Platform |
|--------|----------|----------|
| `youtube_scraper.py` | YouTube video/channel data | YouTube |
| `china_multi_platform.py` | Chinese influencers multi-platform data | Bilibili, Weibo, Douyin |
| `x_free_crawler.py` | X/Twitter data scraper | Twitter/X |
| `podcast_nuclear_hunter.py` | Podcast data scraper | Spotify |
| `multi_platform_scraper.py` | Multi-platform comprehensive scraper | All platforms |

### Report Generation Modules

| Script | Function |
|--------|----------|
| `complete_full_platform_report.py` | Generate complete full-platform report |
| `china_full_platform_report.py` | Generate Chinese influencers report |
| `free_version_report.py` | Free version report (no API required) |
| `complete_report_with_podcast.py` | Complete report with podcast data |

## 📈 Output Files

### JSON Data Files (`data/json/`)

- `COMPLETE_FULL_DATA_*.json` - Complete influencer data
- `CHINA_FULL_DATA_*.json` - Chinese influencers data
- `FINAL_DATA_*.json` - Final comprehensive data
- `CN_INFLUENCERS_*.json` - Chinese influencer profiles
- `*_COMPLETE_DATA_*.json` - Individual influencer complete data

### Report Files (`data/reports/`)

- `COMPLETE_FULL_REPORT_*.txt` - Complete full-platform report
- `CHINA_FULL_REPORT_*.txt` - Chinese influencers report
- `FINAL_REPORT_*.txt` - Daily influence ranking
- `*_complete_report.txt` - Individual influencer detailed report

### Database (`database/`)

- `influence_ranking.db` - Influence ranking database
- `influencer_data.db` - Influencer basic data
- `complete_influence.db` - Complete influence data

## ⚙️ Configuration

### Environment Variables (.env file)

The project uses a `.env` file for environment variables. Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

| Variable | Description | Required |
|----------|-------------|----------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 Key | Yes |
| `LISTENNOTES_API_KEY` | ListenNotes API Key (podcasts) | No |
| `HTTP_PROXY` | HTTP proxy address | No |
| `HTTPS_PROXY` | HTTPS proxy address | No |
| `LOG_LEVEL` | Log level (DEBUG/INFO/WARNING/ERROR) | No |

### Getting YouTube API Key

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **YouTube Data API v3**
4. Go to the **Credentials** page
5. Click **Create Credentials** → **API Key**
6. Copy the key and paste it into the `.env` file

```bash
YOUTUBE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🎯 Usage Examples

### Scrape a Single YouTube Video

```bash
python3 scripts/youtube_scraper.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Scrape Chinese Influencers Data

```bash
python3 scripts/china_multi_platform.py
```

### Generate Complete Report

```bash
python3 scripts/complete_full_platform_report.py
```

### Run Complete System (Recommended)

```bash
python3 scripts/final_complete_system.py
```

## ⏰ Scheduled Tasks

Add daily automated scraping with cron:

```bash
crontab -e
```

Add the following line:

```
0 9 * * * cd /path/to/project && python3 scripts/final_complete_system.py >> logs/cron.log 2>&1
```

## 📝 Data Information

### Data Sources

| Platform | Data Source | Accuracy |
|----------|-------------|----------|
| YouTube | API | Exact |
| Bilibili | API | Exact |
| Instagram | Web scraping | High |
| TikTok | Web scraping | High |
| Twitter/X | Estimated | Estimated |
| Weibo | Estimated | Estimated |
| Douyin | Estimated | Estimated |
| WeChat | No public API | Unavailable |

### Influence Score Calculation

```
Influence Score = Σ (Platform Followers × Platform Weight × Engagement Coefficient)

Platform Weights:
- YouTube: 1.0
- Podcast: 0.6
- Bilibili: 0.8
- TikTok: 0.35
- Instagram: 0.3
- Twitter: 0.25
- Weibo: 0.25
- Douyin: 0.4
```

## 🛠️ Tech Stack

- **Python 3.8+**
- **YouTube Data API v3** - YouTube data
- **SQLite** - Local data storage
- **urllib** - Web scraping
- **instaloader** - Instagram data

## ⚠️ Important Notes

1. **API Limits**: YouTube API has daily quota limits, please use responsibly
2. **Anti-scraping**: Twitter/X, Weibo, and Douyin have strict anti-scraping measures; some data uses estimates
3. **Data Privacy**: This project only scrapes publicly available social media data
4. **Network Environment**: Some Chinese platforms require access from within the appropriate network environment

## 📄 License

This project is for educational and research purposes only.

## 🤝 Contributing

Issues and Pull Requests are welcome to improve the project.

## 📧 Contact

For questions, please contact via GitHub Issues.

---

**Last Updated**: February 2025
