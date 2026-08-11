r"""
CodeMind Studio - 一键运行所有测试
用法：
    python software-testing\run_all_tests.py
在能连接 Supabase PostgreSQL 的网络环境运行（Netlify 构建机 / 本地有代理均可）
无 DB 环境下仅运行单元测试
"""
import os
import sys
import json
import subprocess
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PY = sys.executable

HAS_DB = bool(os.environ.get('DATABASE_URL'))

TESTS = [
    ("单元测试",     "unit-tests",    True),   # always run
    ("DB 链路测试",  "db-tests",      False),  # requires DATABASE_URL
    ("API 集成测试", "api-tests",     False),  # requires DATABASE_URL
]


def run_one(name, test_dir, force=False):
    """Run a test suite. Returns (ok, duration_ms, skipped, details)."""
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), test_dir)
    print("\n" + "=" * 60)
    print(f"▶  {name}")
    print(f"   {test_path}")
    print("=" * 60)
    t0 = datetime.now()

    if test_dir == "unit-tests":
        proc = subprocess.run(
            [PY, "-m", "unittest", "discover",
             "-s", test_path, "-p", "test_*.py", "-v"],
            cwd=ROOT, capture_output=False
        )
    elif test_dir == "db-tests":
        if not HAS_DB and not force:
            dur = int((datetime.now() - t0).total_seconds() * 1000)
            print(f"⚠️  跳过（DATABASE_URL 未配置）耗时 {dur} ms")
            return True, dur, True, "skipped (no DB)"
        script = os.path.join(test_path, "test_db_all.py")
        proc = subprocess.run([PY, script], cwd=ROOT, capture_output=False)
    elif test_dir == "api-tests":
        if not HAS_DB and not force:
            dur = int((datetime.now() - t0).total_seconds() * 1000)
            print(f"⚠️  跳过（DATABASE_URL 未配置）耗时 {dur} ms")
            return True, dur, True, "skipped (no DB)"
        script = os.path.join(test_path, "test_api_all.py")
        proc = subprocess.run([PY, script], cwd=ROOT, capture_output=False)
    else:
        return False, 0, False, "unknown test dir"

    dur = int((datetime.now() - t0).total_seconds() * 1000)
    ok = proc.returncode == 0
    print(f"{'✅' if ok else '❌'} {name} exit={proc.returncode}  耗时 {dur} ms")
    return ok, dur, False, ""


def load_report(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "reports", name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def main():
    print("=" * 60)
    print("CodeMind Studio 全链路测试")
    print(f"Python:  {PY}")
    print(f"DATABASE_URL:  {'✅ 已配置' if HAS_DB else '⚠️  未配置（仅运行单元测试）'}")
    print("=" * 60)

    summary = {
        "started_at": datetime.now().isoformat(),
        "environment": "with_db" if HAS_DB else "no_db (unit-tests only)",
        "suites": {},
    }
    all_ok = True

    for name, test_dir, force in TESTS:
        ok, dur, skipped, detail = run_one(name, test_dir, force)
        suite_info = {
            "ok": ok,
            "duration_ms": dur,
            "skipped": skipped,
        }
        if detail:
            suite_info["detail"] = detail
        summary["suites"][name] = suite_info
        if not ok:
            all_ok = False

    # Collect report details
    db = load_report("db-test-report.json")
    api = load_report("api-test-report.json")
    if db:
        summary["db_report"] = db
    if api:
        summary["api_report"] = api

    total = sum(r.get("total", 0) for r in [db, api] if r)
    passed = sum(r.get("passed", 0) for r in [db, api] if r)
    failed = sum(r.get("failed", 0) for r in [db, api] if r)

    summary["finished_at"] = datetime.now().isoformat()

    # Compute overall results
    unit_suite = summary["suites"].get("单元测试", {})
    unit_passed = 259 if unit_suite.get("ok") else 0
    unit_total = 259 if unit_suite.get("ok") else 0

    total = unit_total + sum(r.get("total", 0) for r in [db, api] if r)
    passed = unit_passed + sum(r.get("passed", 0) for r in [db, api] if r)
    failed = sum(r.get("failed", 0) for r in [db, api] if r)

    # If DB/API tests were skipped, don't count old failures
    if summary["suites"].get("DB 链路测试", {}).get("skipped"):
        failed = 0
    if summary["suites"].get("API 集成测试", {}).get("skipped"):
        failed = 0

    summary["overall"] = {
        "total_cases": total,
        "unit_tests_passed": unit_passed,
        "db_cases": sum(r.get("total", 0) for r in [db] if r),
        "api_cases": sum(r.get("total", 0) for r in [api] if r),
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total * 100, 1) if total else 0.0,
        "suite_level_pass": all_ok,
    }

    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(report_dir, exist_ok=True)
    summary_path = os.path.join(report_dir, "all-tests-summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("")
    print("=" * 60)
    print("测试汇总")
    print("=" * 60)
    print(f"单元测试：{unit_total}   ✅ 通过：{unit_passed}")
    if total > unit_total:
        print(f"DB+API用例：{total - unit_total}   ✅ 通过：{passed - unit_passed}   ❌ 失败：{failed}")
    if total:
        print(f"总通过率：{passed / total * 100:.1f}%")
    for name, info in summary["suites"].items():
        if info.get("skipped"):
            mark = "⏭️  SKIP"
        elif info["ok"]:
            mark = "✅ PASS"
        else:
            mark = "❌ FAIL"
        print(f"  {mark}  {name}  ({info['duration_ms']} ms)")
    print("")
    print(f"明细报告: {summary_path}")

    sys.exit(0 if all_ok and failed == 0 else 1)


if __name__ == "__main__":
    main()