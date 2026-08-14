"""
调用AI接口生成算法题目，并调用models中的相关函数将其存储到数据库中。
使用异步处理让题目无论存储到数据库中与否，都能够正常显示在前端。
"""
import json
import logging
import re
import uuid
from datetime import datetime

from app.models.ai import AlgorithmProblemGenerator
from app.models.save_problem import save_problem_to_database
from app.models.save_problem import save_test_cases_to_database
from app.service.ai.volcengine_api_caller import volcengine_api_caller


def parse_algorithm_problem_response(response):
    """
    解析AI接口返回的算法题目结果

    参数:
        response (dict): AI接口返回的原始JSON数据

    返回:
        dict: 包含解析后的算法题目的数据结构
    """
    # 检查响应是否包含错误
    if "error" in response:
        return {"error": response["error"]}

    try:
        # 从response中获取实际内容
        if "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0]["message"]["content"]
            
            # 处理无效的控制字符
            # 替换所有ASCII控制字符(0-31)除了\n, \r, \t
            content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)

            # 去除多余的字符（如 ```json\n 和 `\n```）
            if content.startswith('```json\n') and content.endswith('\n```'):
                content = content[8:-4]

            # 解析JSON格式的内容
            try:
                json_content = json.loads(content)
                response = json_content  # 将解析后的JSON内容赋值给response
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析错误: {e}, 尝试修复JSON字符串")
                # 记录原始内容用于调试
                logging.debug(f"原始内容: {content[:200]}...")

                # 尝试使用更宽松的解析方式
                import ast
                try:
                    # 尝试将单引号替换为双引号，并使用ast.literal_eval
                    fixed_content = content.replace("'", "\"")
                    json_content = json.loads(fixed_content)
                    response = json_content
                    logging.info("成功修复JSON并解析")
                except Exception:
                    # 如果仍然失败，则返回错误
                    return {"error": f"无法解析JSON响应: {str(e)}"}

        # 提取题目信息
        problem_type = response.get("题目类型", "")
        difficulty_level = response.get("题目难度", "")
        problem_description = response.get("题目描述", "")
        test_case_inputs = response.get("测试用例输入", [])
        test_case_outputs = response.get("测试用例输出", [])

        # 增强标签处理逻辑
        tags = response.get("标签", [])
        # 如果标签是字符串，转换为列表
        if isinstance(tags, str):
            # 检查是否有逗号分隔，如果有则按逗号分割
            if ',' in tags:
                tags = [tag.strip() for tag in tags.split(',')]
            elif '，' in tags:
                tags = [tag.strip() for tag in tags.split('，')]
            else:
                tags = [tags]
        # 如果标签不是列表或字符串，则使用算法类型作为默认标签
        elif not isinstance(tags, list):
            tags = [str(tags)]

        # 如果标签列表为空，使用算法类型作为标签
        if not tags:
            tags = [problem_type] if problem_type else ["算法题"]

        # 记录日志
        logging.info(f"解析得到的标签: {tags}")

        title = response.get("题目标题", problem_type)

        # 合法的难度值
        valid_difficulties = ["简单", "中等", "困难"]

        # 验证必要字段是否存在
        if not problem_type or not difficulty_level or not problem_description:
            return {"error": "返回的题目信息不完整"}

        # 验证 difficulty_level 是否合法
        if difficulty_level not in valid_difficulties:
            return {"error": f"返回的难度等级无效：{difficulty_level}"}

        # 构造解析后的结果，添加ID和创建时间以便于前端展示
        parsed_result = {
            "id": str(uuid.uuid4()),
            "algorithm_type": problem_type,
            "difficulty_level": difficulty_level,
            "description": problem_description,
            "test_cases": [
                {"input": inp, "output": out}
                for inp, out in zip(test_case_inputs, test_case_outputs)
            ],
            "tags": tags,
            "title": title,
            "created_at": datetime.now().isoformat()
        }

        return parsed_result

    except Exception as e:
        logging.error(f"解析题目时出错: {str(e)}")
        return {"error": f"解析响应时发生错误：{str(e)}"}


