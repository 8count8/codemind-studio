""" answer_routes.py
    答题系统路由（页面由 Vue Router 渲染，本文件提供 JSON API）

    本文件实现答题板 (AnswerpadView) 需要的两个核心端点：
      1) POST /api/answer/run     -> 仅运行一次代码（用户点"运行"按钮，通常用 sample input）
      2) POST /api/answer/submit  -> 提交判分（跑全部测试用例 + 异步 AI 批改）
"""
from __future__ import annotations

import json
import uuid
import logging
from threading import Thread

from flask import request, jsonify, current_app

from . import answer_bp
from app.service.CodeRunService import run_code_single, review_algorithm_code as run_all_testcases
from app.service.ai.CodeInsightExaminerService import CodeReviewService
from app.utils.auth import get_current_user_id, require_auth
from app.models.user_operation_records import (
    log_function_usage,
    upload_file_to_db,
    log_api_response,
)
from app.service import QuestionService
from app.service.learning_service import LearningService
from app.service.ability_matrix_service import AbilityMatrixService

log = logging.getLogger('answer_routes')


# ---------- 小工具 ----------
def _require_code(body):
    code = (body or {}).get('code')
    if not isinstance(code, str) or not code.strip():
        return None, (jsonify({"status": 400, "message": "代码不能为空"}), 400)
    return code, None


# ============================================================
# A3.1  "运行代码" 按钮  —— 只跑一次，不做 AI 批改
# ============================================================
@answer_bp.route('/api/answer/run', methods=['POST'])
@answer_bp.route('/api/answerpad/run', methods=['POST'])
def answer_run():
    """
    Request JSON:
      {
        "code": "...源代码...",
        "language": "python" | "javascript" | "java" | "c++" | "c",
        "sample_input": "可选，示例输入 stdin"
      }

    Response JSON:
      {
        "status": 200,
        "data": {
            "success": bool,
            "output": str,
            "error": str | None,
            "run_time": float,
            "sandbox_mode": "docker" | "native",
            "runtime_check": {...}
        }
      }
    """
    body = request.get_json(silent=True) or {}
    code, err_resp = _require_code(body)
    if err_resp is not None:
        return err_resp

    language = (body.get('language') or 'python').strip().lower()
    sample_input = body.get('sample_input')

    try:
        result = run_code_single(
            code=code,
            language=language,
            sample_input=sample_input,
            task_id=f"run-{uuid.uuid4().hex[:10]}",
        )
    except Exception as e:
        log.exception("answer_run 内部错误")
        return jsonify({
            "status": 500,
            "message": f"运行失败: {e}",
            "data": {"success": False, "output": None, "error": str(e), "run_time": 0}
        }), 500

    # 运行不写入历史（用户会频繁点），避免操作记录爆表
    return jsonify({
        "status": 200,
        "message": "运行完成",
        "data": result
    })


