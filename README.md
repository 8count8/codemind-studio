# CodeMind Studio

> 基于 AI 的编程学习与代码质量审查平台。采用**前后端分离架构**，Vue 3 前端 + Flask REST API 后端，全栈部署于 Netlify + Supabase PostgreSQL。

## 项目简介

CodeMind Studio 是一个面向编程初学者与从业者的智能学习平台，融合 AI 代码审查、实时编程反馈、智能错题诊断与个性化能力分析，帮助用户高效提升编程能力。

## 技术栈

### 后端
- **Flask** ≥ 2.3 — Web 框架
- **Flask-WTF** — CSRF 保护
- **Flask-CORS** — 前后端分离跨域支持
- **Flasgger** — Swagger API 文档自动生成
- **psycopg2-binary** — PostgreSQL 驱动
- **bcrypt** — 密码哈希加密
- **python-dotenv** — 环境变量管理

### 前端
- **Vue** 3.4 + **Vite** 5 — 视图框架与构建工具
- **Vue Router** 4 — SPA 路由
- **Pinia** 2 — 状态管理
- **Axios** — HTTP 客户端（含 CSRF 拦截器 + Session Cookie）
- **Chart.js** — 能力矩阵雷达图可视化
- **Marked** + **highlight.js** — Markdown 渲染与代码高亮
- **Ace Builds** — 在线代码编辑器

### 数据库
- **Supabase PostgreSQL** — 11 张表，完整建表 + 种子数据脚本

### 部署
- **Netlify** — 前端静态托管 + Serverless Functions 后端（统一平台）
- **Supabase** — PostgreSQL 数据库（500MB 免费额度）

## 功能模块

| 模块 | 路由 | 说明 |
|---|---|---|
| 用户认证 | `/login` `/register` `/reset` | 邮箱验证码注册、登录、密码重置、CSRF Token |
| 首页仪表盘 | `/` `/dashboard` | 平台入口、功能导航 |
| 题库系统 | `/quizbank` | 题目列表、按难度/标签筛选、模糊搜索、题目详情 |
| 在线答题 | `/answerpad` | 代码编辑器、提交运行、测试用例验证 |
| AI 代码审查 | `/code-review` | 上传/粘贴代码 → AI 多维度审查、结果存入历史 |
| AI 智能出题 | `/ai-question` | AI 自动生成编程题目 |
| 能力矩阵 | `/ability-matrix` | 5 维度雷达图（语法/算法/项目/调试/安全）、提交评估、历史趋势、学习推荐 |
| 收藏夹 | `/favorites` | 收藏题目、搜索收藏、删除收藏 |
| 历史记录 | `/history` | 功能使用日志 + 代码上传记录 + 审查结果（3 表合并、按时间排序） |
| 个人中心 | `/profile` | 用户资料（含注册时间、最后登录时间） |

## 项目结构

```
CMS-master/
├── app/                              # Flask 后端应用
│   ├── __init__.py                   # 应用工厂 (create_app)
│   ├── api/                          # 蓝图层 (10 个 Blueprint)
│   │   ├── __init__.py               # Blueprint 注册
│   │   ├── main_routes.py            # 主路由 + CSRF Token 接口
│   │   ├── app_auth.py               # 认证接口
│   │   ├── quizbank_routes.py        # 题库接口
│   │   ├── answer_routes.py          # 答题接口
│   │   ├── code_review_routes.py     # 代码审查
│   │   ├── ai_question_routes.py     # AI 智能出题
│   │   ├── ability_matrix_routes.py  # 能力矩阵
│   │   ├── favorites_history_routes.py  # 收藏与历史
│   │   ├── profile_routes.py         # 个人中心
│   │   └── user_api.py              # 用户接口（代码审查/历史/收藏 API）
│   ├── models/                       # 数据模型层
│   │   ├── db.py                     # PostgreSQL 连接 + 建表（11 张表）
│   │   ├── user_login.py            # 用户注册/登录/验证码（bcrypt + secrets.compare_digest）
│   │   ├── question_db.py           # 题库 CRUD
│   │   ├── favorites_topics.py      # 收藏 CRUD
│   │   ├── user_operation_records.py # 操作记录（3 表合并查询）
│   │   ├── ability_matrix_model.py  # 能力矩阵 + 提交历史 + 趋势 + 推荐
│   │   └── testcode.py              # 测试用例
│   ├── service/                      # 业务逻辑层
│   │   ├── ability_matrix_service.py # 能力矩阵服务（启发式评分）
│   │   └── ai/                       # AI 服务（代码审查/出题）
│   └── utils/                        # 工具层（邮件发送等）
├── frontend/                         # Vue 3 前端应用
│   ├── src/
│   │   ├── views/                    # 11 个页面视图
│   │   ├── components/               # 公共组件（主题切换等）
│   │   ├── router/                   # 路由配置 + 登录守卫
│   │   ├── stores/                   # Pinia 状态管理
│   │   ├── utils/                    # http 封装（Axios + CSRF）、常量
│   │   └── assets/                   # 静态资源与样式
│   ├── vite.config.js                # Vite 配置（含开发代理 → :5000）
│   └── package.json
├── database/
│   └── init_db.sql                   # 完整建表 + 15 道种子题 + 42 组测试用例 + 预置账户
├── netlify/
│   ├── functions/
│   │   └── app.py                    # Netlify Serverless Functions 入口（Flask WSGI 适配）
│   └── toml                          # → netlify.toml
├── software-testing/                 # 测试代码（与业务代码隔离）
│   ├── api-tests/                    # 20 条 Flask API 集成测试
│   ├── db-tests/                     # 23 条数据库链路测试
│   ├── reports/                      # JSON 测试报告
│   └── run_all_tests.py             # 一键运行入口
├── config.py                         # 配置类（Dev/Prod/Test）
├── requirements.txt                  # Python 依赖
├── netlify.toml                      # Netlify 构建配置 + SPA 路由 + API 重定向
└── .env.example                      # 环境变量示例
```

