import re

def parse_markdown_problem(markdown_text):
    """
    解析 Markdown 格式的题目描述，提取输入输出格式和测试用例数量。

    参数:
        markdown_text (str): 包含题目描述的 Markdown 文本。

    返回:
        dict: 包含输入格式、输出格式和测试用例数量的字典。
    """
    # 初始化结果容器
    result = {
        "input_format": "",
        "output_format": "",
        "test_cases_count": 0
    }

    # 使用正则表达式提取输入描述
    input_match = re.search(r"### 输入描述([\s\S]*?)###", markdown_text)
    if input_match:
        result["input_format"] = input_match.group(1).strip()

    # 使用正则表达式提取输出描述
    output_match = re.search(r"### 输出描述([\s\S]*?)###", markdown_text)
    if output_match:
        result["output_format"] = output_match.group(1).strip()

    # 使用正则表达式提取测试用例部分
    test_cases_match = re.findall(r"- 输入([\s\S]*?)- 输出([\s\S]*?)(?=- 输入|- 示例|$)", markdown_text)
    if test_cases_match:
        result["test_cases_count"] = len(test_cases_match)

    return result
