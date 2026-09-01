"""
Model 基类
    AI 模型（代码审查/出题/批改）。使用 Ollama 本地大模型，
    全程零 API Token、完全离线。

    协议：Ollama /v1/chat/completions（OpenAI 兼容）
    默认服务地址：http://localhost:11434/v1
    默认模型：qwen2.5:7b（可通过 OLLAMA_MODEL 环境变量全局覆盖）
"""

import os
from typing import Optional, Union, Dict, List


class Model:
    """
    属性:
        model_id (str): 模型唯一标识符（业务用）
        model_name (str): 模型中文名称（展示用）
        model_prompt (str): 系统提示词（System Prompt）
        ollama_model_name (str|None): 模型专属 Ollama 模型名；None 时走全局 OLLAMA_MODEL
        temperature / top_p / frequency_penalty / presence_penalty: 生成参数
        stop (list|str): 停止词（可选）
        logit_bias (dict): 词汇偏置（可选）
    """
    model_id: str = None
    model_name: str = None
    model_prompt: str = None

    temperature: float = None
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    stop: Optional[Union[str, List[str]]] = None
    logit_bias: Optional[Dict[str, float]] = None

    # ---- Ollama 字段 ----
    ollama_model_name: str = None

    # ----- 已废弃（原火山引擎字段，留空防 AttributeError） -----
    # 2026-08-27：用户明确要求"去掉所有需要 Token 的方式"，只保留 Ollama
    model_ark_id: str = None
    model_ark_url: str = None
    model_ark_key: str = None

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------
    @staticmethod
    def get_ollama_base_url() -> str:
        return os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434/v1"
        )

    def get_ollama_model_name(self) -> str:
        """优先级：模型自身 ollama_model_name → 环境变量 OLLAMA_MODEL → 默认 qwen2.5:7b"""
        return (
            self.ollama_model_name
            or os.environ.get("OLLAMA_MODEL")
            or "qwen2.5:7b"
        )
