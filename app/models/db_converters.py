"""
数据库转换器模块 — 数据格式转换

负责:
- dict_to_markdown(): 字典转 Markdown 字符串
"""


def dict_to_markdown(content):
    """将字典格式的内容转换为 Markdown 格式字符串"""
    if isinstance(content, str):
        return content

    markdown_content = ""
    for section, text in content.items():
        if isinstance(text, list):
            markdown_content += f"### {section}\n"
            for example in text:
                markdown_content += f"- {example}\n"
        else:
            markdown_content += f"### {section}\n{text}\n\n"
    return markdown_content.strip()
