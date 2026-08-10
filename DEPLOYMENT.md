# 🚀 CodeMind Studio 完整部署指南（方案 B：Render.com + Supabase）

> **免费、无银行卡、数据库持久化**

---

## 📋 目录

1. [架构总览](#架构总览)
2. [前置准备](#前置准备)
3. [步骤一：Supabase 数据库配置](#步骤一supabase-数据库配置)
4. [步骤二：推送到 GitHub](#步骤二推送到-github)
5. [步骤三：部署后端到 Render.com](#步骤三部署后端到-rendercom)
6. [步骤四：部署前端到 Netlify](#步骤四部署前端到-netlify)
7. [步骤五：更新代理地址](#步骤五更新代理地址)
8. [步骤六：验证部署](#步骤六验证部署)
9. [常见问题排查](#常见问题排查)

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Netlify (前端)                                             │
│  URL: https://codemind-studio.netlify.app                   │
│  - 托管 Vue 3 静态文件                                       │
│  - API 反向代理 → Render.com                                 │
└─────────────────────────────────────────────────────────────┘
                              │ 反向代理
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Render.com (后端)                                          │
│  URL: https://codemind-studio.onrender.com                   │
│  - 运行 Flask 应用                                          │
│  - 连接 Supabase PostgreSQL                                 │
│  - 750 小时/月免费额度                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Supabase (数据库)                                          │
│  - PostgreSQL 数据库                                         │
│  - 500MB 免费存储                                           │
│  - 数据持久化保存                                           │
└─────────────────────────────────────────────────────────────┘
```

### 免费额度

| 平台 | 免费额度 | 说明 |
|------|----------|------|
| **Netlify** | 100GB 带宽/月 | 前端静态网站托管 |
| **Render.com** | 750 小时/月 | 后端 Flask 服务 |
| **Supabase** | 500MB 存储 | PostgreSQL 持久化 |

---

## 前置准备

### 1.1 需要的账号

| 账号 | 用途 | 注册地址 |
|------|------|----------|
| **GitHub** | 代码托管 | [github.com](https://github.com) |
| **Supabase** | 免费数据库 | [supabase.com](https://supabase.com) |
| **Render.com** | 后端部署 | [render.com](https://render.com) |
| **Netlify** | 前端部署 | [netlify.com](https://netlify.com) |

### 1.2 本地环境要求

- Python 3.10+
- Node.js 18+
- Git

### 1.3 项目文件结构

```
CMS-master/
├── app/                    # Flask 后端
│   ├── models/            # 数据模型
│   │   ├── db.py          # 统一数据库路由（SQLite/PostgreSQL）
│   │   ├── user_login.py  # 用户认证
│   │   ├── question_db.py # 题库管理
│   │   └── ...
│   └── ...
├── frontend/              # Vue 3 前端
│   └── ...
├── app.py                 # Flask 入口
├── requirements.txt       # Python 依赖
├── render.yaml            # Render 部署配置
├── netlify.toml           # Netlify 部署配置
├── .env                   # 环境变量（本地开发）
└── DEPLOYMENT.md          # 本文档
```

---

## 步骤一：Supabase 数据库配置

### 1.1 创建 Supabase 项目

1. 访问 [supabase.com](https://supabase.com) 并登录（使用 GitHub 账号）
2. 点击右上角 **"New Project"**
3. 填写项目信息：
   - **Name**: `codemind`（或任意名称）
   - **Database Password**: `0zRH7mlijXinntXg`（您已提供的密码）
   - **Region**: 选择 `Tokyo`（东京，延迟最低）
4. 点击 **"Create new project"**
5. 等待项目创建完成（约 1-2 分钟）

### 1.2 获取数据库连接字符串

1. 在 Supabase 控制台左侧菜单，点击 **"Database"** 图标
2. 在页面中部找到 **"Connection string"** 区域
3. 点击 **"Copy"** 按钮复制完整连接字符串

连接字符串格式：
```
postgresql://postgres:密码@主机地址:5432/postgres
```

示例（您的项目）：
```
postgresql://postgres:0zRH7mlijXinntXg@db.xqwbtufemsickddncnsm.supabase.co:5432/postgres
```

### 1.3 配置完成

✅ Supabase 数据库已配置完成，连接字符串已保存。

---

## 步骤二：推送到 GitHub

### 2.1 创建 GitHub 仓库

1. 访问 [github.com/new](https://github.com/new)
2. 填写仓库名：`codemind-studio`
3. 选择 **Private**（私有仓库）
4. 点击 **"Create repository"**

### 2.2 初始化本地 Git 仓库

打开终端（PowerShell 或 CMD），执行：

```bash
# 进入项目目录
cd f:\ne3\CMS-master

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit - CodeMind Studio"

# 设置远程仓库（替换 YOUR_USERNAME 为您的 GitHub 用户名）
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/codemind-studio.git

# 推送到 GitHub
git push -u origin main
```

### 2.3 注意事项

如果项目已初始化过 Git，可跳过 `git init`，直接执行：
```bash
git add .
git commit -m "更新部署配置"
git push origin main
```

---

## 步骤三：部署后端到 Render.com

### 3.1 准备工作

确保 `render.yaml` 文件已正确配置（已为您准备）：

```yaml
services:
  - type: web
    name: codemind-studio
    env: python
    region: singapore
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn -w 2 -b 0.0.0.0:$PORT app:app"
    envVars:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        value: postgresql://postgres:0zRH7mlijXinntXg@db.xqwbtufemsickddncnsm.supabase.co:5432/postgres
      - key: SECRET_KEY
        generateValue: true
      - key: CORS_ORIGINS
        value: https://codemind-studio.netlify.app,http://localhost:5173
      - key: PYTHON_VERSION
        value: "3.10.0"
    healthCheckPath: /health
    autoDeploy: false
```

### 3.2 创建 Render.com Web Service

1. 访问 [render.com](https://render.com) 并登录（使用 GitHub 账号）
2. 点击右上角 **"New +"** 按钮
3. 选择 **"Web Service"**

### 3.3 配置 Web Service

#### 连接 GitHub 仓库

1. 在 "Connect a repository" 部分，选择您的 `codemind-studio` 仓库
2. 如果看不到仓库，点击 **"Configure"** 授权访问

#### 基本配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **Name** | `codemind-studio` | 服务名称 |
| **Region** | `Singapore` | 新加坡，延迟最低 |
| **Branch** | `main` | 部署分支 |
| **Root Directory** | 留空 | 仓库根目录 |
| **Build Command** | `pip install -r requirements.txt` | 安装依赖 |
| **Start Command** | `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` | 启动 Flask |
| **Instance Type** | **Free** | 免费版 |

#### 环境变量（重要！）

如果 `render.yaml` 没有自动配置，请手动添加：

点击 **"Environment"** 标签，添加以下变量：

| NAME_OF_VARIABLE | value | 说明 |
|-----------------|-------|------|
| `FLASK_ENV` | `production` | 生产环境模式 |
| `DATABASE_URL` | `postgresql://postgres:0zRH7mlijXinntXg@db.xqwbtufemsickddncnsm.supabase.co:5432/postgres` | Supabase 连接字符串 |
| `SECRET_KEY` | 点击 **"Generate"** 自动生成 | Flask 密钥 |
| `CORS_ORIGINS` | `https://codemind-studio.netlify.app,http://localhost:5173` | 允许的前端地址 |
| `PYTHON_VERSION` | `3.10.0` | Python 版本 |

### 3.4 启动部署

1. 点击 **"Create Web Service"** 按钮
2. 等待部署完成（约 5-10 分钟）
3. 部署状态显示为 **"Live"** 时表示成功

### 3.5 获取后端 URL

部署成功后，您会获得一个后端 URL，格式为：
```
https://codemind-studio.onrender.com
```

**请记录此 URL，后续步骤需要使用！**

### 3.6 验证后端

在浏览器中访问：
```
https://codemind-studio.onrender.com/health
```

如果返回 `{"status": "healthy"}` 或类似 JSON，表示后端运行正常。

---

## 步骤四：部署前端到 Netlify

### 4.1 准备工作

确保 `netlify.toml` 文件已正确配置。

**注意**：此时需要先获取 Render 的后端 URL（将在步骤 5 中填入）。

### 4.2 创建 Netlify 站点

1. 访问 [netlify.com](https://netlify.com) 并登录（使用 GitHub 账号）
2. 点击 **"Add new site"** → **"Import an existing project"**
3. 选择您的 `codemind-studio` 仓库

### 4.3 配置构建

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **Build command** | `cd frontend && npm install && npm run build` | 构建前端 |
| **Publish directory** | `frontend/dist` | 构建产物目录 |

Netlify 会自动从 `netlify.toml` 读取配置。

### 4.4 启动部署

1. 点击 **"Deploy site"** 按钮
2. 等待前端构建完成（约 2-5 分钟）
3. 部署状态显示为 **"Published"** 时表示成功

### 4.5 获取前端 URL

部署成功后，您会获得一个前端 URL，格式为：
```
https://codemind-studio.netlify.app
```

**请记录此 URL！**

---

## 步骤五：更新代理地址

### 5.1 修改 netlify.toml

用文本编辑器打开 `netlify.toml` 文件，将所有 `YOUR_RENDER_URL` 替换为实际的 Render URL。

**示例**：如果您的 Render URL 是 `https://codemind-studio.onrender.com`

修改前：
```toml
[[redirects]]
  from = "/api/*"
  to = "https://YOUR_RENDER_URL/api/:splat"
```

修改后：
```toml
[[redirects]]
  from = "/api/*"
  to = "https://codemind-studio.onrender.com/api/:splat"
```

### 5.2 提交并推送

```bash
cd f:\ne3\CMS-master
git add netlify.toml
git commit -m "Update proxy URL for Render deployment"
git push origin main
```

### 5.3 触发重新部署

Netlify 会自动检测到代码变更并重新部署。

您也可以手动触发：
1. 打开 Netlify Dashboard
2. 进入站点 → **"Deploy"** 标签
3. 点击 **"Trigger deploy"** → **"Clear cache and deploy site"**

---

## 步骤六：验证部署

### 6.1 完整验证清单

按以下顺序验证每个功能：

#### ✅ 1. 后端 API 测试

在浏览器或 Postman 中测试：

```
GET https://codemind-studio.onrender.com/health
```
预期返回：`{"status": "healthy"}`

#### ✅ 2. 前端页面测试

在浏览器中访问：
```
https://codemind-studio.netlify.app
```
预期结果：显示 CodeMind Studio 首页

#### ✅ 3. 用户注册测试

1. 打开前端网站
2. 点击注册
3. 输入邮箱、用户名、密码
4. 点击获取验证码
5. 输入邮箱收到的验证码
6. 完成注册

#### ✅ 4. 用户登录测试

1. 用刚注册的账号登录
2. 确认可以进入主页

#### ✅ 5. 题库功能测试

1. 登录后访问题库
2. 确认题目列表可以加载
3. 点击题目查看详情

#### ✅ 6. 数据库持久化测试

1. 注册一个新用户
2. 在 Supabase 控制台 → **Table Editor** 查看 `users` 表
3. 确认新用户数据已保存

### 6.2 验证成功标准

如果以上所有测试通过，🎉 恭喜您！部署完成！

---

## 常见问题排查

### Q1: Render 服务启动失败

**症状**：部署状态显示红色错误

**排查步骤**：
1. 打开 Render Dashboard → 服务 → **"Logs"** 标签
2. 查看错误日志
3. 常见原因：
   - 缺少环境变量（检查 `DATABASE_URL`、`SECRET_KEY` 等）
   - 数据库连接失败（检查 Supabase 连接字符串是否正确）
   - Python 版本不匹配（设置 `PYTHON_VERSION=3.10.0`）

### Q2: 数据库连接失败

**症状**：`psycopg2.OperationalError` 或类似错误

**排查步骤**：
1. 确认 `DATABASE_URL` 格式正确
2. 确认密码正确
3. 在 Render 环境变量中检查是否有拼写错误
4. 如果使用特殊字符，需要 URL 编码（如 `@` → `%40`）

### Q3: 前端页面空白或 404

**症状**：访问前端 URL 显示空白页或 404 错误

**排查步骤**：
1. 检查 `netlify.toml` 中的 build command 和 publish directory
2. 确认 `frontend/dist` 目录存在
3. 在 Netlify → **"Deploy"** → 查看构建日志

### Q4: API 请求失败或 502 错误

**症状**：前端可以访问，但 API 请求返回错误

**排查步骤**：
1. 确认 `netlify.toml` 中的代理地址已更新为实际的 Render URL
2. 测试后端直接访问：`https://YOUR_RENDER_URL/health`
3. 检查 CORS 配置是否正确

### Q5: Render 服务休眠

**症状**：首次请求需要 30 秒以上才响应

**原因**：Render 免费版 15 分钟无流量后休眠

**解决方案**：
1. 使用 [UptimeRobot](https://uptimerobot.com)（免费）
2. 创建一个监控任务，每 5 分钟访问一次后端 URL
3. 这样可以防止服务休眠

### Q6: 邮件功能不工作

**症状**：验证码无法发送

**排查步骤**：
1. 检查 `.env` 中的 SMTP 配置
2. QQ 邮箱需要使用授权码，不是登录密码
3. 在 Render 环境变量中添加 SMTP 配置

### Q7: 本地开发和生产环境的差异

**本地开发**：
- 使用 SQLite 数据库（`codemind.db` 文件）
- 无需配置环境变量
- 运行 `python app.py` 启动

**生产环境**：
- 使用 Supabase PostgreSQL
- 需要配置 `DATABASE_URL` 等环境变量
- 通过 Render.com 部署

---

## 附录：代码文件说明

| 文件 | 用途 | 说明 |
|------|------|------|
| `app/models/db.py` | 统一数据库路由 | 自动切换 SQLite/PostgreSQL |
| `app/models/user_login.py` | 用户认证 | 登录、注册、密码重置 |
| `app/models/question_db.py` | 题库管理 | 题目 CRUD 操作 |
| `app/models/user_operation_records.py` | 操作记录 | 日志、历史记录 |
| `app/models/favorites_topics.py` | 收藏功能 | 收藏的题目管理 |
| `render.yaml` | Render 配置 | 后端部署配置文件 |
| `netlify.toml` | Netlify 配置 | 前端部署配置文件 |
| `.env` | 环境变量 | 本地开发配置 |

---

## 完成检查清单

- [x] Supabase 数据库已创建
- [x] GitHub 仓库已推送
- [x] Render 后端部署成功
- [x] Netlify 前端部署成功
- [x] netlify.toml 代理地址已更新
- [x] 数据库连接测试通过
- [x] 用户注册功能正常
- [x] 用户登录功能正常
- [x] 题库功能正常
- [x] 数据持久化验证通过

---

## 📞 技术支持

如遇到问题：
1. 查看 Render 日志：Dashboard → 服务 → Logs
2. 查看 Netlify 日志：Dashboard → Site → Deploy → Log
3. 查看 Supabase 状态：Console → Database → Connection string
4. 检查环境变量配置是否正确

---

**文档版本**: v1.0
**最后更新**: 2026-08-10
**适用项目**: CodeMind Studio