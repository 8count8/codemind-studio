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

from flask import Blueprint, request, jsonify, render_template, session, current_app
from flasgger import swag_from

from . import ability_matrix_bp
from app.service.ability_matrix_service import AbilityMatrixService


@ability_matrix_bp.route('/ability-matrix', methods=['GET'])
@swag_from({
    'tags': ['能力矩阵'],
    'description': '能力矩阵页面',
    'responses': {
        200: {'description': '成功加载能力矩阵页面'},
        401: {'description': '用户未登录'}
    }
})
def ability_matrix_page():
    """加载能力矩阵页面"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": 401, "message": "请先登录"}), 401

    current_app.logger.info(f'用户 {user_id} 访问能力矩阵页面')
    return render_template('ability_matrix.html', user_id=user_id)


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
def get_ability_matrix():
    """获取当前登录用户的能力矩阵"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": 401, "message": "请先登录"}), 401

    try:
        # 确保用户矩阵已初始化
        AbilityMatrixService.init_user_matrix(user_id)

        # 获取完整的能力矩阵数据（含薄弱维度分析）
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
def submit_code_evaluation():
    """提交代码进行能力评估"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": 401, "message": "请先登录"}), 401

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
def submit_evaluation():
    """直接提交评分数据更新能力矩阵"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": 401, "message": "请先登录"}), 401

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
def get_submission_history():
    """获取用户的提交历史记录"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": 401, "message": "请先登录"}), 401

    try:
        limit = request.args.get('limit', 30, type=int)
        limit = min(max(1, limit), 100)  # 限制在1-100之间

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
def get_ability_trend():
    """获取用户的能力趋势数据"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": 401, "message": "请先登录"}), 401

    try:
        dimension = request.args.get('dimension')
        days = request.args.get('days', 30, type=int)
        days = min(max(7, days), 365)  # 限制在7-365天

        if dimension:
            # 获取单个维度的趋势
            result, status = AbilityMatrixService.get_ability_trend(user_id, dimension, days)
        else:
            # 获取所有维度的趋势
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
def get_recommendations():
    """获取个性化学习推荐"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": 401, "message": "请先登录"}), 401

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