## 数据库

### 11 张表

| 表名 | 用途 |
|---|---|
| `users` | 用户账户（username + bcrypt password + email + created_at + last_login） |
| `verification_codes` | 邮箱验证码（10 分钟过期，ON CONFLICT 覆盖重发） |
| `problems` | 题库（15 道种子题：简单 5 + 中等 7 + 困难 3） |
| `test_cases` | 测试用例（42 组 input + expected_output） |
| `answer_records` | 答题记录 |
| `favorites` | 收藏夹 |
| `functions_used` | 功能使用日志（历史记录来源之一） |
| `user_uploads` | 代码上传记录（历史记录来源之一） |
| `api_responses` | 审查结果记录（历史记录来源之一，关联 upload_id） |
| `ability_matrix` | 能力矩阵 5 维度评分 |
| `ability_submissions` | 能力评估提交历史（趋势分析数据源） |

### 初始化

在 Supabase SQL Editor 中粘贴执行 [database/init_db.sql](database/init_db.sql)：
- 11 张表建表（`IF NOT EXISTS`，可重复执行）
- 15 道编程题目 + 42 组测试用例
- 2 个预置账户（admin / testuser，bcrypt 已验证）
- 10 个性能索引
- `ALTER TABLE ADD COLUMN IF NOT EXISTS` 兼容旧库迁移

### 安全设计

- 密码使用 **bcrypt** 加密存储
- 验证码比较使用 **`secrets.compare_digest`**（恒定时间，防时序攻击）
- 验证码过期时间用 **datetime 对象**比较（非字符串）
- 验证码 10 分钟有效期 + 20 秒重发间隔限制
- CSRF Token 通过 Flask-WTF session 签名实现（不落库）
- Session Cookie 由 `SECRET_KEY` 签名

## 本地开发

### 环境要求
- Python ≥ 3.10
- Node.js ≥ 18
- Supabase PostgreSQL 连接串

### 1. 启动后端

```bash
# 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DATABASE_URL 等

# 启动 Flask（通过 Netlify Functions 本地模拟或直接运行）
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务：http://localhost:5173

> Vite 开发服务器已配置代理，`/api/*`、`/login`、`/auth/*` 等路径会自动转发到后端。

### 3. 生产构建

```bash
cd frontend
npm run build      # 输出到 frontend/dist
```

## 环境变量

| 变量名 | 说明 | 示例 |
|---|---|---|
| `DATABASE_URL` | Supabase PostgreSQL 连接串 | `postgresql://postgres:pwd@db.xxx.supabase.co:5432/postgres` |
| `SECRET_KEY` | 会话加密密钥（生产必填） | 随机字符串 |
| `CORS_ORIGINS` | 允许的前端来源（逗号分隔） | `http://localhost:5173,https://xxx.netlify.app` |
| `SMTP_SERVER` | 邮件服务器 | `smtp.qq.com` |
| `SMTP_PORT` | 邮件端口 | `465` |
| `EMAIL_ACCOUNT` | 邮箱账号 | `you@qq.com` |
| `EMAIL_PASSWORD` | 邮箱 SMTP 授权码 | — |

## 部署

### 架构：Netlify（全栈）+ Supabase（数据库）

```
用户浏览器
    ↓
Netlify（统一平台）
    ├── 前端：Vue 3 → npm build → 静态托管
    ├── 后端：Flask → netlify/functions/app.py（Serverless Functions）
    └── 数据库：Supabase PostgreSQL（通过 DATABASE_URL 连接）
```

### 部署步骤

1. **数据库**：在 [Supabase](https://supabase.com) 创建项目，执行 `database/init_db.sql`，获取连接串
2. **代码推送**：将仓库推送到 GitHub
3. **Netlify 部署**：在 [Netlify](https://netlify.com) 创建站点，选择仓库，`netlify.toml` 已配置：
   - 构建命令：`cd frontend && npm install && npm run build`
   - 发布目录：`frontend/dist`
   - Functions 目录：`netlify/functions`
4. **环境变量**：在 Netlify 站点设置中注入 `DATABASE_URL`、`SECRET_KEY`、`CORS_ORIGINS`、SMTP 相关变量
5. **验证**：访问前端首页，测试注册/登录、题库浏览、代码审查、能力矩阵、历史记录

## 测试

测试代码位于 `software-testing/` 目录，与业务代码完全隔离。

```bash
# 一键运行全部测试
.venv\Scripts\python.exe software-testing\run_all_tests.py

# 单独运行数据库链路测试（23 条）
.venv\Scripts\python.exe software-testing\db-tests\test_db_all.py

# 单独运行 API 集成测试（20 条）
.venv\Scripts\python.exe software-testing\api-tests\test_api_all.py
```

测试报告输出到 `software-testing/reports/` 目录（JSON 格式）。

## API 文档

启动后端后访问 `/apidocs/` 查看由 Flasgger 自动生成的 Swagger 交互式 API 文档。

## 致谢

本项目基于 [zhuofeng1023/CMS](https://github.com/zhuofeng1023/CMS.git) 重构而成，在前端分离架构、数据库设计、安全加固与免费部署方案上进行了重新设计与实现。

## License

本项目仅供学习与交流使用。
