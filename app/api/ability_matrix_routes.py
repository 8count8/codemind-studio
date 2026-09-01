"""
能力矩阵路由层

该模块定义了能力矩阵相关的所有 HTTP 端点，包括：
1. 能力矩阵页面渲染
2. 获取用户能力矩阵数据 API
3. 提交代码评估 API
4. 获取提交历史记录 API
5. 获取能力趋势数据 API
6. 获取学习推荐 API
"""

from flask import Blueprint, request, jsonify, session, current_app, send_file
from app.api.flasgger_compat import swag_from
from app.utils.auth import require_auth, get_authenticated_user_id

from . import ability_matrix_bp
from app.service.ability_matrix_service import AbilityMatrixService
from app.service.ability_report_service import AbilityReportService
from app.models import ability_matrix_model
from app.models.achievement_model import (
    get_user_achievements,
    check_and_unlock_achievements,
)
from app.utils.collaborative_filtering import collaborative_recommendations
from app.utils.knowledge_tracing import get_user_mastery, recommend_by_mastery
from app.utils.adaptive_learning import get_review_schedule
from app.utils.ml_scorer import predict_scores_with_ml, is_ml_available


@ability_matrix_bp.route('/ability-matrix', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '能力矩阵页面（页面由 Vue Router 渲染）',
    'responses': {
        200: {'description': '成功加载能力矩阵页面'},
        401: {'description': '用户未登录'}
    }
})
@require_auth
def ability_matrix_page():
    """能力矩阵页面（页面由 Vue Router 渲染）"""
    user_id = session.get('user_id')
    current_app.logger.info(f'用户 {user_id} 访问能力矩阵页面')
    return jsonify({"status": 200})


