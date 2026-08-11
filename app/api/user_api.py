import uuid
from threading import Thread
import re
import json

from app.api import user_api_bp

from flask import jsonify, request, current_app
from app.utils.auth import require_auth, get_current_user_id
from app.service import QuestionService
from app.service import FavoriteService
from app.service.ai import CodeCheckerService, check_code, CodeReviewService, get_algorithm_review_result
from app.models.user_operation_records import (
    log_function_usage,
    upload_file_to_db,
    log_api_response,
    get_user_history_combined,
)


@user_api_bp.route('/api/questions', methods=['GET'])
def get_questions():
    # 获取所有题目
    result = QuestionService.get_all_questions()
    if 'error' in result:
        return jsonify({"status": 500, "message": result["error"]}), 500

    # 检查 result 的结构
    if isinstance(result, dict) and "questions" in result:
        return jsonify({
            "status": 200,
            "data": result["questions"]
        })
    elif isinstance(result, (list, tuple)) and len(result) > 0 and isinstance(result[0], dict) and "questions" in \
            result[0]:
        return jsonify({
            "status": 200,
            "data": result[0]["questions"]
        })
    else:
        return jsonify({"status": 500, "message": "Invalid data structure returned from QuestionService"}), 500


@user_api_bp.route('/process_code', methods=['POST'])
def process_code():
    """
    处理代码审查请求，返回 JSON 格式的响应。
    """
    # try:
    # 获取审查类型
    review_type = request.form.get('review_type', 'code-commenting')

    # 通用字段
    code_file = request.files.get('code-file')
    pasted_code = request.form.get('paste_code', None)
    doc_file = request.files.get('doc-file', None)
    standard = request.form.get('code-standard', 'google')

    # 提交代码
    submit_code = None
    if code_file:
        submit_code = code_file.read().decode('utf-8')
    elif pasted_code:
        submit_code = pasted_code
    else:
        return jsonify({
            "status": 400,
            "message": "缺少代码文件或粘贴的代码"
        }), 400
    if standard:
        submit_code = f"使用标准：{standard}\ncode:{submit_code}"
    # 根据不同类型处理附加字段
    result = {"function": "未知类型", "result": "未处理"}

    if review_type in CodeCheckerService.function_mapping:
        print(submit_code)
        result = check_code(CodeCheckerService.function_mapping[review_type], submit_code, doc_file)

    # 写入用户操作历史到数据库
    user_id = get_current_user_id()
    if user_id:
        try:
            log_function_usage(user_id, f"code_review_{review_type}")
            upload_id = upload_file_to_db(
                user_id,
                f"code_review_{review_type}_{uuid.uuid4().hex[:8]}.py",
                "python"
            )
            if upload_id:
                log_api_response(
                    upload_id,
                    f"review_result_{review_type}.md",
                    json.dumps(result, ensure_ascii=False)
                )
        except Exception as e:
            current_app.logger.error(f"写入历史记录失败: {e}")

    return jsonify({
        "status": 200,
        "message": "处理成功",
        "results": [result]
    })


# 示例处理函数（需根据实际逻辑实现）
def handle_code_commenting(code_file, pasted_code):
    # 实现注释检查逻辑
    return {
        "function": "代码注释和功能校对",
        "result": "发现3处注释不匹配\n1. main函数缺少功能说明\n2. 变量命名不规范\n3. 复杂逻辑缺少行内注释"
    }


