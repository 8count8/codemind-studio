"""
ollama_routes.py —— Ollama 本地大模型状态 + 拉模型 API

供前端"设置页 (SettingsView)"使用：
  1. GET  /api/ollama/status     -> 检查 Ollama 服务是否在线、已安装模型、默认模型
  2. POST /api/ollama/pull       -> 后台拉一个模型（流式日志写入内存）
  3. GET  /api/ollama/pull_log   -> 轮询拉取进度日志（纯文本 / JSON）

完全不需要任何 API Token，只跟本地 http://localhost:11434 通信。
"""
from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from collections import deque
from typing import Dict, List

import requests
from flask import jsonify, request

from . import ollama_bp

log = logging.getLogger('ollama_routes')

# 全局：拉模型日志（默认最多保留 1000 行，环形缓冲）
_MAX_LOG_LINES = 1000
_pull_state_lock = threading.Lock()
_pull_state: Dict = {
    "running": False,
    "model": None,
    "started_at": None,
    "finished_at": None,
    "success": None,
    "log": deque(maxlen=_MAX_LOG_LINES),
}


def _ollama_base() -> str:
    """Ollama 基础地址（不含 /v1），用于 Ollama 原生管理接口"""
    v1 = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1").strip().rstrip("/")
    # 常见约定 <host>:<port>/v1/... -> 管理接口就在 <host>:<port>
    if v1.endswith("/v1"):
        return v1[:-3].rstrip("/") or "http://localhost:11434"
    return v1 or "http://localhost:11434"


def _default_model() -> str:
    return os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")


def _append_log(line: str) -> None:
    with _pull_state_lock:
        _pull_state["log"].append(f"[{time.strftime('%H:%M:%S')}] {line}")


# ============================================================
# C2.1  Ollama 状态
# ============================================================
@ollama_bp.route('/api/ollama/status', methods=['GET'])
def ollama_status():
    base = _ollama_base()
    default_model = _default_model()
    info: Dict = {
        "base_url": base + "/v1",
        "manage_url": base,
        "default_model": default_model,
        "reachable": False,
        "version": None,
        "models": [],                 # [{name, size, modified_at, digest}]
        "pulling": None,              # 正在拉的状态（见 _pull_state）
        "downloads": {
            # 常用模型的下载方式（纯信息性，前端可直接展示）
            "official": "https://ollama.com/download",
            "mirror_note": (
                "国内加速：先 set OLLAMA_HOST=0.0.0.0:11434 ；"
                "再 set OLLAMA_MODELS=D:\\ollama\\models （可选自定义目录）；"
                "然后使用镜像代理： https://mirrors.sdu.edu.cn/docs/mirrors/ollama.html"
            ),
            "recommended_models": [
                {"tag": "qwen2.5:7b",            "size_gb": 4.7, "desc": "通用首选（综合中文+代码）"},
                {"tag": "qwen2.5-coder:7b",      "size_gb": 4.5, "desc": "代码审查更强"},
                {"tag": "qwen2.5:14b",           "size_gb": 9.0, "desc": "综合质量更好（16GB 显存推荐）"},
                {"tag": "deepseek-coder-v2:16b", "size_gb": 9.5, "desc": "代码专业模型（16GB 显存推荐）"},
            ]
        }
    }

    # 1) 管理端健康检查
    try:
        r = requests.get(f"{base}/api/tags", timeout=5)
        if r.status_code == 200:
            info["reachable"] = True
            info["models"] = (r.json() or {}).get("models", []) or []
    except Exception as e:
        log.warning("Ollama /api/tags 不可达: %s", e)

    # 2) 版本
    if info["reachable"]:
        try:
            rv = requests.get(f"{base}/api/version", timeout=3)
            if rv.status_code == 200:
                info["version"] = (rv.json() or {}).get("version")
        except Exception:
            pass

    # 3) 正在拉模型？
    with _pull_state_lock:
        info["pulling"] = {
            "running": _pull_state["running"],
            "model": _pull_state["model"],
            "started_at": _pull_state["started_at"],
            "finished_at": _pull_state["finished_at"],
            "success": _pull_state["success"],
            "log_tail": list(_pull_state["log"])[-80:],  # 只返回末尾 80 行
        }

    return jsonify({"status": 200, "data": info})