@ability_matrix_bp.route('/api/ability-matrix', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '获取当前用户的能力矩阵数据',
    'responses': {
        200: {'description': '成功获取能力矩阵'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def get_ability_matrix():
    """获取当前登录用户的能力矩阵"""
    user_id = session.get('user_id')

    try:
        AbilityMatrixService.init_user_matrix(user_id)
        result, status = AbilityMatrixService.get_user_matrix(user_id)

        if status == 200:
            return jsonify({
                "status": 200,
                "data": result
            })
        else:
            return jsonify({
                "status": status,
                "message": result.get("error", "获取能力矩阵失败")
            }), status

    except Exception as e:
        current_app.logger.error(f"获取能力矩阵失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/submit', methods=['POST'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '提交代码进行能力评估',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string', 'description': '代码内容'},
                    'question_id': {'type': 'string', 'description': '题目ID（可选）'}
                },
                'required': ['code']
            }
        }
    ],
    'responses': {
        200: {'description': '评估成功'},
        400: {'description': '参数错误'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def submit_code_evaluation():
    """提交代码进行能力评估"""
    user_id = session.get('user_id')

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": 400, "message": "请求数据不能为空"}), 400

        code = data.get('code')
        question_id = data.get('question_id')

        if not code:
            return jsonify({"status": 400, "message": "代码内容不能为空"}), 400

        result, status = AbilityMatrixService.submit_code_evaluation(user_id, code, question_id)

        if status == 200:
            return jsonify({
                "status": 200,
                "data": result,
                "message": "评估完成"
            })
        else:
            return jsonify({
                "status": status,
                "message": result.get("error", "评估失败")
            }), status

    except Exception as e:
        current_app.logger.error(f"代码评估提交失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/evaluate', methods=['POST'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '直接提交评分数据更新能力矩阵',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'source_type': {'type': 'string'},
                    'source_id': {'type': 'string'},
                    'scores': {
                        'type': 'object',
                        'properties': {
                            'syntax_score': {'type': 'number'},
                            'algorithm_score': {'type': 'number'},
                            'project_score': {'type': 'number'},
                            'debug_score': {'type': 'number'},
                            'security_score': {'type': 'number'}
                        }
                    },
                    'detail': {'type': 'object'}
                },
                'required': ['source_type', 'scores']
            }
        }
    ],
    'responses': {
        200: {'description': '更新成功'},
        400: {'description': '参数错误'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def submit_evaluation():
    """直接提交评分数据更新能力矩阵"""
    user_id = session.get('user_id')

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": 400, "message": "请求数据不能为空"}), 400

        source_type = data.get('source_type', 'code_submit')
        source_id = data.get('source_id')
        scores = data.get('scores')
        detail = data.get('detail')

        if not scores:
            return jsonify({"status": 400, "message": "评分数据不能为空"}), 400

        result, status = AbilityMatrixService.submit_evaluation(
            user_id=user_id,
            source_type=source_type,
            source_id=source_id,
            scores=scores,
            detail=detail
        )

        if status == 200:
            return jsonify({
                "status": 200,
                "data": result,
                "message": "能力矩阵已更新"
            })
        else:
            return jsonify({
                "status": status,
                "message": result.get("error", "更新失败")
            }), status

    except Exception as e:
        current_app.logger.error(f"评分提交失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/history', methods=['GET'])
@ability_matrix_bp.route('/api/ability-matrix/submissions', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '获取能力评估提交历史记录',
    'parameters': [
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'default': 30,
            'description': '返回记录数量'
        }
    ],
    'responses': {
        200: {'description': '成功获取历史记录'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def get_submission_history():
    """获取用户的提交历史记录"""
    user_id = session.get('user_id')

    try:
        limit = request.args.get('limit', 30, type=int)
        limit = min(max(1, limit), 100)

        result, status = AbilityMatrixService.get_submission_history(user_id, limit)

        if status == 200:
            return jsonify({
                "status": 200,
                "data": result
            })
        else:
            return jsonify({
                "status": status,
                "message": result.get("error", "获取历史记录失败")
            }), status

    except Exception as e:
        current_app.logger.error(f"获取提交历史失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/trend', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '获取能力趋势数据',
    'parameters': [
        {
            'name': 'dimension',
            'in': 'query',
            'type': 'string',
            'description': '能力维度（可选，不传则返回所有维度）'
        },
        {
            'name': 'days',
            'in': 'query',
            'type': 'integer',
            'default': 30,
            'description': '统计天数'
        }
    ],
    'responses': {
        200: {'description': '成功获取趋势数据'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def get_ability_trend():
    """获取用户的能力趋势数据"""
    user_id = session.get('user_id')

    try:
        dimension = request.args.get('dimension')
        days = request.args.get('days', 30, type=int)
        days = min(max(7, days), 365)

        if dimension:
            result, status = AbilityMatrixService.get_ability_trend(user_id, dimension, days)
        else:
            result, status = AbilityMatrixService.get_all_trends(user_id, days)

        if status == 200:
            return jsonify({
                "status": 200,
                "data": result
            })
        else:
            return jsonify({
                "status": status,
                "message": result.get("error", "获取趋势数据失败")
            }), status

    except Exception as e:
        current_app.logger.error(f"获取能力趋势失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/recommendations', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '获取个性化学习推荐',
    'responses': {
        200: {'description': '成功获取推荐'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def get_recommendations():
    """获取个性化学习推荐"""
    user_id = session.get('user_id')

    try:
        result, status = AbilityMatrixService.get_learning_recommendations(user_id)

        if status == 200:
            return jsonify({
                "status": 200,
                "data": result
            })
        else:
            return jsonify({
                "status": status,
                "message": result.get("error", "获取推荐失败")
            }), status

    except Exception as e:
        current_app.logger.error(f"获取学习推荐失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/export', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '导出当前用户的能力诊断 PDF 报告',
    'parameters': [{
        'name': 'format', 'in': 'query', 'type': 'string',
        'default': 'pdf', 'enum': ['pdf']
    }],
    'produces': ['application/pdf'],
    'responses': {
        200: {'description': 'PDF 报告文件'},
        400: {'description': '不支持的导出格式'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def export_ability_report():
    """Export the current user's matrix and recommendations as PDF."""
    if request.args.get('format', 'pdf').lower() != 'pdf':
        return jsonify({"status": 400, "message": "仅支持 PDF 格式"}), 400

    user_id = session.get('user_id')
    try:
        AbilityMatrixService.init_user_matrix(user_id)
        matrix_result, matrix_status = AbilityMatrixService.get_user_matrix(user_id)
        if matrix_status != 200:
            return jsonify({
                "status": matrix_status,
                "message": matrix_result.get("error", "获取能力矩阵失败")
            }), matrix_status

        recommendations_result, recommendations_status = (
            AbilityMatrixService.get_learning_recommendations(user_id)
        )
        if recommendations_status != 200:
            recommendations_result = {"recommendations": []}

        report = AbilityReportService.build_pdf(
            matrix_result,
            recommendations_result,
            username=session.get('username') or f"用户 {user_id}",
        )
        return send_file(
            report,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='codemind-ability-report.pdf',
            max_age=0,
        )
    except Exception as e:
        current_app.logger.exception(f"导出能力报告失败: {e}")
        return jsonify({"status": 500, "message": "生成能力报告失败"}), 500


# ============================================================
# 群体分位对比 API（对应文档 §6.3）
# ============================================================
@ability_matrix_bp.route('/api/ability-matrix/percentile', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '获取用户在所有用户中的能力百分位排名',
    'responses': {
        200: {'description': '成功获取百分位数据'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def get_percentile():
    """获取用户群体分位对比数据"""
    user_id = session.get('user_id')
    try:
        result, status = ability_matrix_model.get_user_percentile(user_id)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({
            "status": status,
            "message": result.get("error", "获取分位数据失败")
        }), status
    except Exception as e:
        current_app.logger.error(f"获取分位对比失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


# ============================================================
# 子维度数据 API（对应文档 §1.2.1 子维度细化）
# ============================================================
@ability_matrix_bp.route('/api/ability-matrix/subscores', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '获取用户各维度的子维度细分分数',
    'responses': {
        200: {'description': '成功获取子维度数据'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def get_subscores():
    """获取用户子维度细分分数"""
    user_id = session.get('user_id')
    try:
        result, status = ability_matrix_model.get_user_subscores(user_id)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({
            "status": status,
            "message": result.get("error", "获取子维度失败")
        }), status
    except Exception as e:
        current_app.logger.error(f"获取子维度失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


# ============================================================
# 成就/勋章系统 API（对应文档 §十一）
# ============================================================
@ability_matrix_bp.route('/api/ability-matrix/achievements', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '获取当前用户的成就勋章列表及解锁状态',
    'responses': {
        200: {'description': '成功获取成就列表'},
        401: {'description': '用户未登录'},
        500: {'description': '服务器错误'}
    }
})
@require_auth
def get_achievements():
    """获取用户成就勋章"""
    user_id = session.get('user_id')
    try:
        result, status = get_user_achievements(user_id)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({
            "status": status,
            "message": result.get("error", "获取成就失败")
        }), status
    except Exception as e:
        current_app.logger.error(f"获取成就失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


# ============================================================
# P2 增强推荐 API（对应文档 §10.3 / §10.4）
# ============================================================

@ability_matrix_bp.route('/api/ability-matrix/recommendations/content', methods=['GET'])
@require_auth
def get_content_recommendations():
    """基于内容推荐：标签相似度（§10.3.1）"""
    user_id = session.get('user_id')
    try:
        limit = request.args.get('limit', 5, type=int)
        result, status = ability_matrix_model.content_based_recommendations(user_id, limit)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({"status": status, "message": result.get("error", "推荐失败")}), status
    except Exception as e:
        current_app.logger.error(f"内容推荐失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/recommendations/collaborative', methods=['GET'])
@require_auth
def get_collaborative_recommendations():
    """基于协同过滤推荐（§10.4.1）"""
    user_id = session.get('user_id')
    try:
        limit = request.args.get('limit', 5, type=int)
        result, status = collaborative_recommendations(user_id, limit)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({"status": status, "message": result.get("error", "推荐失败")}), status
    except Exception as e:
        current_app.logger.error(f"协同过滤推荐失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/recommendations/error-weighted', methods=['GET'])
@require_auth
def get_error_weighted_recommendations():
    """基于错题标签聚类加权推荐（§10.3.2）"""
    user_id = session.get('user_id')
    try:
        limit = request.args.get('limit', 5, type=int)
        result, status = ability_matrix_model.error_weighted_recommendations(user_id, limit)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({"status": status, "message": result.get("error", "推荐失败")}), status
    except Exception as e:
        current_app.logger.error(f"错题加权推荐失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/mastery', methods=['GET'])
@require_auth
def get_mastery():
    """获取用户知识追踪数据（§10.4.2）"""
    user_id = session.get('user_id')
    try:
        tag = request.args.get('tag', None)
        result, status = get_user_mastery(user_id, tag)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({"status": status, "message": result.get("error", "获取失败")}), status
    except Exception as e:
        current_app.logger.error(f"知识追踪失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/recommendations/mastery', methods=['GET'])
@require_auth
def get_mastery_recommendations():
    """基于知识追踪的推荐（§10.4.2 最近发展区）"""
    user_id = session.get('user_id')
    try:
        limit = request.args.get('limit', 5, type=int)
        result, status = recommend_by_mastery(user_id, limit)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({"status": status, "message": result.get("error", "推荐失败")}), status
    except Exception as e:
        current_app.logger.error(f"知识追踪推荐失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/review-schedule', methods=['GET'])
@require_auth
def get_review_schedule_api():
    """获取复习计划（§10.4.3 Anki 间隔重复）"""
    user_id = session.get('user_id')
    try:
        limit = request.args.get('limit', 10, type=int)
        result, status = get_review_schedule(user_id, limit)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({"status": status, "message": result.get("error", "获取失败")}), status
    except Exception as e:
        current_app.logger.error(f"复习计划失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@ability_matrix_bp.route('/api/ability-matrix/ml-score', methods=['POST'])
@require_auth
def get_ml_score():
    """ML 模型评分（§3.2 随机森林/GBDT）"""
    user_id = session.get('user_id')
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code', '')
        if not code:
            return jsonify({"status": 400, "message": "代码不能为空"}), 400

        scores = predict_scores_with_ml(code)
        return jsonify({
            "status": 200,
            "data": {
                "scores": scores,
                "ml_available": is_ml_available(),
                "note": "ML 模型评分（未训练时降级到启发式）"
            }
        })
    except Exception as e:
        current_app.logger.error(f"ML 评分失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500
