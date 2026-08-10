# app/utils/response_processor.py

"""
API响应处理工具模块

提供独立于具体服务的通用API响应处理功能：
1. 统一处理HTTP状态码
2. 提取和验证JSON数据结构
3. 修复JSON字符串格式异常
"""

import json
import re
from typing import Dict, Any

class APIResponseProcessor:
    @staticmethod
    def process_response(response) -> Dict[str, Any]:
        """
        完整处理API响应的入口方法

        :param response: requests.Response对象或类似结构的API响应
        :return: 解析后的结构化数据字典
        :raises ValueError: 当响应不符合预期时
        """
        # 状态码检查
        APIResponseProcessor._validate_status_code(response)

        # 解析原始JSON
        raw_data = APIResponseProcessor._parse_raw_json(response)

        # 数据结构验证
        APIResponseProcessor._validate_data_structure(raw_data)

        # 内容提取和解析
        content = raw_data["choices"][0]["message"].get("content", "")
        return APIResponseProcessor.parse_json_content(content)

    @staticmethod
    def _validate_status_code(response):
        """HTTP状态码验证"""
        if response.status_code != 200:
            raise ValueError(
                f"API请求失败，状态码：{response.status_code}\n"
                f"响应内容：{response.text[:200]}..."
            )

    @staticmethod
    def _parse_raw_json(response) -> Dict:
        """原始JSON解析"""
        try:
            return response.json()
        except json.JSONDecodeError:
            # 尝试修复JSON字符串
            text = response.text
            # 简单处理换行问题，将换行符替换为转义字符
            text = text.replace('\n', '\\n')
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                fixed_str = APIResponseProcessor._fix_json_string(text)
                try:
                    return json.loads(fixed_str)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"JSON解析失败: {e}\n"
                        f"原始内容: {text[:200]}...\n"
                        f"修复后内容: {fixed_str[:200]}..."
                    )

    @staticmethod
    def _validate_data_structure(data: Dict):
        """响应数据结构验证"""
        if not (
                isinstance(data.get("choices"), list) and
                len(data["choices"]) > 0 and
                isinstance(data["choices"][0].get("message"), dict)
        ):
            raise ValueError("无效的API响应结构，缺少必要字段")

    @staticmethod
    def parse_json_content(content: str) -> Dict[str, Any]:
        """
        通用JSON内容解析方法（可供其他类直接调用）

        :param content: 包含JSON代码块的原始字符串
        :return: 解析后的字典
        """
        json_str = APIResponseProcessor._extract_json_string(content)
        return APIResponseProcessor._safe_load_json(json_str)

    @staticmethod
    def _extract_json_string(content: str) -> str:
        """提取JSON代码块内容"""
        match = re.search(
            r"```json\s*(.*?)\s*```",
            content,
            re.DOTALL | re.IGNORECASE
        )
        if not match:
            raise ValueError("未找到有效的JSON代码块")
        return match.group(1).strip()

    @staticmethod
    def _safe_load_json(json_str: str) -> Dict:
        """安全加载JSON并自动修复常见问题"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            fixed_str = APIResponseProcessor._fix_json_string(json_str)
            try:
                return json.loads(fixed_str)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"JSON解析失败: {e}\n"
                    f"原始内容: {json_str[:200]}...\n"
                    f"修复后内容: {fixed_str[:200]}..."
                )

    @staticmethod
    def _fix_json_string(json_str: str) -> str:
        """自动修复JSON字符串中的常见格式问题"""
        # 处理未终止的字符串问题
        # 首先检查并修复未配对的引号
        quote_count = json_str.count('"')
        if quote_count % 2 != 0:
            # 尝试找到并修复未闭合的字符串
            fixed_str = json_str
            pattern = r'"([^"\\]*(\\.[^"\\]*)*)'  # 匹配开始但未结束的字符串
            unclosed_strings = re.findall(pattern + '$', fixed_str)
            if unclosed_strings:
                # 为未闭合的字符串添加结束引号
                fixed_str = fixed_str + '"'
            else:
                # 如果是其他引号错误，尝试基本修复
                fixed_str = re.sub(r'([^"\\])"([^:,{\[\s])', r'\1"\2', fixed_str)
            json_str = fixed_str
        
        # 处理未转义的特殊字符
        return re.sub(
            r'"((?:[^"\\]|\\.)*)"',
            lambda m: f'"{json.dumps(m.group(1))[1:-1]}"',
            json_str,
            flags=re.DOTALL
        )