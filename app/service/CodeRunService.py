from typing import Dict
from app.Docker.sandbox import execute_code
from app.service.CodeService import get_test_cases

def test_run(test_cases, code: str, language: str, task_id: str = None):
    # 存储结果
    results = []
    # 遍历测试用例
    for test_case in test_cases:
        # 执行代码
        result = execute_code(code, language, task_id, test_case["input"])
        # 检查输出是否符合预期
        success = (result["output"] == test_case["output"])
        results.append({
            "success": success,  # 执行结果
            "run_time": result["run_time"],  # 执行时间
            "input": test_case["input"],  # 输入
            "expected_output": test_case["output"],  # 预期输出
            "actual_output": result["output"],  # 实际输出
            "error": result["error"]  # 错误信息
        })
    return results


def review_algorithm_code(
        code: str,
        language: str,
        task_id: str = None,
        question_id=None
) -> Dict:
    """
    代码评审函数
    :param code: 算法代码
    :param language: 语言
    :param question_id: 题目ID
    :param task_id: 任务ID
    :return: 评审结果
    """

    # 查询题目测试用例（输入、输出）
    test_cases = get_test_cases(int(question_id))

    # 执行测试用例
    results = test_run(test_cases, code, language, task_id)

    # 统计结果
    total_cases = len(results)
    passed_cases = sum(1 for result in results if result["success"])
    failed_cases = total_cases - passed_cases
    # 生成评审报告
    report = {
        "task_id": task_id,  # 任务ID
        "success": failed_cases == 0,  # 评审结果
        "question_id": question_id,  # 题目ID
        "total_cases": total_cases,  # 总用例数
        "passed_cases": passed_cases,  # 通过用例数
        "failed_cases": failed_cases,  # 失败用例数
        "results": results  # 测试结果
    }
    # 返回评审报告
    # print("\n\n", "="*20, report, "="*20, "\n\n")
    return report