# ============================================================
# C2.2  拉模型（后台线程，避免 HTTP 超时）
# ============================================================
@ollama_bp.route('/api/ollama/pull', methods=['POST'])
def ollama_pull():
    body = request.get_json(silent=True) or {}
    model = (body.get("model") or "").strip() or _default_model()
    # 简单安全校验
    if len(model) > 120 or any(c in model for c in ";&|`$\n\r"):
        return jsonify({"status": 400, "message": "非法的模型名"}), 400

    with _pull_state_lock:
        if _pull_state["running"]:
            return jsonify({
                "status": 409,
                "message": f"已有拉取任务正在进行：{_pull_state['model']}",
                "running_model": _pull_state["model"],
            }), 409
        _pull_state["running"] = True
        _pull_state["model"] = model
        _pull_state["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        _pull_state["finished_at"] = None
        _pull_state["success"] = None
        _pull_state["log"].clear()

    t = threading.Thread(target=_do_pull, args=(model,), daemon=True)
    t.start()
    return jsonify({
        "status": 200,
        "message": f"已开始后台拉取模型 {model}，请通过 /api/ollama/status 或 /api/ollama/pull_log 查看进度",
        "model": model,
    })


def _do_pull(model: str) -> None:
    """后台拉模型实现：优先走 Ollama HTTP /api/pull；失败再回退子进程 ollama pull"""
    base = _ollama_base()
    _append_log(f"开始拉取模型: {model}")
    _append_log(f"Ollama 管理地址: {base}")

    success = False
    try:
        # --- 方案 A: 调 Ollama HTTP 管理接口（会流式吐进度） ---
        url = f"{base}/api/pull"
        _append_log(f"POST {url}  {{name: {model}}}")
        r = requests.post(url, json={"name": model, "stream": True}, timeout=60 * 120, stream=True)
        if r.status_code == 200:
            for raw in r.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                try:
                    j = __import__("json").loads(raw)
                except Exception:
                    _append_log(raw[:300])
                    continue
                status = j.get("status") or ""
                total = j.get("total")
                completed = j.get("completed")
                digest = j.get("digest") or ""
                if total and completed:
                    pct = int(completed * 100 / total)
                    _append_log(f"{status}  {digest[:12]}  {pct}%  ({completed}/{total})")
                else:
                    _append_log(status + (f"  {digest[:12]}" if digest else ""))
                if "success" in status.lower():
                    success = True
        else:
            _append_log(f"Ollama HTTP 拉取失败 status={r.status_code} body={r.text[:300]}")
    except Exception as e:
        _append_log(f"Ollama HTTP 拉取异常: {e}")

    # --- 方案 B: 回退到子进程 ollama pull（适合 Docker / 用户自己配了 CLI） ---
    if not success:
        _append_log("回退到子进程 `ollama pull` ...")
        try:
            proc = subprocess.Popen(
                ["ollama", "pull", model],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                _append_log(line.rstrip())
            proc.wait(timeout=60 * 120)
            success = (proc.returncode == 0)
        except FileNotFoundError:
            _append_log("未找到 ollama 可执行文件。请先安装 Ollama：https://ollama.com/download")
            success = False
        except Exception as e:
            _append_log(f"子进程拉取异常: {e}")
            success = False

    with _pull_state_lock:
        _pull_state["running"] = False
        _pull_state["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        _pull_state["success"] = success
    _append_log("完成。" + ("成功" if success else "失败，请检查网络或查看上方日志。"))


# ============================================================
# C2.3  拉取日志（前端轮询）
# ============================================================
@ollama_bp.route('/api/ollama/pull_log', methods=['GET'])
def ollama_pull_log():
    tail = int(request.args.get("tail", 200))
    with _pull_state_lock:
        log_lines: List[str] = list(_pull_state["log"])[-max(1, tail):]
        snapshot = {
            "running": _pull_state["running"],
            "model": _pull_state["model"],
            "started_at": _pull_state["started_at"],
            "finished_at": _pull_state["finished_at"],
            "success": _pull_state["success"],
        }
    return jsonify({
        "status": 200,
        "data": {**snapshot, "log": log_lines}
    })
