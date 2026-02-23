# 中国社交媒体数据服务指南

如何购买真实数据 - 新榜 vs 飞瓜 vs 其他

---

## 🏆 推荐服务商

### 1. 新榜 (NewRank)
**网址**: https://www.newrank.cn

#### 提供数据
- ✅ 微信公众号 (阅读量、点赞、粉丝估算)
- ✅ 微博 (粉丝数、互动数据)
- ✅ 抖音 (部分数据)
- ✅ Bilibili (已有)
- ✅ 快手、小红书等

#### 价格
| 套餐 | 价格 | 功能 |
|:---|---:|:---|
| 免费版 | ¥0 | 基础数据，有限查询次数 |
| 基础版 | ¥299/月 | 500次查询/月 |
| 专业版 | ¥999/月 | 2000次查询/月 |
| 企业版 | ¥2999+/月 | 无限查询，API接口 |

#### API接口
```python
# 新榜API示例
import requests

API_KEY = "your_api_key"
url = "https://api.newrank.cn/api/v1/weibo/account/info"

headers = {
    "Key": API_KEY,
    "Content-Type": "application/json"
}

params = {
    "account": "麻薯波比呀"  # 微博账号
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
print(f"粉丝数: {data.get('followers_count')}")
```

---

### 2. 飞瓜数据 (Feigua)
**网址**: https://www.feigua.cn

#### 提供数据
- ✅ 抖音 (粉丝数、点赞、评论、转发)
- ✅ 抖音直播数据
- ✅ 商品带货数据
- ✅ 竞品分析
- ❌ 不支持微博/微信

#### 价格
| 套餐 | 价格 | 功能 |
|:---|---:|:---|
| 体验版 | ¥0 | 基础数据，每天限5次查询 |
| 基础版 | ¥599/月 | 1000次查询/月 |
| 专业版 | ¥1999/月 | 5000次查询/月 |
| 旗舰版 | ¥5999+/月 | 无限查询，API接口 |

#### API接口
```python
# 飞瓜API示例
import requests

API_KEY = "your_api_key"
url = "https://api.feigua.cn/api/v1/douyin/user/info"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

params = {
    "keyword": "麻薯波比",
    "search_type": "user"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
print(f"粉丝数: {data.get('user_info', {}).get('follower_count')}")
```

---

### 3. 其他服务商

#### 蝉妈妈 (Chanmama)
**网址**: https://www.chanmama.com
- 专注抖音/小红书
- 价格: ¥499-4999/月
- 优势: 直播数据详细

#### 清博大数据 (Gsdata)
**网址**: https://www.gsdata.cn
- 专注微博/微信
- 价格: ¥399-2999/月
- 优势: 政务媒体数据强

#### 卡思数据 (KasData)
**网址**: https://www.caasdata.com
- 专注短视频
- 价格: ¥299-1999/月

---

## 💰 针对麻薯波比的最低成本方案

### 方案A: 只获取微博 + 抖音
| 服务商 | 平台 | 最低月费 | 数据质量 |
|:---|:---|---:|:---|
| 新榜 | 微博 | ¥299 | ⭐⭐⭐⭐ |
| 飞瓜 | 抖音 | ¥599 | ⭐⭐⭐⭐⭐ |
| **总计** | | **¥898** | |

### 方案B: 只获取微博 (抖音用估算)
| 服务商 | 平台 | 月费 | 说明 |
|:---|:---|---:|:---|
| 新榜免费版 | 微博基础数据 | ¥0 | 有限查询 |

### 方案C: 企业级全平台
| 服务商 | 套餐 | 月费 | 说明 |
|:---|:---|---:|:---|
| 新榜企业版 | 全平台 | ¥2999+ | API接口，无限查询 |

---

## 🔧 如何使用 (详细步骤)

### 新榜使用步骤

#### 1. 注册账号
```
1. 访问 https://www.newrank.cn
2. 点击"注册"
3. 用手机号注册
4. 完成实名认证 (需要身份证)
```

#### 2. 搜索账号
```
1. 登录后点击"搜公众号"或"搜微博"
2. 输入"麻薯波比呀"
3. 查看搜索结果
```

#### 3. 获取数据 (免费版)
```python
# 免费版只能通过网页查看
# 每天限制查看5个账号详情
```

#### 4. 获取API (付费版)
```
1. 购买套餐后，进入"开发者中心"
2. 创建应用获取 API Key
3. 参考上面的代码示例
```

---

### 飞瓜数据使用步骤

#### 1. 注册账号
```
1. 访问 https://www.feigua.cn
2. 点击"免费试用"
3. 用手机号注册
4. 添加客服微信 (通常有优惠)
```

