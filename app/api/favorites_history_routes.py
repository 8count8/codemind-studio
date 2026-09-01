""" favorites_history_routes.py
    收藏夹、历史记录、错题诊断页面路由（页面由 Vue Router 渲染）
    错题诊断 API 实现 P0-5：错题诊断引擎（对应文档 §1 项目需求文档）
"""
from flask import jsonify, session, current_app
from . import favorites_history_bp
from app.utils.auth import require_auth
from app.models.error_diagnosis_model import (
    diagnose_error_patterns,
    recommend_similar_questions,
)


@favorites_history_bp.route('/favorites', methods=['GET', 'POST'])
def favorites():
    return jsonify({"status": 200})


@favorites_history_bp.route('/history', methods=['GET', 'POST'])
def history():
    return jsonify({"status": 200})


# ============================================================
# 错题诊断引擎 API（对应文档 1.项目需求文档.md §2.1 错题诊断引擎）
# ============================================================
@favorites_history_bp.route('/api/error-diagnosis/patterns', methods=['GET'])
@require_auth
def get_error_patterns():
    """获取用户错误模式分析（错题标签聚类 + 错误类型分布）"""
    user_id = session.get('user_id')
    try:
        result, status = diagnose_error_patterns(user_id, limit=50)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({"status": status, "message": result.get("error", "分析失败")}), status
    except Exception as e:
        current_app.logger.error(f"获取错误模式分析失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500


@favorites_history_bp.route('/api/error-diagnosis/recommendations', methods=['GET'])
@require_auth
def get_error_recommendations():
    """基于错题标签聚类推荐相似强化题目"""
    user_id = session.get('user_id')
    try:
        result, status = recommend_similar_questions(user_id, limit=5)
        if status == 200:
            return jsonify({"status": 200, "data": result})
        return jsonify({"status": status, "message": result.get("error", "推荐失败")}), status
    except Exception as e:
        current_app.logger.error(f"获取错题推荐失败: {e}")
        return jsonify({"status": 500, "message": "服务器内部错误"}), 500