# ============================================================
# A3.2  "提交判分" 按钮  —— 跑所有测试用例 + 异步 AI 批改
# ============================================================
@answer_bp.route('/api/answer/submit', methods=['POST'])
@answer_bp.route('/api/answerpad/submit', methods=['POST'])
def answer_submit():
    """
    Request JSON:
      {
        "code": "...源代码...",
        "language": "python" | "javascript" | "java" | "c++" | "c",
        "question_id": int | str | None    # DB 题目 ID；None 时 AI 只静态判分
      }

    Response JSON (立即返回，AI 批改结果通过 /api/ai_review_status/<task_id> 轮询):
      {
        "status": 200,
        "message": "运行结果已返回，AI 批改正在处理中",
        "task_id": str,
        "run_result": {
            "total_cases": n, "passed_cases": n, "failed_cases": n,
            "results": [...], "success": bool, "note": "..."
        }
      }
    """
    body = request.get_json(silent=True) or {}
    code, err_resp = _require_code(body)
    if err_resp is not None:
        return err_resp

    language = (body.get('language') or 'python').strip().lower()
    question_id_raw = body.get('question_id')
    question_id = str(question_id_raw) if question_id_raw not in (None, '') else None
    task_id = str(uuid.uuid4())

    # ---- 1) 同步跑完整组测试用例 ----
    try:
        run_result = run_all_testcases(
            code=code,
            language=language,
            question_id=question_id,
            task_id=task_id,
        )
    except Exception as e:
        log.exception("answer_submit 执行测试用例异常")
        return jsonify({
            "status": 500,
            "message": f"处理代码时出错: {e}",
            "run_result": {
                "status": "error",
                "output": f"服务器错误: {e}",
                "success": False,
                "total_cases": 0,
                "passed_cases": 0,
                "failed_cases": 0,
                "results": [],
            }
        }), 500

    # ---- 2) 异步启动 AI 批改（与 /api/process_algorithm_code 共用一套结果存储） ----
    question_data = None
    try:
        # 过滤 AI 生成 UUID，避免 DB 查询报错
        is_ai_gen = (
            bool(question_id) and
            (str(question_id).startswith('ai_generated') or len(str(question_id)) > 20)
        )
        if (not is_ai_gen) and question_id:
            q = QuestionService.get_question_by_id(question_id)
            if isinstance(q, tuple) and q and isinstance(q[0], dict):
                question_data = q[0].get('question')
    except Exception as e:
        current_app.logger.warning(f"answer_submit 获取题目失败 task={task_id}: {e}")

    try:
        svc = CodeReviewService()
        app_ref = (
            current_app._get_current_object()
            if current_app else None
        )
        # 这里只跑 AI 批改（不再重复跑测试用例），直接把 run_result 喂给 prompt
        Thread(
            target=svc._process_ai_review,
            args=(code, language, question_data, task_id, run_result, app_ref),
            daemon=True,
        ).start()
    except Exception as e:
        current_app.logger.error(f"启动 AI 批改线程失败 task={task_id}: {e}")

    # ---- 3) 写入用户操作历史到数据库 ----
    user_id = get_current_user_id()
    submission = None
    ability_scores = None
    if user_id:
        try:
            submission = LearningService.save_submission(
                user_id, question_id, language, code, run_result, task_id
            )
            ability_scores, detail = AbilityMatrixService.evaluate_code_with_ai(code, question_id)
            total_cases = int(run_result.get("total_cases") or 0)
            passed_cases = int(run_result.get("passed_cases") or 0)
            if total_cases:
                pass_score = round(passed_cases / total_cases * 100)
                ability_scores["algorithm_score"] = round(
                    ability_scores["algorithm_score"] * 0.35 + pass_score * 0.65
                )
                ability_scores["debug_score"] = round(
                    ability_scores["debug_score"] * 0.5 + pass_score * 0.5
                )
            detail.update({
                "task_id": task_id,
                "language": language,
                "total_cases": total_cases,
                "passed_cases": passed_cases,
            })
            AbilityMatrixService.submit_evaluation(
                user_id=user_id,
                source_type="quiz_answer",
                source_id=question_id,
                scores=ability_scores,
                detail=detail,
            )
            log_function_usage(user_id, "algorithm_submit")
            upload_id = upload_file_to_db(
                user_id,
                f"algorithm_{question_id or 'NA'}_{uuid.uuid4().hex[:8]}.{language}",
                language,
                code,
            )
            if upload_id:
                log_api_response(
                    upload_id,
                    f"algorithm_result_{task_id}.md",
                    json.dumps(run_result, ensure_ascii=False),
                )
        except Exception as e:
            current_app.logger.error(f"写入算法提交历史失败: {e}")

    return jsonify({
        "status": 200,
        "message": "运行结果已返回，AI 批改正在处理中",
        "task_id": task_id,
        "run_result": run_result,
        "submission": submission,
        "ability_scores": ability_scores,
    }), 200


@answer_bp.route('/answerpad', methods=['GET', 'POST'])
def answerpad():
    """答题板页面占位（实际页面由 Vue Router 渲染）"""
    return jsonify({"status": 200})


@answer_bp.route('/api/answerpad/auto-save', methods=['POST'])
@require_auth
def answerpad_auto_save():
    body = request.get_json(silent=True) or {}
    try:
        LearningService.save_draft(
            get_current_user_id(), body.get('question_id'),
            (body.get('language') or 'python').strip().lower(),
            body.get('code') if isinstance(body.get('code'), str) else '',
        )
        return jsonify({"status": 200, "message": "草稿已保存"})
    except ValueError as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    except Exception as e:
        current_app.logger.exception(f"保存草稿失败: {e}")
        return jsonify({"status": 500, "message": "保存草稿失败"}), 500


@answer_bp.route('/api/answerpad/restore', methods=['GET'])
@require_auth
def answerpad_restore():
    question_id = request.args.get('question_id')
    if not question_id:
        return jsonify({"status": 400, "message": "缺少题目 ID"}), 400
    try:
        return jsonify({"status": 200, "data": LearningService.draft(get_current_user_id(), question_id)})
    except Exception as e:
        current_app.logger.exception(f"恢复草稿失败: {e}")
        return jsonify({"status": 500, "message": "恢复草稿失败"}), 500


@answer_bp.route('/api/answerpad/submissions', methods=['GET'])
@require_auth
def answerpad_submissions():
    try:
        data = LearningService.history(get_current_user_id(), {
            'question_id': request.args.get('question_id'),
            'page': request.args.get('page', 1, type=int),
            'per_page': request.args.get('per_page', 20, type=int),
        })
        return jsonify({"status": 200, "data": data})
    except Exception as e:
        current_app.logger.exception(f"加载题目提交历史失败: {e}")
        return jsonify({"status": 500, "message": "加载提交历史失败"}), 500
