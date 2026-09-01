import uuid
from threading import Thread
import re
import json

from app.api import user_api_bp

from flask import jsonify, request, current_app
from app.utils.auth import require_auth, get_current_user_id
from app.service import QuestionService
from app.service import FavoriteService
from app.service.learning_service import LearningService
from app.service.ai import CodeCheckerService, check_code, CodeReviewService, get_algorithm_review_result
from app.models.user_operation_records import (
    log_function_usage,
    upload_file_to_db,
    log_api_response,
    get_user_history_combined,
)


def _build_quality_report(code, legacy_result):
    """Create a stable three-dimension report even when the local model is unavailable."""
    lines = code.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    long_lines = [index + 1 for index, line in enumerate(lines) if len(line) > 100]
    tab_lines = [index + 1 for index, line in enumerate(lines) if '\t' in line]
    comment_count = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*')))
    nested_loop = bool(re.search(r'(for|while)[^\n]*:\s*\n\s+(for|while)\b', code))
    security_patterns = {
        '动态执行 eval/exec': r'\b(eval|exec)\s*\(',
        'Shell 命令执行': r'\b(os\.system|subprocess\.(run|Popen|call))\s*\(',
        '可能的硬编码密钥': r'(?i)(password|secret|api[_-]?key)\s*=\s*["\'][^"\']+["\']',
        'SQL 字符串拼接': r'(?i)(select|insert|update|delete).*(\+|f["\'])',
    }
    security_hits = [label for label, pattern in security_patterns.items() if re.search(pattern, code)]
    style_score = max(35, 100 - len(long_lines) * 4 - len(tab_lines) * 3 - (8 if len(lines) > 12 and not comment_count else 0))
    performance_score = max(45, 88 - (12 if nested_loop else 0) - min(15, code.count('.sort(') * 3))
    security_score = max(20, 100 - len(security_hits) * 18)
    annotations = []
    annotations.extend({'line': line, 'type': '规范', 'message': '单行超过 100 个字符，建议拆分。'} for line in long_lines[:8])
    annotations.extend({'line': line, 'type': '规范', 'message': '建议使用空格代替 Tab 缩进。'} for line in tab_lines[:8])
    annotations.extend({'line': None, 'type': '安全', 'message': message} for message in security_hits)
    if nested_loop:
        annotations.append({'line': None, 'type': '性能', 'message': '检测到嵌套循环，请复核时间复杂度。'})
    if not annotations:
        annotations.append({'line': None, 'type': '总结', 'message': '未发现明显的规范、性能或安全高风险项。'})
    optimized = '\n'.join(line.rstrip().replace('\t', '    ') for line in lines).rstrip() + '\n'
    scores = {'style': style_score, 'performance': performance_score, 'security': security_score}
    return {
        'scores': scores,
        'total_score': round(sum(scores.values()) / 3),
        'summary': f"共分析 {len(lines)} 行代码，发现 {len(annotations)} 项可关注内容。",
        'annotations': annotations,
        'original_code': code,
        'optimized_code': optimized,
        'ai_analysis': legacy_result,
    }


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


@user_api_bp.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """返回答题板需要的单题详情。"""
    result = QuestionService.get_question_by_id(question_id)
    if not isinstance(result, dict):
        return jsonify({"status": 500, "message": "题目数据格式错误"}), 500
    if "error" in result:
        status = 404 if result["error"] == "Question not found" else 500
        return jsonify({"status": status, "message": result["error"]}), status
    question = result.get("question")
    if not question:
        return jsonify({"status": 404, "message": "题目不存在"}), 404
    return jsonify({"status": 200, "data": question})