def generate_algorithm_problem(algorithm_type: str, difficulty_level: str):
    """
    调用AI生成算法题目

    参数:
        algorithm_type (str): 算法类型，例如 "排序算法"、"查找算法" 等
        difficulty_level (str): 难度等级，可选值为 "简单"、"中等"、"困难"

    返回:
        dict: 包含生成的算法题目的JSON数据
    """
    # 构造用户输入的消息
    user_input = f"请生成一道{difficulty_level}难度的{algorithm_type}题目，要求题目有实际应用场景和情境描述，不要仅使用算法类型作为题目名称，而是应该有一个概括性的、有实际意义的题目标题。请提供完整的题目内容、标签、测试用例等信息，以JSON格式返回。"

    # 检查输入是否符合要求
    if not algorithm_type or not difficulty_level:
        return {"error": "缺失算法类型或难度等级"}

    if difficulty_level not in ["简单", "中等", "困难"]:
        return {"error": "输入内容不符合要求"}

    # 创建模型实例
    model = AlgorithmProblemGenerator()

    # 调用火山API生成算法题目，使用重试机制
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = volcengine_api_caller(model=model, message=user_input)
            
            # 解析API响应
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(result)
                    # 解析返回的算法题目
                    parsed_result = parse_algorithm_problem_response(result)
                    
                    # 检查解析是否成功
                    if "error" in parsed_result and retry_count < max_retries - 1:
                        logging.warning(f"解析失败 (尝试 {retry_count+1}/{max_retries}): {parsed_result['error']}")
                        retry_count += 1
                        continue
                    
                    return parsed_result
                    
                except ValueError as e:
                    if retry_count < max_retries - 1:
                        logging.error(f"API响应解析失败 (尝试 {retry_count+1}/{max_retries}): {str(e)}")
                        retry_count += 1
                        continue
                    else:
                        logging.error(f"API响应解析失败 (最终尝试): {str(e)}")
                        return {"error": f"API响应格式错误: {str(e)}"}
            else:
                if retry_count < max_retries - 1:
                    logging.error(f"API调用失败 (尝试 {retry_count+1}/{max_retries}), 状态码: {response.status_code}")
                    retry_count += 1
                    continue
                else:
                    logging.error(f"API调用失败 (最终尝试), 状态码: {response.status_code}, 响应: {response.text[:200]}")
                    return {"error": f"API调用失败，状态码：{response.status_code}"}
                    
        except Exception as e:
            if retry_count < max_retries - 1:
                logging.error(f"发生异常 (尝试 {retry_count+1}/{max_retries}): {str(e)}")
                retry_count += 1
                continue
            else:
                logging.error(f"发生异常 (最终尝试): {str(e)}")
                return {"error": f"调用API时发生异常: {str(e)}"}
            
        # 增加重试计数
        retry_count += 1
    
    # 如果所有重试都失败
    return {"error": "多次尝试生成题目均失败，请稍后再试"}


# 配置日志记录
logging.basicConfig(level=logging.INFO)


def generate_and_save_algorithm_problem(algorithm_type: str, difficulty_level: str):
    """
    调用AI生成算法题目，并将其存储到数据库中

    参数:
        algorithm_type (str): 算法类型，例如 "排序算法"、"查找算法" 等
        difficulty_level (str): 难度等级，可选值为 "简单"、"中等"、"困难"

    返回:
        dict: 包含生成结果或错误信息的字典
    """
    # 调用生成算法题目的函数
    result = generate_algorithm_problem(algorithm_type, difficulty_level)

    # 检查生成是否成功
    if "error" in result:
        logging.error(f"生成题目失败: {result['error']}")
        return result

    # 提取生成的题目数据
    problem_data = result
    if not problem_data:
        return {"error": "生成的题目数据为空"}

    # 转换测试用例为Markdown格式
    test_cases_md = ""
    if "test_cases" in problem_data and problem_data["test_cases"]:
        test_cases_md = "\n\n### 测试用例\n\n"
        for i, tc in enumerate(problem_data["test_cases"], 1):
            test_cases_md += f"**示例 {i}:**\n\n"
            test_cases_md += f"输入: `{tc['input']}`\n\n"
            test_cases_md += f"输出: `{tc['output']}`\n\n"

    # 准备Markdown内容
    content_markdown = f"# {problem_data.get('title', '算法题')}\n\n"
    content_markdown += f"## 描述\n\n{problem_data.get('description', '')}\n\n"
    content_markdown += test_cases_md

    # 确保tags是可用的
    tags = problem_data.get('tags', [])
    if not tags:
        tags = [algorithm_type]
    logging.info(f"准备保存题目，标签为: {tags}")

    # 异步存储题目到数据库
    def async_save():
        try:
            problem_id = save_problem_to_database(
                title=problem_data.get('title', f"{algorithm_type}题目"),
                content=content_markdown,
                difficulty=problem_data.get('difficulty_level', difficulty_level),
                tags=tags
            )
            problem_data["id"] = problem_id
            # print(problem_data)
            logging.info(f"成功存储题目，题目 ID: {problem_id}")
            # 如果有测试用例，则保存测试用例
            if "test_cases" in problem_data and problem_data["test_cases"]:
                test_cases_saved = save_test_cases_to_database(
                    problem_id=problem_id,
                    test_cases=problem_data["test_cases"]
                )
                if not test_cases_saved:
                    logging.warning("存储测试用例失败，请检查数据库连接或输入数据")

            logging.info(f"成功存储题目和测试用例: {problem_data.get('title', '未命名题目')}")

        except Exception as e:
            logging.error(f"存储题目时发生异常：{str(e)}")

    async_save()

    # 对问题描述进行格式化，适应answerpad的展示格式
    problem_data['description'] = content_markdown

    # 返回生成的题目数据给前端
    logging.info(f"成功生成题目: {problem_data.get('title', '未命名题目')}")
    # print("a\n", problem_data)
    return {"problem": problem_data}