def handle_code_documentation(code_file, pasted_code, doc_file):
    """
    实现代码文档与功能校对逻辑。
    检查代码与相关文档是否匹配，发现不一致的地方。

    :param code_file: 上传的代码文件
    :param pasted_code: 粘贴的代码内容
    :param doc_file: 上传的文档文件
    :return: 校对结果
    """
    # 获取代码内容
    code_content = None
    if code_file:
        code_content = code_file.read().decode('utf-8')
    elif pasted_code:
        code_content = pasted_code

    # 获取文档内容
    doc_content = None
    if doc_file:
        doc_content = doc_file.read().decode('utf-8')

    if not code_content or not doc_content:
        return {
            "function": "代码文档和功能校对",
            "result": "缺少必要的代码或文档内容"
        }

    # 检查代码中的函数名是否在文档中提及
    issues = []
    functions_in_code = set(re.findall(r'def\s+(\w+)\s*\(', code_content))
    for func in functions_in_code:
        if func not in doc_content:
            issues.append(f"函数 '{func}' 在文档中未提及")

    if not issues:
        result_message = "代码与文档匹配，无问题"
    else:
        result_message = "发现以下问题：\n" + "\n".join(issues)

    return {
        "function": "代码文档和功能校对",
        "result": result_message
    }



def handle_missing_comment(code_file, pasted_code):
    """
    实现缺失注释和文档的预警逻辑。
    检查代码中是否存在关键位置缺少注释的情况。

    :param code_file: 上传的代码文件
    :param pasted_code: 粘贴的代码内容
    :return: 预警结果
    """
    # 获取代码内容
    code_content = None
    if code_file:
        code_content = code_file.read().decode('utf-8')
    elif pasted_code:
        code_content = pasted_code

    if not code_content:
        return {
            "function": "缺失注释和文档预警",
            "result": "缺少代码内容"
        }

    # 检查函数定义、类定义等是否有注释
    issues = []
    lines = code_content.split("\n")
    for i, line in enumerate(lines):
        if re.match(r'^\s*def\s+\w+\s*\(', line):  # 函数定义
            if i == 0 or not lines[i - 1].strip().startswith("#"):
                issues.append(f"第 {i + 1} 行：函数定义缺少注释")
        elif re.match(r'^\s*class\s+\w+\s*\(', line):  # 类定义
            if i == 0 or not lines[i - 1].strip().startswith("#"):
                issues.append(f"第 {i + 1} 行：类定义缺少注释")

    if not issues:
        result_message = "代码注释完整，无问题"
    else:
        result_message = "发现以下问题：\n" + "\n".join(issues)

    return {
        "function": "缺失注释和文档预警",
        "result": result_message
    }


# 定义全局变量用于存储 AI 批改结果
ai_review_results = {}


# 处理算法代码
@user_api_bp.route('/api/process_algorithm_code', methods=['POST'])
def process_algorithm_code():
    # 获取代码、语言和题目ID
    code = request.json.get('code')
    language = request.json.get('language', 'python')  # 默认为Python
    question_id = str(request.json.get('question_id'))

    # 记录请求信息
    current_app.logger.info(f"收到代码提交: 题目ID={question_id}, 语言={language}")
    
    # 验证必要参数
    if not code:
        return jsonify({"status": 400, "message": "代码不能为空"}), 400

    # 生成任务 ID
    task_id = str(uuid.uuid4())

    try:
        # AI生成的题目ID可能是UUID格式，不是数据库中的实际ID
        # 记录这个情况但不阻止评估
        is_ai_generated = False
        if question_id and (question_id.startswith('ai_generated') or len(question_id) > 20):
            current_app.logger.warning(f"检测到可能是AI生成的题目ID: {question_id}")
            is_ai_generated = True

        # 当不是AI生成的题目ID时才尝试从数据库获取题目信息
        question_data = None
        if not is_ai_generated and question_id:
            try:
                # 尝试从数据库获取题目信息
                result = QuestionService.get_question_by_id(question_id)
                if isinstance(result, tuple) and len(result) > 0 and isinstance(result[0], dict):
                    question_data = result[0].get('question')
                    current_app.logger.info(f"成功获取题目数据: {question_data.get('title') if question_data else 'None'}")
                else:
                    current_app.logger.warning(f"未找到题目数据，ID: {question_id}, 结果: {result}")
            except Exception as e:
                current_app.logger.error(f"获取题目数据时出错: {str(e)}")
        else:
            current_app.logger.info("跳过题目数据获取，将直接评估代码")

        # 初始化代码审查服务
        code_review_service = CodeReviewService()

        # 执行代码评估和批改
        run_result = code_review_service.review_algorithm_code(
            code=code,
            language=language,
            question_id=question_id,
            task_id=task_id
        )

        # 写入用户操作历史到数据库
        user_id = get_current_user_id()
        if user_id:
            try:
                log_function_usage(user_id, "algorithm_submit")
                upload_id = upload_file_to_db(
                    user_id,
                    f"algorithm_{question_id}_{uuid.uuid4().hex[:8]}.{language}",
                    language
                )
                if upload_id:
                    log_api_response(
                        upload_id,
                        f"algorithm_result_{task_id}.md",
                        json.dumps(run_result, ensure_ascii=False)
                    )
            except Exception as e:
                current_app.logger.error(f"写入算法提交历史失败: {e}")

        return jsonify({
            "status": 200,
            "message": "运行结果已返回，AI 批改正在处理中",
            "task_id": task_id,
            "run_result": run_result
        }), 200

    except Exception as e:
        current_app.logger.error(f"处理算法代码时出错: {str(e)}")
        return jsonify({
            "status": 500,
            "message": f"处理代码时出错: {str(e)}",
            "run_result": {
                "status": "error",
                "output": f"服务器错误: {str(e)}",
                "test_passed": False,
                "execution_time": "0s"
            }
        }), 500


