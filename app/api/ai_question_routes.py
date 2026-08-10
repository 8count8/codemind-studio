from flask import Blueprint, request, jsonify, render_template, current_app
from app.api.flasgger_compat import swag_from
from app.service.algorithm_service import generate_and_save_algorithm_problem
from . import ai_question_bp


@ai_question_bp.route('/ai-question', methods=['GET'])
@swag_from({
    'tags': ['AI出题'],
    'description': 'AI出题页面',
    'responses': {
        200: {'description': '成功加载AI出题页面'}
    }
})
def ai_question():
    """加载AI出题页面"""
    return render_template('ai_question.html')


@ai_question_bp.route('/api/generate-question', methods=['POST'])
@swag_from({
    'tags': ['AI出题'],
    'description': '生成算法题目',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'algorithm_type': {'type': 'string'},
                    'difficulty_level': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': '成功生成题目'},
        400: {'description': '参数错误'},
        500: {'description': '生成题目失败'}
    }
})
def generate_question():
    """生成算法题目"""
    try:
        data = request.json
        algorithm_type = data.get('algorithm_type')
        difficulty_level = data.get('difficulty_level')

        if not algorithm_type or not difficulty_level:
            return jsonify({'error': '缺少必要参数'}), 400

        # 调用算法服务生成题目
        result = generate_and_save_algorithm_problem(algorithm_type, difficulty_level)
        
        # 如果遇到错误
        if 'error' in result:
            error_msg = result['error']
            # 处理常见的JSON解析错误，提供更友好的错误信息
            if "Invalid control character" in error_msg:
                return jsonify({'error': '生成题目时遇到格式错误，请重试'}), 500
            elif "API调用失败" in error_msg:
                return jsonify({'error': '与AI服务通信失败，请稍后重试'}), 500
            else:
                return jsonify({'error': error_msg}), 500

        # 处理标签，确保格式正确
        problem = result['problem']
        tags = problem.get('tags', [])
        if not tags:
            tags = [algorithm_type]
        # 确保标签是字符串形式以便前端显示
        if isinstance(tags, list):
            tags_str = ', '.join(tags)
        else:
            tags_str = str(tags)

        # 转换格式以符合answerpad页面所需数据格式
        question_data = {
            'id': problem.get('id', 'ai_generated'),
            'title': problem.get('title', f"{algorithm_type}题目"),
            'content': problem.get('description', ''),
            'difficulty': problem.get('difficulty_level', difficulty_level),
            'tags': tags_str,
            'created_at': problem.get('created_at', '')
        }
        
        return jsonify({'question': question_data}), 200
        
    except Exception as e:
        # 捕获所有未预期的异常
        current_app.logger.error(f"生成题目时发生未预期错误: {str(e)}")
        return jsonify({'error': '服务器内部错误，请稍后重试'}), 500


