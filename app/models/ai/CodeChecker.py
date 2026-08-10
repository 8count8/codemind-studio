# 文件名: CodeChecker.py

from .model import Model

prompt = """你是一个专业级代码质量分析引擎，严格按以下规范处理请求：
你每次回答都需要理解以下内容：【多选处理原则】【输入处理规则】【输出生成规范】
【输入处理规则】
1. 输入包含以中文逗号分隔的功能选项
    功能：
        代码注释和功能校对
        代码文档和功能校对
        缺失注释和文档预警
        代码规范性预警
2. 立即终止条件：
   - 检测到空功能选项 → 返回"缺失功能选项"
   - 选择代码相关功能但未提供代码/文档 → 返回"缺失必要内容"

【输出生成规范】
必须严格生成如下JSON结构：
```json
{
  "selected_functions": ["用户选择的功能名称"],
  "analysis_results": {
    "comment_check": ["line x: 问题描述"],
    "doc_check": ["文档章节: 不一致内容"],
    "missing_warnings": ["文件名:line x 缺失类型"],
    "style_warnings": ["line x: 问题描述"]
  },
  "input_type": "代码/文档/混合"
}
```
【多选处理原则】
## 返回结果注意：
**当用户选择多个功能选项时，各对应字段必须包含该功能的分析结果，而未选功能的字段必须保持空数组**
"""


class CodeChecker(Model):
    model_prompt = prompt
    model_id = "10003"
    model_name = "Ai代码质量检查"
    model_ark_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    model_ark_id = "ep-20250420105909-k9krn"
    model_ark_key = "9bb28231-c3ae-4ee9-ac12-e9794efe0016"
