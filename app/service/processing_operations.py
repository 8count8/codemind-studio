import os
import uuid
import re

# 判断文件内容的语言类型
def detect_language(content, file_extension=None):
    # 定义每种语言的关键字和正则表达式
    language_keywords = {
        "py": {"keywords": ["def ", "import ", "class ", "__name__"], "regex": r"def\s+\w+\s*$.*$"},
        "java": {"keywords": ["public class", "System.out.println", "extends", "implements"], "regex": r"public\s+class\s+\w+"},
        "js": {"keywords": ["function ", "console.log", "let ", "const ", "var "], "regex": r"function\s+\w*\s*$.*$"},
        "cpp": {"keywords": ["#include", "using namespace", "std::", "int main"], "regex": r"#include\s*[<\"].*[>\"]"},
        "c": {"keywords": ["#include", "int main", "printf", "scanf"], "regex": r"#include\s*[<\"].*[>\"]"},
        "txt": {"keywords": [], "regex": None}  # 默认为文本文件
    }

    # 根据文件扩展名直接判断语言
    if file_extension:
        file_extension = file_extension.lower()
        if file_extension in language_keywords:
            return file_extension[1:]  # 去掉点号（如 ".py" -> "py"）

    # 如果没有扩展名或需要进一步确认，通过内容判断
    for lang, patterns in language_keywords.items():
        # 检查关键字
        if any(keyword in content for keyword in patterns["keywords"]):
            return lang
        # 检查正则表达式
        if patterns["regex"] and re.search(patterns["regex"], content):
            return lang

    # 如果无法判断，默认返回 "txt"
    return "txt"

# 根据检测到的语言类型，将非代码文件转换为对应的代码内容
def convert_to_code(content, language):
    if language == "py":
        return f"# Converted Python code\n{content}"
    elif language == "java":
        return f"// Converted Java code\npublic class Generated {{\npublic static void main(String[] args) {{\nSystem.out.println(\"{content}\");\n}}\n}}"
    elif language == "js":
        return f"// Converted JavaScript code\nconsole.log(\"{content}\");"
    else:
        return content

# 处理上传文件，判断语言类型并生成代码文件
def process_uploaded_file(file_path):
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower()

    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # 如果不是代码文件，尝试判断语言并生成代码文件
    if file_extension not in ['.py', '.java', '.js', '.cpp','c']:
        detected_language = detect_language(file_content)
        new_file_name = f"{uuid.uuid4()}.{detected_language}"
        file_type = detected_language
        file_content = convert_to_code(file_content, detected_language)
    else:
        new_file_name = file_name
        file_type = file_extension[1:]  # 去掉点号

    return new_file_name, file_type, file_content