"""
ollama_api_caller (原文件名 volcengine_api_caller，保留旧别名以兼容)
    调用本地 Ollama 大模型服务进行 AI 推理。

**特性：**
  · 全程零 API Token、完全离线、零费用
  · 协议：Ollama /v1/chat/completions（OpenAI Chat 兼容）
  · 默认地址：http://localhost:11434/v1
  · 超时 300 秒（7B 模型推理较慢）
  · 连接失败时给出明确的安装/启动指南，而不是报 ConnectionError

**兼容调用点（无需改名即可使用）：**
  · from app.service.ai.volcengine_api_caller import volcengine_api_caller
"""

import logging
import os
import requests
from app.models.ai import Model, CodeInsightExaminer
from app.service.ai import ChatCompletionRequest

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 向后兼容：旧 import 名称不改动
# ---------------------------------------------------------------------------
def volcengine_api_caller(model: Model, message, message_list: list = None):
    """旧调用点（volcengine_api_caller）→ 转发到本地 Ollama"""
    return ollama_api_caller(model, message, message_list)


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def llm_api_caller(model: Model, message, message_list: list = None):
    """对外推荐的调用名（通用名）。转发到 ollama_api_caller。"""
    return ollama_api_caller(model, message, message_list)


def ollama_api_caller(model: Model, message, message_list: list = None):
    """
    请求本地 Ollama 服务：POST {base_url}/chat/completions

    Args:
        model:         AI 模型实例（CodeChecker / CodeInsightExaminer / AlgorithmProblemGenerator）
        message:       str 或 list[dict] — 用户输入
        message_list:  历史消息列表（多轮对话）

    Returns:
        requests.Response：与原 volcengine_api_caller 完全同构，调用方零改造。
    """
    base_url = Model.get_ollama_base_url().rstrip("/")
    endpoint = f"{base_url}/chat/completions"
    headers = {"Content-Type": "application/json"}   # 本地 Ollama 不需要 Authorization

    body = ChatCompletionRequest(
        model=model,
        message=message,
        messages_list=message_list,
    )

    ollama_model = model.get_ollama_model_name()
    logger.info(f"[Ollama] POST {endpoint}  model={ollama_model}")

    try:
        # Product SLA is 10 seconds for AI endpoints.  If the local model is
        # unavailable or cold, callers fall back to deterministic analysis.
        timeout_seconds = min(9.0, max(1.0, float(os.getenv("AI_TIMEOUT_SECONDS", "9"))))
        resp = requests.post(endpoint, headers=headers, data=body, timeout=timeout_seconds)
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "\n==============================================================\n"
            " 无法连接到本地 Ollama 服务。请按以下步骤安装启动：\n"
            "\n"
            "   1. 下载安装 Ollama:  https://ollama.com/download\n"
            "   2. 启动服务 (新开终端):  ollama serve\n"
            "   3. 拉取一个模型 (默认 qwen2.5:7b):  ollama pull qwen2.5:7b\n"
            "      其他代码类模型推荐：\n"
            "        ollama pull deepseek-coder-v2:16b   (代码审查更强)\n"
            "        ollama pull qwen2.5-coder:7b        (阿里代码专用)\n"
            "\n"
            "   如需更换模型/地址，请在 .env 中修改：\n"
            "       OLLAMA_BASE_URL=http://localhost:11434/v1\n"
            "       OLLAMA_MODEL=qwen2.5:7b\n"
            "=============================================================="
        ) from None

    return resp


# ---------------------------------------------------------------------------
# CLI 调试：python -m app.service.ai.volcengine_api_caller
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print(f"[DEBUG] Ollama base URL  = {Model.get_ollama_base_url()}")
    m = CodeInsightExaminer()
    print(f"[DEBUG] Ollama model     = {m.get_ollama_model_name()}")
    print(f"[DEBUG] temperature      = {m.temperature}")
    print(f"[DEBUG] top_p            = {m.top_p}")

    try:
        resp = ollama_api_caller(m, "归并排序，简单")
        print(f"\n--- HTTP status: {resp.status_code} ---")
        text = resp.text
        print(text if len(text) < 5000 else text[:5000] + "\n... (已截断)")
    except Exception as e:
        print(f"[ERROR] {e}")
