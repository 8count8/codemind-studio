"""试题库页面与 REST API。"""
import json

from flask import jsonify, request
from . import quizbank_bp
from app.service import QuestionService, FavoriteService
from app.service.CodeService import get_test_cases
from app.utils.auth import require_auth, get_current_user_id


@quizbank_bp.route('/quizbank', methods=['GET', 'POST'])
def quizbank():
    """试题库页面（页面由 Vue Router 渲染）"""
    return jsonify({"status": 200})


def _parse_tags(value):
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
        if isinstance(parsed, list):
            return parsed
    except (TypeError, ValueError):
        pass
    return [item.strip() for item in str(value or "").split(',') if item.strip()]


@quizbank_bp.route('/api/quizbank/list', methods=['GET'])
@quizbank_bp.route('/api/quizbank/search', methods=['GET'])
@require_auth
def quizbank_list_api():
    result = QuestionService.get_all_questions()
    if not isinstance(result, dict) or 'error' in result:
        return jsonify({"status": 500, "message": result.get('error', '加载题库失败')}), 500
    questions = result.get('questions', [])
    difficulty = request.args.get('difficulty', '').strip()
    requested_tags = {tag.strip() for tag in request.args.get('tags', '').split(',') if tag.strip()}
    keyword = request.args.get('keyword', '').strip().lower()
    filtered = []
    for question in questions:
        tags = _parse_tags(question.get('tags'))
        if difficulty and question.get('difficulty') != difficulty:
            continue
        if requested_tags and not requested_tags.intersection(tags):
            continue
        if keyword and keyword not in str(question.get('title') or '').lower():
            continue
        filtered.append({**question, 'tags': tags})
    page = max(1, request.args.get('page', 1, type=int))
    per_page = min(50, max(1, request.args.get('per_page', 20, type=int)))
    start = (page - 1) * per_page
    return jsonify({
        "status": 200,
        "data": {"total": len(filtered), "page": page, "per_page": per_page, "questions": filtered[start:start + per_page]},
    })


@quizbank_bp.route('/api/quizbank/<int:question_id>', methods=['GET'])
@require_auth
def quizbank_detail_api(question_id):
    result = QuestionService.get_question_by_id(question_id)
    question = result.get('question') if isinstance(result, dict) else None
    if not question:
        return jsonify({"status": 404, "message": "题目不存在"}), 404
    question['tags'] = _parse_tags(question.get('tags'))
    cases = get_test_cases(question_id)
    question['samples'] = cases[:1]
    try:
        favorites = FavoriteService.get_favorites_without_question(get_current_user_id())
        payload = favorites[0] if isinstance(favorites, tuple) else favorites
        favorite_ids = {str(item.get('id')) for item in payload.get('favorites', [])}
        question['is_favorited'] = str(question_id) in favorite_ids
    except Exception:
        question['is_favorited'] = False
    return jsonify({"status": 200, "data": question})