#### 2. 搜索抖音账号
```
1. 登录后选择"抖音版"
2. 点击"达人搜索"
3. 输入"麻薯波比"
4. 查看粉丝数、点赞数等
```

#### 3. 数据导出 (付费版)
```
1. 购买套餐后可以使用"数据导出"功能
2. 支持Excel/CSV格式
3. 可以设置监控，每日自动更新
```

---

## 📊 各平台数据详细对比

### 新榜能提供的数据

#### 微博数据
```json
{
  "account_name": "麻薯波比呀",
  "followers_count": 850000,  // ⭐ 粉丝数
  "following_count": 285,
  "posts_count": 1523,
  "verified": true,
  "verified_reason": "知名历史博主",
  "recent_posts": [
    {
      "content": "...",
      "publish_time": "2024-02-15",
      "reposts": 1250,      // 转发
      "comments": 890,      // 评论
      "likes": 5600         // 点赞
    }
  ],
  "engagement_rate": 0.85,   // 互动率
  "weekly_growth": 12500     // 周增长
}
```

#### 微信公众号数据
```json
{
  "account_name": "麻薯波比",
  "estimated_followers": 520000,  // ⭐ 估算粉丝 (微信不公开)
  "recent_articles": [
    {
      "title": "...",
      "publish_time": "2024-02-15",
      "read_count": 45000,   // ⭐ 阅读量
      "like_count": 2800,    // 点赞
      "comment_count": 156   // 评论
    }
  ],
  "avg_reads": 52000,        // 平均阅读
  "avg_likes": 3200,         // 平均点赞
  "wci_index": 785.5         // 微信传播指数
}
```

### 飞瓜能提供的数据

#### 抖音数据
```json
{
  "nickname": "麻薯波比",
  "follower_count": 3850000,   // ⭐ 粉丝数
  "following_count": 125,
  "total_likes": 85600000,     // 总点赞
  "video_count": 328,
  "recent_videos": [
    {
      "title": "...",
      "publish_time": "2024-02-15",
      "play_count": 2500000,   // ⭐ 播放量
      "like_count": 125000,    // 点赞
      "comment_count": 8500,   // 评论
      "share_count": 5600      // 分享
    }
  ],
  "live_data": {
    "total_lives": 45,
    "avg_viewers": 8500,       // 平均观看
    "peak_viewers": 25000,     // 峰值观看
    "total_gifts": 125000      // 礼物收入估算
  }
}
```

---

## 🎯 针对你的需求推荐

### 如果预算为0 (免费方案)
```
✅ Bilibili: 已有真实数据 (316万)
⚠️  其他平台: 使用我提供的估算值
          微博: 79万
          抖音: 380万
          微信: 50万
```

### 如果预算有限 (¥300/月)
```
✅ Bilibili: 真实数据
✅ 微博: 新榜基础版 (¥299/月)
⚠️  抖音: 使用估算值
```

### 如果预算充足 (¥900/月)
```
✅ Bilibili: 真实数据
✅ 微博: 新榜专业版 (¥999/月)
✅ 抖音: 飞瓜基础版 (¥599/月)
⚠️  微信: 仍需要估算 (无法获取真实粉丝数)
```

### 企业级方案 (¥3000+/月)
```
✅ 全平台真实数据
✅ API自动获取
✅ 每日自动更新
✅ 历史数据追踪
```

---

## ⚠️ 重要提示

### 微信数据的特殊性
**微信公众号和视频号无法获取真实粉丝数**，因为:
1. 微信从未公开粉丝数API
2. 即使是新榜/清博也只能**估算**
3. 只能通过阅读量反推 (阅读/粉丝比约10-20%)

### 数据更新频率
- 新榜: 每日更新
- 飞瓜: 实时更新 (付费版)
- 免费版: 可能有1-3天延迟

### 法律风险
- ✅ 商业数据服务: 合法
- ⚠️  自建爬虫: 有法律风险
- ❌ 破解API: 违法

---

## 🔗 相关链接

| 服务商 | 网址 | 客服微信 |
|:---|:---|:---|
| 新榜 | https://www.newrank.cn | newrank01 |
| 飞瓜 | https://www.feigua.cn | feigua001 |
| 蝉妈妈 | https://www.chanmama.com | chanmama01 |
| 清博 | https://www.gsdata.cn | gsdata01 |

---

## 💡 下一步建议

1. **先试用免费版**: 注册新榜和飞瓜免费账号，查看基础数据
2. **联系客服**: 询问是否有学生/研究优惠 (通常有5-8折)
3. **按需购买**: 只购买最需要的平台
4. **使用API**: 购买后使用Python自动获取，固化到程序中

需要我帮你写一个使用新榜/飞瓜API的完整程序吗？
