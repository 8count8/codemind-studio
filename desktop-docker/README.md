# 桌面版 / Docker 部署相关文件

本目录存放 CodeMind Studio 的 **桌面离线版** 与 **Docker Compose 部署** 相关文件，
**宝塔面板 / 云服务器直接部署不需要本目录**。

## 文件清单

### Docker Compose 部署

| 文件 | 用途 |
|------|------|
| `Dockerfile.backend` | 后端 Flask 镜像构建文件 |
| `Dockerfile.frontend` | 前端 Nginx 镜像构建文件 |
| `docker-compose.yml` | Docker Compose 编排（含 MySQL/Ollama/沙箱） |
| `docker-compose.gpu.yml` | GPU 加速版 Compose（叠加使用） |
| `.env.docker.example` | Docker 环境变量模板 |
| `.dockerignore` | Docker 构建忽略清单 |

### 代码执行沙箱镜像

`sandbox-images/` 目录下是 5 种语言（C/C++/Java/JS/Python）的沙箱运行时镜像构建文件。
宝塔部署若需在线判题（OJ）功能，需在服务器上安装 Docker 并构建这些镜像；
沙箱核心逻辑在 `app/Docker/sandbox.py`（已保留在原位置，被 `CodeRunService` 引用）。

### 桌面离线版

| 文件 | 用途 |
|------|------|
| `requirements-desktop.txt` | 桌面版额外依赖（PyInstaller + Waitress） |

## 使用方式

- **Docker 部署**：参考根目录 `docs/7.部署手册.md`
- **桌面版打包**：参考 `packaging/docker-distribute/` 目录
