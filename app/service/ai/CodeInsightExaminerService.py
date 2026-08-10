"""
CodeInsightExaminer 代码审查服务模块Service

该模块提供基于AI模型的代码审查服务，主要包含以下功能：
1. 调用火山引擎API进行代码分析
2. 解析和修复API返回的JSON数据
3. 格式化审查结果输出
4. 处理算法题目批改
"""

from typing import Optional, List, Dict
import uuid
from threading import Thread
import logging
from flask import current_app, Flask

from app.service.CodeRunService import review_algorithm_code
from app.models.ai import CodeInsightExaminer
from app.service.ai.volcengine_api_caller import volcengine_api_caller
from app.service.QusetionSevice import QuestionService
from app.utils import *


# 修复 JSON 字符串中的换行符问题（将字符串内的换行符转义为 \n）
def escape_newlines(match):
    return match.group(0).replace('\n', '\\n')


# 全局存储批改结果的字典
algorithm_review_results = {}


# 创建一个日志记录器，避免在线程中使用 current_app
logger = logging.getLogger('algorithm_review')


class CodeReviewService:
    """
    CodeReviewService 类用于封装 CodeInsightExaminer 模型的服务逻辑。
    """

    def __init__(self):
        self.model = CodeInsightExaminer()
        self.app = None
        if current_app:
            self.app = current_app._get_current_object()  # 获取实际的应用实例

    def review_code(
            self,
            user_code: str,
            additional_messages: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        # 参数校验
        if not isinstance(user_code, str) or not user_code.strip():
            raise ValueError("user_code 必须是非空字符串")

        try:
            # 调用API
            response = volcengine_api_caller(
                model=self.model,
                message=user_code,
                message_list=additional_messages
            )

            # 使用工具类处理响应
            return APIResponseProcessor.process_response(response)

        except Exception as e:
            raise RuntimeError(f"代码审查异常: {str(e)}")

    def parse_review_result(self, review_result: Dict) -> Dict:
        """
        解析审查结果，提取关键信息。

        参数:
            review_result (Dict): 审查结果字典。

        返回:
            Dict: 包含解析后信息的字典。
        """
        if not review_result or "reviewed_code" not in review_result or "summary" not in review_result:
            raise ValueError("无效的审查结果")

        reviewed_code = review_result.get("reviewed_code", "")
        summary = review_result.get("summary", {})

        strengths = summary.get("strengths", [])
        issues = summary.get("issues", [])
        suggestions = summary.get("suggestions", [])

        # 计算得分
        initial_score = 100
        score = initial_score
        score += len(strengths) * 5  # 每个优点加 5 分
        score -= len(issues) * 10    # 每个问题减 10 分
        score -= len(suggestions) * 3  # 每个建议减 3 分

        # 限制得分范围
        score = max(0, min(score, 100))

        parsed_result = {
            "reviewed_code": reviewed_code,
            "strengths": strengths,
            "issues": issues,
            "suggestions": suggestions,
            "score": score  # 新增得分字段
        }

        return parsed_result

    def format_review_result(self, parsed_result: Dict) -> str:
        """
        格式化审查结果，便于展示给用户。

        参数:
            parsed_result (Dict): 解析后的审查结果字典。

        返回:
            str: 格式化后的审查结果。
        """
        reviewed_code = parsed_result.get("reviewed_code", "")
        strengths = parsed_result.get("strengths", [])
        issues = parsed_result.get("issues", [])
        suggestions = parsed_result.get("suggestions", [])
        score = parsed_result.get("score", 0)  # 获取得分

        formatted_result = []

        # 添加得分
        formatted_result.append(f"综合评分：{score}/100\n")

        # 添加带注释的代码
        formatted_result.append("审查后的代码：")
        formatted_result.append(reviewed_code)

        # 添加优点
        if strengths:
            formatted_result.append("\n优点：")
            formatted_result.extend([f"- {item}" for item in strengths])

        # 添加问题
        if issues:
            formatted_result.append("\n问题：")
            formatted_result.extend([f"- {item}" for item in issues])

        # 添加建议
        if suggestions:
            formatted_result.append("\n建议：")
            formatted_result.extend([f"- {item}" for item in suggestions])

        return "\n".join(formatted_result)
        
    def review_algorithm_code(
            self,
            code: str,
            language: str,
            question_id: Optional[str],
            task_id: str
    ) -> Dict:
        """
        异步执行算法代码评估和AI批改
        
        参数:
            code (str): 用户提交的代码
            language (str): 编程语言
            question_id (str, optional): 题目ID
            task_id (str): 任务ID，用于后续查询结果
            
        返回:
            Dict: 包含运行结果的字典
        """
        # 参数校验
        if not isinstance(code, str) or not code.strip():
            raise ValueError("代码不能为空")
            
        # 我们不再强制依赖从数据库获取的题目信息
        question_data = None
        try:
            # QuestionService.get_question_by_id返回的是元组 (data, status_code)
            # 这个步骤可能会失败，但我们不会中断整个流程
            if question_id:
                result = None
                try:
                    result = QuestionService.get_question_by_id(question_id)
                    if isinstance(result, tuple) and len(result) > 0:
                        # 提取实际的问题数据
                        question_data = result[0].get('question') if isinstance(result[0], dict) else None
                    
                    if current_app:
                        current_app.logger.info(f"获取到题目数据: {question_data is not None}")
                    else:
                        logger.info(f"获取到题目数据: {question_data is not None}")
                except Exception as e:
                    # 记录错误但继续执行
                    if current_app:
                        current_app.logger.warning(f"获取题目数据失败，将继续评估代码: {str(e)}")
                    else:
                        logger.warning(f"获取题目数据失败，将继续评估代码: {str(e)}")
        except Exception as e:
            if current_app:
                current_app.logger.error(f"获取题目数据失败: {str(e)}")
            else:
                logger.error(f"获取题目数据失败: {str(e)}")
        
        # 模拟同步运行结果
        run_result = self._run_code(code, language, question_id, task_id)
        
        # 保存应用实例，以便在线程中使用
        app = self.app or current_app._get_current_object() if current_app else None
        
        # 启动异步AI批改
        Thread(target=self._process_ai_review, args=(code, language, question_data, task_id, run_result, app)).start()
        
        return run_result
    
    def _run_code(self, code: str, language: str,  question_id, task_id) -> Dict:
        """
        运行代码并返回结果（模拟）
        
        在实际实现中，应该通过沙箱环境运行代码并测试用例
        """
        # TODO: 实现真实的代码运行和测试用例验证

        review = review_algorithm_code(code=code, language=language, question_id=question_id, task_id=task_id)
        return review

        # 运行结果返回格式
        # {
        #     'id': task_id,
        #     'run_time': execution_result['run_time'],
        #     'success': execution_result['success'],
        #     'output': execution_result['output'],
        #     'error': execution_result['error'],
        #     'test_passed': passed,
        #     'test_total': total,
        #     'test_details': test_details,
        #     'timestamp': datetime.now().isoformat()
        # }
    
    def _process_ai_review(
            self, 
            code: str, 
            language: str, 
            question_data: Optional[Dict],
            task_id: str,
            run_result: Dict,
            app: Optional[Flask] = None
    ) -> None:
        """
        处理AI批改任务
        """
        # 使用应用上下文
        if app:
            with app.app_context():
                self._do_process_ai_review(code, language, question_data, task_id, run_result)
        else:
            # 没有应用实例时，直接处理
            self._do_process_ai_review(code, language, question_data, task_id, run_result)
    
    def _do_process_ai_review(
            self,
            code: str, 
            language: str, 
            question_data: Optional[Dict],
            task_id: str,
            run_result: Dict
    ) -> None:
        """
        实际处理AI批改的内部方法
        """
        try:
            # 如果question_data为None，不要中断批改流程
            if question_data is None:
                if current_app:
                    current_app.logger.warning(f"题目数据不存在，将仅对代码进行评估，任务ID: {task_id}")
                else:
                    logger.warning(f"题目数据不存在，将仅对代码进行评估，任务ID: {task_id}")
            
            # 构建提示信息
            prompt = self._build_prompt(code, language, question_data, run_result)
            
            # 调用AI模型
            try:
                review_result = self.review_code(prompt)
                
                # 解析审查结果
                parsed_result = self.parse_review_result(review_result)
                
                # 适配前端需要的格式
                result = {
                    "status": "complete",
                    "score": self._calculate_score(parsed_result),
                    "feedback": self._generate_feedback(parsed_result),
                    "improvements": parsed_result.get("suggestions", []),
                    "original_code": code,  # 添加原始代码
                    "reviewed_code": parsed_result.get("reviewed_code", ""),  # 添加带注释的代码
                    "language": language  # 添加代码语言信息
                }
                
                # 保存结果
                algorithm_review_results[task_id] = result
                
                # 记录日志
                if current_app:
                    current_app.logger.info(f"AI批改完成，任务ID: {task_id}")
                    current_app.logger.debug(f"批改结果: {result}")
                else:
                    logger.info(f"AI批改完成，任务ID: {task_id}")
                    logger.debug(f"批改结果: {result}")
            except ValueError as json_error:
                # 特别处理JSON解析错误
                error_msg = f"JSON解析失败: {str(json_error)}"
                if current_app:
                    current_app.logger.error(error_msg)
                else:
                    logger.error(error_msg)
                
                # 更新结果
                algorithm_review_results[task_id] = {
                    "status": "error",
                    "message": f"AI批改处理失败: JSON格式错误，请重试提交"
                }
            
        except Exception as e:
            # 记录错误
            error_msg = f"AI批改错误: {str(e)}"
            if current_app:
                current_app.logger.error(error_msg)
            else:
                logger.error(error_msg)
                
            # 更新结果
            algorithm_review_results[task_id] = {
                "status": "error",
                "message": f"AI批改过程中发生错误: {str(e)}"
            }
    
    def _build_prompt(
            self, 
            code: str, 
            language: str, 
            question_data: Optional[Dict],
            run_result: Dict
    ) -> str:
        """
        构建发送给AI模型的提示
        """
        prompt_parts = [
            f"以下是一段使用{language}语言编写的算法代码:",
            "\n\n代码:\n```",
            code,
            "```\n"
        ]
        
        # 处理题目数据
        if question_data:
            prompt_parts.append("\n题目描述:\n")
            
            # 安全获取题目属性
            try:
                # 尝试直接访问字典
                if isinstance(question_data, dict):
                    title = question_data.get("title", "")
                    content = question_data.get("content", "")
                    prompt_parts.append(f"{title}\n{content}\n")
                # 尝试作为对象访问
                else:
                    if hasattr(question_data, "title"):
                        prompt_parts.append(f"{question_data.title}\n")
                    if hasattr(question_data, "content"):
                        prompt_parts.append(f"{question_data.content}\n")
            except Exception as e:
                # 记录错误但继续处理
                logger.error(f"处理题目数据时出错: {str(e)}")
                prompt_parts.append("无法解析题目数据\n")
        else:
            # 没有题目数据时使用通用指令
            prompt_parts.append("\n请对代码进行评估，关注以下几点:\n")
            prompt_parts.append("1. 代码的正确性和逻辑性\n")
            prompt_parts.append("2. 算法效率和时间复杂度\n")
            prompt_parts.append("3. 代码风格和可读性\n")
            prompt_parts.append("4. 可能存在的边界情况处理\n")
        
        prompt_parts.extend([
            "\n运行结果:\n",
            f"状态: {run_result.get('status')}\n",
            f"输出: {run_result.get('output')}\n",
            f"测试通过: {run_result.get('test_passed')}\n",
            f"执行时间: {run_result.get('execution_time')}\n",
        ])
        
        return "".join(prompt_parts)
    
    def _calculate_score(self, parsed_result: Dict) -> int:
        """
        根据解析结果计算分数
        """
        # 基础分数
        base_score = 70
        
        # 根据优点增加分数
        strengths = parsed_result.get("strengths", [])
        strength_score = min(len(strengths) * 5, 15)
        
        # 根据问题减少分数
        issues = parsed_result.get("issues", [])
        issue_score = min(len(issues) * 8, 30)
        
        # 根据建议数量适当调整
        suggestions = parsed_result.get("suggestions", [])
        suggestion_adjustment = min(len(suggestions), 5)
        
        # 计算总分
        final_score = base_score + strength_score - issue_score + suggestion_adjustment
        
        # 确保分数在0-100范围内
        return max(0, min(100, final_score))
    
    def _generate_feedback(self, parsed_result: Dict) -> str:
        """
        根据解析结果生成总体反馈
        """
        strengths = parsed_result.get("strengths", [])
        issues = parsed_result.get("issues", [])
        
        if not issues:
            return "代码质量很好，思路清晰，逻辑正确。" + (strengths[0] if strengths else "")
        elif len(issues) == 1:
            return f"代码基本正确，但存在一个问题：{issues[0]}"
        else:
            return f"代码存在{len(issues)}个问题，主要包括：{issues[0]}"


# 获取算法题批改结果
def get_algorithm_review_result(task_id: str) -> Dict:
    """
    获取算法批改任务的结果
    
    参数:
        task_id (str): 任务ID
        
    返回:
        Dict: 包含批改结果的字典
    """
    return algorithm_review_results.get(task_id, {"status": "processing"})


if __name__ == "__main__":
    # 初始化服务
    service = CodeReviewService()

    # 用户代码
    user_code = """
def add_numbers(a, b)
    return a + b
"""

    try:
        # 调用代码审查
        review_result = service.review_code(user_code)

        # 解析审查结果
        parsed_result = service.parse_review_result(review_result)

        # 输出结果
        print("代码审查结果：")
        print(parsed_result, "\n\n", review_result)

        # 格式化审查结果
        formatted_result = service.format_review_result(parsed_result)
        print("\n格式化后的审查结果：")
        print(formatted_result)
    except Exception as e:
        print(f"发生错误: {e}")