@user_api_bp.route('/api/ai_review_status/<task_id>', methods=['GET'])
def get_ai_review_status(task_id):
    # 使用服务获取批改结果
    result = get_algorithm_review_result(task_id)
    current_app.logger.info(f"获取AI批改状态 - 任务ID: {task_id}, 状态: {result.get('status')}")
    return jsonify(result)


@user_api_bp.route('/api/user/favorites', methods=['GET'])
@require_auth
def get_user_favorites():
    try:
        user_id = get_current_user_id()
        
        result = FavoriteService.get_favorites_without_question(user_id)
        
        # 修改这里，确保返回数组格式
        if isinstance(result, tuple):
            favorites = result[0].get("favorites", []) 
        else:
            favorites = result.get("favorites", []) if isinstance(result, dict) else []
            
        return jsonify({
            "status": 200,
            "data": favorites  # 确保data字段直接包含数组
        })
    except Exception as e:
        current_app.logger.error(f"获取用户收藏的题目错误: {str(e)}")
        return jsonify({
            "status": 500, 
            "message": "服务器错误",
            "error": str(e)
        }), 500

@user_api_bp.route('/api/user/favorites', methods=['POST'])
@require_auth
def handle_favorite():
    try:
        user_id = get_current_user_id()

        data = request.get_json()
        question_id = data.get('questionId')
        action = data.get('action')
        title = data.get('title', question_id)
        difficulty = data.get('difficulty', '中等')
        tags = data.get('tags', [])
        question_content = data.get('content', '')

        if action == 'add':
            result = FavoriteService.add_favorite(user_id, title, question_content, difficulty, tags)
        elif action == 'remove':
            try:
                favorite_id = int(question_id)
            except (TypeError, ValueError):
                favorite_id = question_id
            result = FavoriteService.delete_favorite(favorite_id, user_id)
        else:
            return jsonify({"status": 400, "message": "无效操作"}), 400
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500


@user_api_bp.route('/api/user/history', methods=['GET'])
@require_auth
def get_user_history():
    """获取当前登录用户的历史记录（功能使用 + 上传文件 + API响应）"""
    try:
        user_id = get_current_user_id()

        records = get_user_history_combined(user_id)
        if records is None:
            records = []

        return jsonify({
            "status": 200,
            "data": records
        })
    except Exception as e:
        current_app.logger.error(f"获取用户历史记录错误: {str(e)}")
        return jsonify({"status": 500, "message": "服务器错误"}), 500
