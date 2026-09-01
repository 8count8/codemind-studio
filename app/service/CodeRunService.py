"""
代码运行与测试用例判分（基于沙箱）。

这里的函数对原 CodeRunService 做了增强：
1) test_run / review_algorithm_code 保持原返回结构兼容（调用方 0 改动）
2) 新增输出标准化：expected vs actual 比较时会 strip 两侧空格 / 统一换行符 / 去掉尾部多余空行
3) 新增 run_code_single() 供答题板"运行代码"按钮使用（无测试用例，仅跑用户示例输入）
4) 新增 judge() 统一函数：返回 total_cases / passed_cases / failed_cases / results 及汇总 message
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app.Docker.sandbox import execute_code, check_runtime_requirements
from app.service.CodeService import get_test_cases

log = logging.getLogger('CodeRunService')


def _normalize_output(s: Optional[str]) -> str:
    """
    标准化输出，减少不必要的"输出 vs 预期"错判：
    - 去首尾空白（含 NBSP / \r\n / 中文空格）
    - 行首 / 行尾空白逐行 strip
    - 去掉文件结尾多余空行（很多人最后多打一个 print()）
    """
    if s is None:
        return ''
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    # 逐行 strip 首尾
    lines = [ln.strip() for ln in s.split('\n')]
    # 去掉尾部空行
    while lines and lines[-1] == '':
        lines.pop()
    return '\n'.join(lines)


def test_run(test_cases: List[Dict], code: str, language: str, task_id: str = None) -> List[Dict]:
    """跑一组测试用例并返回每条是否通过 + 实际输出 + 错误"""
    results: List[Dict] = []
    for idx, tc in enumerate(test_cases):
        case_id = f"{task_id or 'case'}#{idx}"
        case_input = tc.get("input")
        expected_raw = tc.get("output")
        try:
            exec_result = execute_code(code, language, case_id, case_input)
        except Exception as e:
            results.append({
                "index": idx,
                "input": case_input,
                "expected_output": expected_raw,
                "actual_output": None,
                "success": False,
                "run_time": 0,
                "error": f"Sandbox error: {e}",
            })
            continue

        actual_raw = exec_result.get("output")
        expected_norm = _normalize_output(expected_raw)
        actual_norm = _normalize_output(actual_raw)

        # 通过条件：执行成功（returncode==0）且标准化输出 == 标准化预期
        case_ok = bool(exec_result.get("success")) and (expected_norm == actual_norm)

        results.append({
            "index": idx,
            "input": case_input,
            "expected_output": expected_raw,
            "actual_output": actual_raw,
            "success": case_ok,
            "run_time": exec_result.get("run_time", 0),
            "error": exec_result.get("error"),
            "_normalized_expected": expected_norm,   # 调试用下划线前缀，AI 会忽略
            "_normalized_actual": actual_norm,
            "sandbox_mode": exec_result.get("sandbox_mode"),
        })
    return results


def review_algorithm_code(
        code: str,
        language: str,
        task_id: str = None,
        question_id=None,
) -> Dict:
    """
    代码评审函数（原 CodeInsightExaminerService._run_code 调用这里；保持原 JSON 字段不变）。

    - 没传 question_id / 没有测试用例：直接返回 sandbox 不可用提示，让 AI 纯静态判分
    - 有测试用例：逐条跑，统计通过数
    """
    test_cases: List[Dict] = []
    try:
        if question_id:
            test_cases = get_test_cases(int(question_id)) or []
    except Exception as e:
        log.warning("加载测试用例失败 question_id=%s err=%s", question_id, e)

    if not test_cases:
        return {
            "task_id": task_id,
            "question_id": question_id,
            "success": False,
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "results": [],
            "note": "No test cases available for this question. AI will grade based on static analysis only.",
        }

    # 先做"本机是否具备该语言运行环境"预检（避免 Docker 不存在 + native 也没有时，一条一条报同样错浪费时间）
    env_check = check_runtime_requirements(language)
    if not env_check.get("available"):
        return {
            "task_id": task_id,
            "question_id": question_id,
            "success": False,
            "total_cases": len(test_cases),
            "passed_cases": 0,
            "failed_cases": len(test_cases),
            "results": [],
            "note": (
                "Unable to execute user code: " + env_check.get("message", "") +
                " AI will grade based on static analysis only. "
                "Install Docker Desktop for Windows/Mac, or install the required compiler/interpreter locally."
            ),
            "runtime_check": env_check,
        }

    results = test_run(test_cases, code, language, task_id)
    total = len(results)
    passed = sum(1 for r in results if r.get("success"))
    failed = total - passed

    report = {
        "task_id": task_id,
        "success": failed == 0,
        "question_id": question_id,
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": failed,
        "results": results,
        "runtime_check": env_check,
        "note": (
            f"Passed {passed}/{total} test cases via {env_check.get('mode')} sandbox. "
            if env_check.get("mode") else
            f"Passed {passed}/{total} test cases. "
        ),
    }
    return report


def run_code_single(code: str, language: str, sample_input: Optional[str] = None,
                    task_id: Optional[str] = None) -> Dict:
    """
    答题板"运行代码"按钮用：没有测试用例时，只跑一次（通常用一个 sample input）。
    返回 run_time / success / output / error + 环境检查
    """
    env_check = check_runtime_requirements(language)
    if not env_check.get("available"):
        return {
            "task_id": task_id,
            "success": False,
            "run_time": 0,
            "output": None,
            "error": "Runtime not available: " + env_check.get("message", ""),
            "runtime_check": env_check,
        }
    try:
        res = execute_code(code, language, task_id or "run-once", sample_input)
    except Exception as e:
        return {
            "task_id": task_id,
            "success": False,
            "run_time": 0,
            "output": None,
            "error": f"Sandbox error: {e}",
            "runtime_check": env_check,
        }
    res["runtime_check"] = env_check
    return res