@user_api_bp.route('/process_code', methods=['POST'])
@user_api_bp.route('/api/code-review/review', methods=['POST'])
def process_code():
    """
    处理代码审查请求，返回 JSON 格式的响应。
    """
    # try:
    # 获取审查类型
    json_body = request.get_json(silent=True) if request.is_json else {}
    json_body = json_body if isinstance(json_body, dict) else {}
    review_type = (
        request.form.get('review_type') or request.form.get('tab_type')
        or json_body.get('review_type') or 'code-commenting'
    )

    # 通用字段
    code_file = request.files.get('code-file')
    pasted_code = request.form.get('paste_code', None) or json_body.get('code')
    doc_file = request.files.get('doc-file', None)
    standard = (
        request.form.get('code-standard') or request.form.get('code_standard')
        or json_body.get('standard') or 'google'
    )

    # 提交代码
    submit_code = None
    if code_file:
        if code_file.content_length and code_file.content_length > 200_000:
            return jsonify({"status": 413, "message": "代码文件不能超过 200KB"}), 413
        submit_code = code_file.read().decode('utf-8', errors='replace')
    elif pasted_code:
        submit_code = pasted_code
    else:
        return jsonify({
            "status": 400,
            "message": "缺少代码文件或粘贴的代码"
        }), 400
    raw_code = submit_code
    if standard:
        submit_code = f"使用标准：{standard}\ncode:{submit_code}"
    # 根据不同类型处理附加字段
    result = {"function": "未知类型", "result": "未处理"}

    if review_type in CodeCheckerService.function_mapping:
        doc_content = None
        if doc_file:
            doc_content = doc_file.read().decode('utf-8', errors='replace')
        try:
            result = check_code(CodeCheckerService.function_mapping[review_type], submit_code, doc_content)
        except Exception as e:
            current_app.logger.warning(f"本地 AI 审查不可用，使用静态分析兜底: {e}")
            result = {
                "function": CodeCheckerService.function_mapping[review_type],
                "result": "本地 AI 暂不可用；已完成确定性静态质量分析。",
            }
    quality_report = _build_quality_report(raw_code, result)

    # 写入用户操作历史到数据库
    user_id = get_current_user_id()
    if user_id:
        try:
            log_function_usage(user_id, f"code_review_{review_type}")
            upload_id = upload_file_to_db(
                user_id,
                f"code_review_{review_type}_{uuid.uuid4().hex[:8]}.py",
                "python",
                raw_code,
            )
            if upload_id:
                log_api_response(
                    upload_id,
                    f"review_result_{review_type}.md",
                    json.dumps({"legacy": result, "review": quality_report}, ensure_ascii=False)
                )
        except Exception as e:
            current_app.logger.error(f"写入历史记录失败: {e}")

    review_id = f"rev_{uuid.uuid4().hex[:12]}"
    documented_payload = {
        "review_id": review_id,
        "overall_score": quality_report["total_score"],
        "dimension_scores": quality_report["scores"],
        "original_code": quality_report["original_code"],
        "optimized_code": quality_report["optimized_code"],
        "line_comments": quality_report["annotations"],
        "summary": quality_report["summary"],
    }
    return jsonify({
        "status": 200,
        "message": "处理成功",
        "results": [result],
        "review": quality_report,
        "data": documented_payload,
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
                    language,
                    code,
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
        title = question_id
        difficulty = data.get('difficulty', '中等')
        tags = data.get('tags', [])
        question_content = data.get('content', '')

        if action == 'add':
            result = FavoriteService.add_favorite(user_id, title, question_content, difficulty, tags)
        elif action == 'remove':
            result = FavoriteService.delete_favorite(user_id, question_id)
        else:
            return jsonify({"status": 400, "message": "无效操作"}), 400
            
        if isinstance(result, tuple):
            payload, status_code = result
        else:
            payload, status_code = result, 200
        if isinstance(payload, dict) and "error" in payload:
            return jsonify({"status": status_code, "message": payload["error"]}), status_code
        return jsonify({"status": status_code, "message": payload.get("message", "操作成功")}), status_code
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


@user_api_bp.route('/api/code-review/history', methods=['GET'])
@require_auth
def get_code_review_history():
    records = get_user_history_combined(get_current_user_id()) or []
    reviews = [item for item in records if item.get('record_type') == 'api_response']
    return jsonify({"status": 200, "data": reviews})


@user_api_bp.route('/api/code-review/<int:review_id>', methods=['GET'])
@require_auth
def get_code_review_detail(review_id):
    records = get_user_history_combined(get_current_user_id()) or []
    item = next((row for row in records if row.get('record_type') == 'api_response' and row.get('id') == review_id), None)
    if not item:
        return jsonify({"status": 404, "message": "审查记录不存在"}), 404
    return jsonify({"status": 200, "data": item})


@user_api_bp.route('/api/dashboard/summary', methods=['GET'])
@user_api_bp.route('/api/dashboard/stats', methods=['GET'])
@user_api_bp.route('/api/user/stats', methods=['GET'])
@require_auth
def get_dashboard_summary():
    """Dashboard statistics, ability preview and continue-practice target."""
    try:
        return jsonify({"status": 200, "data": LearningService.dashboard(get_current_user_id())})
    except Exception as e:
        current_app.logger.exception(f"加载 Dashboard 概览失败: {e}")
        return jsonify({"status": 500, "message": "加载学习概览失败"}), 500


@user_api_bp.route('/api/history/submissions', methods=['GET'])
@user_api_bp.route('/api/history/list', methods=['GET'])
@user_api_bp.route('/api/user/code-history', methods=['GET'])
@require_auth
def get_submission_history():
    filters = {
        "result": request.args.get("result", ""),
        "difficulty": request.args.get("difficulty", ""),
        "keyword": request.args.get("keyword", "").strip()[:100],
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "page": request.args.get("page", 1, type=int),
        "per_page": request.args.get("per_page", 20, type=int),
    }
    try:
        data = LearningService.history(get_current_user_id(), filters)
        return jsonify({"status": 200, "data": data})
    except Exception as e:
        current_app.logger.exception(f"加载提交历史失败: {e}")
        return jsonify({"status": 500, "message": "加载提交历史失败"}), 500


@user_api_bp.route('/api/history/submissions/<int:submission_id>', methods=['GET'])
@user_api_bp.route('/api/user/code-history/<int:submission_id>', methods=['GET'])
@require_auth
def get_submission_detail(submission_id):
    try:
        item = LearningService.submission(get_current_user_id(), submission_id)
        if not item:
            return jsonify({"status": 404, "message": "提交记录不存在"}), 404
        return jsonify({"status": 200, "data": item})
    except Exception as e:
        current_app.logger.exception(f"加载提交详情失败: {e}")
        return jsonify({"status": 500, "message": "加载提交详情失败"}), 500


@user_api_bp.route('/api/history/compare', methods=['GET'])
@require_auth
def compare_submissions():
    left_id = request.args.get("left", type=int)
    right_id = request.args.get("right", type=int)
    if not left_id or not right_id or left_id == right_id:
        return jsonify({"status": 400, "message": "请选择两条不同的提交记录"}), 400
    left = LearningService.submission(get_current_user_id(), left_id)
    right = LearningService.submission(get_current_user_id(), right_id)
    if not left or not right:
        return jsonify({"status": 404, "message": "提交记录不存在"}), 404
    return jsonify({"status": 200, "data": {"left": left, "right": right}})


@user_api_bp.route('/api/favorites/topics', methods=['GET', 'POST'])
@require_auth
def favorite_topics_api():
    user_id = get_current_user_id()
    try:
        if request.method == 'POST':
            topic_id = LearningService.create_topic(user_id, request.get_json(silent=True) or {})
            return jsonify({"status": 201, "message": "题单已创建", "data": {"id": topic_id}}), 201
        return jsonify({"status": 200, "data": LearningService.topics(user_id)})
    except ValueError as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    except Exception as e:
        current_app.logger.exception(f"题单操作失败: {e}")
        return jsonify({"status": 409, "message": "题单名称已存在或操作失败"}), 409


@user_api_bp.route('/api/favorites/topics/<int:topic_id>', methods=['PUT', 'DELETE'])
@require_auth
def favorite_topic_detail_api(topic_id):
    user_id = get_current_user_id()
    try:
        if request.method == 'DELETE':
            ok = LearningService.delete_topic(user_id, topic_id)
        else:
            ok = LearningService.update_topic(user_id, topic_id, request.get_json(silent=True) or {})
        if not ok:
            return jsonify({"status": 404, "message": "题单不存在"}), 404
        return jsonify({"status": 200, "message": "操作成功"})
    except ValueError as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    except Exception as e:
        current_app.logger.exception(f"更新题单失败: {e}")
        return jsonify({"status": 409, "message": "题单名称已存在或操作失败"}), 409


@user_api_bp.route('/api/favorites/assign', methods=['POST'])
@require_auth
def assign_favorite_topic():
    body = request.get_json(silent=True) or {}
    question_id = body.get("question_id")
    topic_id = body.get("topic_id")
    if question_id in (None, ""):
        return jsonify({"status": 400, "message": "缺少题目 ID"}), 400
    if topic_id not in (None, ""):
        try:
            topic_id = int(topic_id)
        except (TypeError, ValueError):
            return jsonify({"status": 400, "message": "题单 ID 无效"}), 400
    else:
        topic_id = None
    try:
        ok = LearningService.assign_topic(get_current_user_id(), question_id, topic_id)
        if not ok:
            return jsonify({"status": 404, "message": "收藏或题单不存在"}), 404
        return jsonify({"status": 200, "message": "题单已更新"})
    except Exception as e:
        current_app.logger.exception(f"移动收藏失败: {e}")
        return jsonify({"status": 500, "message": "移动收藏失败"}), 500


@user_api_bp.route('/api/favorites/topics/<int:topic_id>/items', methods=['GET'])
@require_auth
def favorite_topic_items(topic_id):
    result = FavoriteService.get_favorites_without_question(get_current_user_id())
    payload = result[0] if isinstance(result, tuple) else result
    items = [item for item in payload.get('favorites', []) if int(item.get('topic_id') or 0) == topic_id]
    return jsonify({"status": 200, "data": items})


@user_api_bp.route('/api/favorites/add', methods=['POST'])
@user_api_bp.route('/api/favorites/remove', methods=['POST'])
@require_auth
def favorite_compatibility_api():
    body = request.get_json(silent=True) or {}
    question_id = body.get('question_id') or body.get('questionId')
    if question_id in (None, ''):
        return jsonify({"status": 400, "message": "缺少题目 ID"}), 400
    if request.path.endswith('/remove'):
        result = FavoriteService.delete_favorite(get_current_user_id(), question_id)
    else:
        result = FavoriteService.add_favorite(get_current_user_id(), question_id, '', '中等', [])
    payload, status = result if isinstance(result, tuple) else (result, 200)
    if status >= 400:
        return jsonify({"status": status, "message": payload.get('error', '操作失败')}), status
    topic_id = body.get('topic_id')
    if request.path.endswith('/add') and topic_id not in (None, ''):
        LearningService.assign_topic(get_current_user_id(), question_id, int(topic_id))
    return jsonify({"status": 200, "message": payload.get('message', '操作成功')})


@user_api_bp.route('/api/user/operation-logs', methods=['GET'])
@require_auth
def get_operation_logs():
    records = get_user_history_combined(get_current_user_id()) or []
    page = max(1, request.args.get('page', 1, type=int))
    per_page = min(100, max(1, request.args.get('per_page', 20, type=int)))
    start = (page - 1) * per_page
    return jsonify({"status": 200, "data": {
        "items": records[start:start + per_page], "total": len(records),
        "page": page, "per_page": per_page,
    }})
