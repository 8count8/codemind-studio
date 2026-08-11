"""
能力矩阵业务逻辑层

该模块封装了能力矩阵相关的业务逻辑，包括：
1. 能力矩阵的获取与初始化
2. 评分计算与矩阵更新
3. 提交记录管理
4. 能力趋势分析
5. 薄弱维度诊断与学习建议
6. AI评分接口调用（模拟）
"""

import logging
import random
from datetime import datetime
from app.models import ability_matrix_model
from app.utils.ability_matrix_calculator import get_recommended_tasks


class AbilityMatrixService:
    """能力矩阵服务类，封装所有业务逻辑"""

    # 能力维度定义
    DIMENSIONS = ability_matrix_model.ABILITY_DIMENSIONS
    DIMENSION_LABELS = ability_matrix_model.DIMENSION_LABELS

    @staticmethod
    def get_user_matrix(user_id):
        """
        获取用户的完整能力矩阵数据。
        :param user_id: 用户ID
        :return: 包含矩阵数据、薄弱维度和建议的综合结果
        """
        try:
            # 获取能力矩阵
            matrix_result, matrix_status = ability_matrix_model.get_ability_matrix(user_id)
            if matrix_status != 200:
                return matrix_result, matrix_status

            # 获取薄弱维度分析
            weak_result, weak_status = ability_matrix_model.get_weak_dimensions(user_id)

            # 组合返回结果
            result = matrix_result
            if weak_status == 200:
                result['weak_dimensions'] = weak_result.get('weak_dimensions', [])
                result['average_score'] = weak_result.get('average_score', 0)
            else:
                result['weak_dimensions'] = []
                result['average_score'] = 0

            return result, 200

        except Exception as e:
            logging.error(f"获取用户能力矩阵失败: {e}")
            return {"error": f"服务器错误: {str(e)}"}, 500

    @staticmethod
    def init_user_matrix(user_id):
        """
        初始化用户的能力矩阵（首次使用时调用）。
        :param user_id: 用户ID
        :return: 操作结果
        """
        try:
            return ability_matrix_model.init_ability_matrix(user_id)
        except Exception as e:
            logging.error(f"初始化用户能力矩阵失败: {e}")
            return {"error": f"服务器错误: {str(e)}"}, 500

    @staticmethod
    def submit_evaluation(user_id, source_type, source_id=None, scores=None, detail=None):
        """
        提交一次能力评估，同时更新能力矩阵和保存提交记录。
        :param user_id: 用户ID
        :param source_type: 数据来源（code_submit/ai_review/quiz_answer）
        :param source_id: 来源ID
        :param scores: 评分字典 {syntax_score: x, algorithm_score: x, ...}
        :param detail: 评分详情（可选）
        :return: 更新后的能力矩阵数据
        """
        try:
            # 验证评分数据
            if scores is None:
                return {"error": "评分数据不能为空"}, 400

            # 验证各维度分数范围
            for dim in AbilityMatrixService.DIMENSIONS:
                score = scores.get(dim, 0)
                if not (0 <= score <= 100):
                    return {"error": f"{dim} 的得分必须在 0-100 之间"}, 400

            # 保存提交记录
            submit_result, submit_status = ability_matrix_model.save_submission(
                user_id=user_id,
                source_type=source_type,
                source_id=source_id,
                scores=scores,
                detail=detail
            )
            if submit_status != 200:
                return submit_result, submit_status

            # 更新能力矩阵
            matrix_result, matrix_status = ability_matrix_model.update_ability_matrix(user_id, scores)
            if matrix_status != 200:
                return matrix_result, matrix_status

            # 返回更新后的矩阵
            return matrix_result, 200

        except Exception as e:
            logging.error(f"提交能力评估失败: {e}")
            return {"error": f"服务器错误: {str(e)}"}, 500

    @staticmethod
    def submit_code_evaluation(user_id, code, question_id=None):
        """
        提交代码进行能力评估（模拟AI评分）。
        在实际生产环境中，这里应该调用真实的AI模型进行评分。
        :param user_id: 用户ID
        :param code: 提交的代码内容
        :param question_id: 题目ID（可选）
        :return: 评分结果和更新后的能力矩阵
        """
        try:
            if not code or len(code.strip()) < 5:
                return {"error": "代码内容过短，无法评估"}, 400

            # 调用AI评分（当前为模拟实现）
            scores, detail = AbilityMatrixService.evaluate_code_with_ai(code, question_id)

            # 提交评估结果
            result, status = AbilityMatrixService.submit_evaluation(
                user_id=user_id,
                source_type='code_submit',
                source_id=question_id,
                scores=scores,
                detail=detail
            )

            if status != 200:
                return result, status

            # 返回评估详情
            return {
                "scores": scores,
                "detail": detail,
                "matrix": result.get('matrix'),
                "message": "代码评估完成，能力矩阵已更新"
            }, 200

        except Exception as e:
            logging.error(f"代码评估失败: {e}")
            return {"error": f"评估失败: {str(e)}"}, 500

    @staticmethod
    def evaluate_code_with_ai(code, question_id=None):
        """
        使用AI对代码进行能力评分（模拟实现）。
        实际项目中应替换为真实的AI API调用。
        :param code: 代码内容
        :param question_id: 题目ID
        :return: (评分字典, 评分详情字典)
        """
        # 基于代码特征的简单启发式评分（模拟）
        code_lines = code.strip().split('\n')
        line_count = len(code_lines)

        # 语法基础：根据代码行数和基本语法特征评分
        syntax_base = min(60 + line_count * 2, 95)
        has_comments = sum(1 for line in code_lines if '#' in line or '//' in line or '"""' in line)
        syntax_score = min(syntax_base + has_comments * 3, 100)

        # 算法思维：根据是否有循环、递归、条件判断等评分
        loop_count = code.count('for ') + code.count('while ')
        condition_count = code.count('if ') + code.count('elif ')
        algorithm_score = min(40 + loop_count * 10 + condition_count * 5, 100)

        # 项目实践：根据是否有函数定义、类定义、模块化设计评分
        func_count = code.count('def ') + code.count('function ')
        class_count = code.count('class ')
        project_score = min(35 + func_count * 15 + class_count * 20, 100)

        # 调试能力：根据是否有异常处理、日志记录评分
        try_count = code.count('try') + code.count('except') + code.count('raise')
        log_count = code.count('print') + code.count('logging')
        debug_score = min(40 + try_count * 12 + log_count * 5, 100)

        # 安全意识：根据是否有输入验证、SQL参数化等评分
        security_keywords = ['sanitize', 'validate', 'escape', 'hash', 'encrypt', '%s', 'parameter']
        security_hits = sum(1 for kw in security_keywords if kw.lower() in code.lower())
        security_score = min(30 + security_hits * 15, 100)

        # 添加随机波动（模拟AI的不确定性）
        import random
        scores = {
            'syntax_score': max(0, min(100, syntax_score + random.randint(-5, 5))),
            'algorithm_score': max(0, min(100, algorithm_score + random.randint(-5, 5))),
            'project_score': max(0, min(100, project_score + random.randint(-5, 5))),
            'debug_score': max(0, min(100, debug_score + random.randint(-5, 5))),
            'security_score': max(0, min(100, security_score + random.randint(-5, 5)))
        }

        # 生成评分详情
        detail = {
            'code_lines': line_count,
            'has_comments': has_comments > 0,
            'loop_count': loop_count,
            'condition_count': condition_count,
            'function_count': func_count,
            'class_count': class_count,
            'exception_handling': try_count > 0,
            'security_practices': security_hits,
            'evaluated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note': '此为模拟评分，生产环境请接入真实AI模型'
        }

        return scores, detail

    @staticmethod
    def get_submission_history(user_id, limit=30):
        """
        获取用户的提交历史记录。
        :param user_id: 用户ID
        :param limit: 返回记录数量
        :return: 提交记录列表
        """
        try:
            return ability_matrix_model.get_submission_history(user_id, limit)
        except Exception as e:
            logging.error(f"获取提交历史失败: {e}")
            return {"error": f"服务器错误: {str(e)}"}, 500

    @staticmethod
    def get_ability_trend(user_id, dimension, days=30):
        """
        获取用户在指定维度上的能力趋势。
        :param user_id: 用户ID
        :param dimension: 能力维度
        :param days: 统计天数
        :return: 趋势数据
        """
        try:
            return ability_matrix_model.get_ability_trend(user_id, dimension, days)
        except Exception as e:
            logging.error(f"获取能力趋势失败: {e}")
            return {"error": f"服务器错误: {str(e)}"}, 500

    @staticmethod
    def get_all_trends(user_id, days=30):
        """
        获取用户在所有维度上的能力趋势。
        :param user_id: 用户ID
        :param days: 统计天数
        :return: 所有维度的趋势数据
        """
        try:
            trends = {}
            for dim in AbilityMatrixService.DIMENSIONS:
                result, status = ability_matrix_model.get_ability_trend(user_id, dim, days)
                if status == 200:
                    trends[dim] = {
                        'label': AbilityMatrixService.DIMENSION_LABELS[dim],
                        'data': result.get('trend', [])
                    }
                else:
                    trends[dim] = {
                        'label': AbilityMatrixService.DIMENSION_LABELS[dim],
                        'data': []
                    }

            return {"trends": trends, "days": days}, 200

        except Exception as e:
            logging.error(f"获取所有能力趋势失败: {e}")
            return {"error": f"服务器错误: {str(e)}"}, 500

    @staticmethod
    def get_learning_recommendations(user_id):
        """
        根据用户的能力矩阵生成个性化学习推荐。
        :param user_id: 用户ID
        :return: 学习推荐列表
        """
        try:
            weak_result, weak_status = ability_matrix_model.get_weak_dimensions(user_id)
            if weak_status != 200:
                return weak_result, weak_status

            weak_dims = weak_result.get('weak_dimensions', [])

            recommendations = []
            for dim in weak_dims[:3]:  # 最多推荐3个薄弱项
                recommendations.append({
                    'dimension': dim['dimension'],
                    'label': dim['label'],
                    'current_score': dim['score'],
                    'suggestion': dim['suggestion'],
                    'recommended_tasks': get_recommended_tasks(dim['dimension'])
                })

            return {"recommendations": recommendations, "count": len(recommendations)}, 200

        except Exception as e:
            logging.error(f"生成学习推荐失败: {e}")
            return {"error": f"服务器错误: {str(e)}"}, 500


# get_recommended_tasks 已迁移至 app.utils.ability_matrix_calculator
