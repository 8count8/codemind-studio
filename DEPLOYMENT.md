# 🚀 CodeMind Studio - 全 Netlify 部署指南

> **完全免费，无需银行卡，一个平台搞定前后端！**

---

## 📋 架构说明

```
用户浏览器
    ↓
Netlify (前端 + 后端 Functions) ──连接──→ Supabase (数据库)
    ↓                              ↓
  Vue 3 + Flask Functions    PostgreSQL
```

### 优势
- ✅ **只需要一个平台**（Netlify）
- ✅ **完全免费**（无需银行卡）
- ✅ **统一管理**（前后端同仓库）
- ✅ **自动部署**（Git push 自动更新）

---

## 📁 项目结构

```
CMS-master/
├── netlify/
│   ├── functions/
│   │   └── app.py          # Flask Serverless 适配
│   └── env                 # 环境变量
├── frontend/               # Vue 3 前端
├── app/                    # Flask 后端
├── app.py                  # Flask 入口
├── netlify.toml            # Netlify 配置
└── requirements.txt        # Python 依赖
```

---

## 🚀 部署步骤

### 步骤 1：创建 GitHub 仓库

```bash
cd f:\ne3\CMS-master
git init
git add .
git commit -m "Initial commit - CodeMind Studio"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/codemind-studio.git
git push -u origin main
```

### 步骤 2：注册 Netlify

1. 访问 [netlify.com](https://netlify.com)
2. 点击 **Get Started**
3. 使用 **GitHub** 账号登录
4. **无需银行卡！**

### 步骤 3：创建 Netlify 站点

1. 点击 **Add new site** → **Import an existing project**
2. 选择 GitHub 仓库 `YOUR_USERNAME/codemind-studio`

### 步骤 4：配置构建

Netlify 会自动从 `netlify.toml` 读取配置：

| 配置项 | 值 |
|--------|-----|
| **Build command** | `cd frontend && npm install && npm run build` |
| **Publish directory** | `frontend/dist` |
| **Functions directory** | `netlify/functions` |

### 步骤 5：设置环境变量

在 Netlify Dashboard → Site Settings → Build & Deploy → Environment 中添加：

| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | `postgresql://postgres:0zRH7mlijXinntXg@db.xqwbtufemsickddncnsm.supabase.co:5432/postgres` |
| `SECRET_KEY` | `codemind_studio_secret_key_2024` |
| `CORS_ORIGINS` | `https://codemind-studio.netlify.app,http://localhost:5173` |
| `PYTHON_VERSION` | `3.10.0` |

### 步骤 6：启动部署

1. 点击 **Deploy site**
2. 等待 3-5 分钟
3. 部署完成后获取 URL：`https://codemind-studio.netlify.app`

---

## ✅ 验证清单

| 测试项 | 操作 | 预期结果 |
|--------|------|----------|
| **首页** | 访问 `https://codemind-studio.netlify.app` | 显示 CodeMind Studio |
| **后端健康检查** | 访问 `.../health` | 返回 JSON |
| **用户注册** | 打开网站 → 注册 | 注册成功 |
| **用户登录** | 用刚注册的账号登录 | 进入主页 |
| **题库加载** | 登录后访问题库 | 显示题目列表 |

---

## ⚠️ 注意事项

### Netlify Functions 限制
- **执行时间**：免费版 26 秒/请求
- **内存**：1024MB
- **冷启动**：首次请求约 1-3 秒

### 本地开发

本地开发时，直接运行 Flask：
```bash
cd f:\ne3\CMS-master
python app.py
```

### 数据库

继续使用 Supabase PostgreSQL：
- **项目 URL**: `https://xqwbtufemsickddncnsm.supabase.co`
- **连接字符串** 已配置在 `.netlify/env` 中

---

## 🔧 常见问题

### Q: 部署失败？
查看日志：Netlify Dashboard → Site → Deploy → Log

### Q: Function 超时？
Netlify Functions 免费版有 26 秒限制，复杂查询可能超时。

### Q: 数据库连接失败？
检查环境变量 `DATABASE_URL` 是否正确。

### Q: 页面空白？
检查前端构建是否成功：`cd frontend && npm run build`

---

## 📚 相关文件

| 文件 | 用途 |
|------|------|
| [netlify.toml](file:///f:/ne3/CMS-master/netlify.toml) | Netlify 配置 |
| [netlify/functions/app.py](file:///f:/ne3/CMS-master/netlify/functions/app.py) | Flask Serverless 适配 |
| [.netlify/env](file:///f:/ne3/CMS-master/.netlify/env) | 环境变量 |

---

**文档版本**: v1.0
**最后更新**: 2026-08-10