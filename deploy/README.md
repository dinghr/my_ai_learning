# AI助学小程序 - 部署文档

## 环境架构

```
┌─────────────────────────────────────────────────────────────┐
│                     微信小程序 (1个 AppID)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  开发版      │  │  体验版      │  │  正式版              │  │
│  │  (开发调试)   │  │  (内部测试)   │  │  (审核发布)           │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                    │              │
│         ▼                ▼                    ▼              │
│    localhost:8000   test-api.xxx.com    api.xxx.com          │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐      ┌─────────────┐     ┌─────────────┐
   │ 开发环境 │      │  测试环境    │     │  生产环境    │
   │ (本地)   │      │ (体验服务器)  │     │ (生产服务器)  │
   │ SQLite   │      │  SQLite     │     │  SQLite/    │
   │ ai_learning│     │ ai_learning │     │ PostgreSQL  │
   │ _dev.db  │      │ _test.db    │     │ _prod.db    │
   └─────────┘      └─────────────┘     └─────────────┘
```

## 环境隔离

### 数据库隔离 ✅

每个环境使用独立的 SQLite 数据库文件：

| 环境 | 数据库文件 | 配置文件 |
|------|-----------|---------|
| 开发 | `ai_learning_dev.db` | `.env.development` |
| 测试 | `ai_learning_test.db` | `.env.test` |
| 生产 | `ai_learning_prod.db` | `.env.production` |

启动时通过 `ENV` 环境变量自动加载对应配置：
```bash
ENV=development uvicorn app.main:app        # 加载 .env.development
ENV=test uvicorn app.main:app               # 加载 .env.test
ENV=production uvicorn app.main:app         # 加载 .env.production
```

### 前端 API 地址隔离 ✅

| 环境 | 构建命令 | API 地址 |
|------|---------|---------|
| 开发 | `npm run dev:h5` / `npm run dev:weapp` | `http://localhost:8000/api` |
| 测试 | `TARO_APP_API_URL=https://test-api.xxx.com/api npm run build:weapp` | 测试服务器 |
| 生产 | `TARO_APP_API_URL=https://api.xxx.com/api npm run build:weapp` | 生产服务器 |

## 小程序：需要两个 AppID 吗？

**不需要。** 微信小程序一个 AppID 就能管理三个版本：

| 版本 | 用途 | 后端连谁 |
|------|------|---------|
| **开发版** | 开发者工具上传，自己调试 | `localhost:8000` |
| **体验版** | 生成二维码，发给家人/朋友测试 | 测试服务器 (`test-api.xxx.com`) |
| **正式版** | 提交审核，发布后所有用户可用 | 生产服务器 (`api.xxx.com`) |

### 体验版 vs 正式版的构建流程

```bash
# 1. 开发调试（本地后端）
npm run dev:weapp

# 2. 构建体验版（连测试后端）
TARO_APP_API_URL=https://test-api.xxx.com/api npm run build:weapp
# → 微信开发者工具 → 上传 → 设置为体验版

# 3. 构建正式版（连生产后端）
TARO_APP_API_URL=https://api.xxx.com/api npm run build:weapp
# → 微信开发者工具 → 上传 → 提交审核
```

> 💡 建议：在 `project.config.json` 中把 `appid` 从 `touristappid` 替换为你的真实小程序 AppID。

## 后端部署步骤

### 1. 首次部署

```bash
# 服务器上
sudo mkdir -p /var/www/ai-study /var/log/ai-study
cd /var/www/ai-study
git clone -b dev https://github.com/dinghr/my_ai_learning.git .

# Python 虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 放置生产环境配置（不要提交到 Git！）
cp .env.production .env.production.local
vim .env.production.local   # 填入真实的密钥、AppID、Secret

# 创建数据库
ENV=production python -c "from app.database import init_db; init_db()"

# 日志目录
sudo mkdir -p /var/log/ai-study
sudo chown deploy:deploy /var/log/ai-study

# Systemd 服务
sudo cp deploy/systemd/ai-study-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-study-backend
sudo systemctl start ai-study-backend

# Nginx
sudo cp deploy/nginx/ai-study.conf /etc/nginx/sites-available/ai-study
sudo ln -s /etc/nginx/sites-available/ai-study /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# HTTPS（推荐）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 更新部署

```bash
# 方式一：GitHub Actions 自动部署（推荐）
# push 到 main 分支会自动触发部署

# 方式二：手动部署
cd /var/www/ai-study
git pull origin dev
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ai-study-backend
```

### 3. 查看日志

```bash
sudo journalctl -u ai-study-backend -f        # 服务日志
sudo tail -f /var/log/ai-study/app.log        # 应用日志
sudo tail -f /var/log/nginx/ai-study-error.log # Nginx 错误
```

## 测试环境部署

测试环境和生产环境可以部署在同一台服务器的不同目录：

```bash
# 测试环境
sudo mkdir -p /var/www/ai-study-test
cd /var/www/ai-study-test
git clone https://github.com/dinghr/my_ai_learning.git .
# ... 同上，但使用 .env.test 和 8001 端口
```

或者使用 Docker 隔离（未来扩展）。

## GitHub Actions Secrets 配置

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret | 说明 |
|--------|------|
| `ALIYUN_HOST` | 生产服务器 IP `8.130.161.121` |
| `ALIYUN_HOST_TEST` | 测试服务器 IP |
| `ALIYUN_SSH_KEY` | SSH 私钥 |
| `PROD_API_URL` | 生产 API 地址，`https://api.xxx.com/api` |
| `TEST_API_URL` | 测试 API 地址，`https://test-api.xxx.com/api` |

## 生产环境检查清单

- [ ] `.env.production` 中 `secret_key` 已改为强随机字符串
- [ ] `.env.production` 中 `cors_origins` 已限制为实际域名（非 `*`）
- [ ] 微信小程序 `appid` 和 `secret` 已填入真实值
- [ ] DeepSeek API Key 已填入
- [ ] 数据库已初始化 (`init_db()`)
- [ ] Nginx 已配置并启用
- [ ] HTTPS 证书已配置（Let's Encrypt）
- [ ] Systemd 服务已启用自启动
- [ ] 日志轮转已配置 (`logrotate`)
- [ ] 防火墙只开放 80/443 端口
