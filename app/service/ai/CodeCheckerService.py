# app/service/ai/CodeCheckerService.py

"""
CodeChecker 代码质量检查服务模块

功能：
1. 处理代码/文档质量检查请求
2. 调用本地 Ollama 大模型进行质量分析（零 Token、离线）
3. 解析和修复 API 返回结果
4. 格式化检查结果输出
"""

from typing import Optional, List, Dict
from app.models.ai import CodeChecker
from app.service.ai.volcengine_api_caller import volcengine_api_caller
from app.utils.response_processor import APIResponseProcessor


class CodeCheckerService:
    function_mapping = {
        "code-commenting": "代码注释和功能校对",
        "code-documentation": "代码文档和功能校对",
        "missing-comment": "缺失注释和文档预警",
        "code-conformance": "代码规范性预警"
    }

    def __init__(self):
        self.model = CodeChecker()

    def check_code(
            self,
            functions: str,
            code_content: Optional[str] = None,
            doc_content: Optional[str] = None
    ) -> Dict:
        """
        执行代码质量检查

        :param functions: 逗号分隔的功能选项字符串
        :param code_content: 待检查的代码内容
        :param doc_content: 待检查的文档内容
        :return: 结构化检查结果
        """
        # 参数校验
        selected_functions = self._parse_functions(functions)
        self._validate_input(selected_functions, code_content, doc_content)

        # 构建请求内容
        request_content = self._build_request_content(
            selected_functions,
            code_content,
            doc_content
        )

        # 调用API并处理响应
        response = volcengine_api_caller(self.model, request_content)
        result = APIResponseProcessor.process_response(response)

        return self._parse_result(result)

    def _parse_functions(self, functions_str: str) -> List[str]:
        """解析功能选项字符串"""
        if not functions_str:
            raise ValueError("缺失功能选项")
        return [f.strip() for f in functions_str.split(",")]

    def _validate_input(
            self,
            functions: List[str],
            code_content: Optional[str],
            doc_content: Optional[str]
    ):
        """输入参数验证"""
        requires_content = any(func in [
            "代码注释和功能校对",
            "代码文档和功能校对",
            "缺失注释和文档预警"
            "代码规范性预警"
        ] for func in functions)

        if requires_content and not (code_content or doc_content):
            raise ValueError("缺失必要内容")

    def _build_request_content(
            self,
            functions: List[str],
            code: Optional[str],
            doc: Optional[str]
    ) -> str:
        """构建符合模型要求的请求内容"""
        content_lines = [
            "功能选项：",
            ", ".join(functions),
            "\n附加内容："
        ]

        if code:
            content_lines.extend(["【代码内容】", code])
        if doc:
            content_lines.extend(["【文档内容】", doc])

        return "\n".join(content_lines)

    def _parse_result(self, raw_result: Dict) -> Dict:
        """解析原始检查结果"""
        required_keys = ["selected_functions", "analysis_results"]
        if not all(key in raw_result for key in required_keys):
            raise ValueError("无效的API响应结构")

        return {
            "selected": raw_result["selected_functions"],
            "results": self._categorize_results(raw_result["analysis_results"]),
            "input_type": raw_result.get("input_type", "未知类型")
        }

    def _categorize_results(self, analysis: Dict) -> Dict:
        """分类整理分析结果"""
        return {
            "comment_issues": analysis.get("comment_check", []),
            "doc_issues": analysis.get("doc_check", []),
            "missing_warnings": analysis.get("missing_warnings", []),
            "style_issues": analysis.get("style_warnings", [])
        }

    def format_result(self, parsed_result: Dict) -> str:
        """格式化检查结果输出"""
        output = [
            f"代码质量检查报告（输入类型：{parsed_result['input_type']}）",
            "已选功能：" + ", ".join(parsed_result["selected"])
        ]

        result_sections = [
            ("注释问题", "comment_issues"),
            ("文档问题", "doc_issues"),
            ("缺失警告", "missing_warnings"),
            ("规范问题", "style_issues")
        ]

        for title, key in result_sections:
            if issues := parsed_result["results"].get(key):
                output.append(f"\n{title}：")
                output.extend([f"- {item}" for item in issues])
        return "\n".join(output)


def check_code(
        functions: str,
        code_content: Optional[str] = None,
        doc_content: Optional[str] = None
):
    """
    执行代码质量检查
    :param functions: 逗号分隔的功能选项字符串
    :param code_content: 待检查的代码内容
    :param doc_content: 待检查的文档内容
    :return: 结构化检查结果
    """
    _service = CodeCheckerService()
    _review_result = _service.check_code(functions, code_content, doc_content)
    _parsed_result = _service.format_result(_review_result)
    print(_parsed_result)
    _result = {"function": functions, "result": _parsed_result}
    return _result


if __name__ == "__main__":
    # 初始化服务
    service = CodeCheckerService()

    # 用户代码
    user_code = """
#输出4行字符's'并每行递增一个
def test():
    for i in '123':
        print(i*'s')
"""

    try:
        # 调用代码审查
        review_result = service.check_code(functions="代码注释和功能校对,代码规范性预警", code_content=user_code)

        # 解析审查结果
        parsed_result = service.format_result(review_result)

        # 输出结果
        print("代码审查结果：")
        print(parsed_result, "\n\n", review_result)
    except Exception as e:
        print(f"发生错误: {e}")
