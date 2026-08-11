"""
CodeMind Studio - 数据库链路测试（真实 DB，不使用 Mock）
模块：app.models.db / user_login / question_db / favorites_topics / user_operation_records
目录：software-testing/db-tests/
"""
import os
import sys
import json
import time
import random
import string
import traceback
from datetime import datetime

# 确保项目根目录在 sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 加载 .env（本地测试用；Netlify 部署时由环境变量注入）
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, '.env'))
except Exception:
    pass

from app.models.db import (
    get_db_connection,
    init_database,
    fetch_dict,
    fetch_one_dict,
    USE_POSTGRESQL,
)

TEST_PREFIX = "TEST_DB_"
RESULT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "reports",
    "db-test-report.json",
)

results = {
    "started_at": datetime.now().isoformat(),
    "database": "PostgreSQL (Supabase)" if USE_POSTGRESQL else "SQLite",
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": [],
}


def record_case(name, passed, detail="", duration_ms=0):
    results["total"] += 1
    if passed:
        results["passed"] += 1
    else:
        results["failed"] += 1
    results["tests"].append({
        "name": name,
        "passed": bool(passed),
        "detail": str(detail),
        "duration_ms": int(duration_ms),
    })
    mark = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {mark}  {name}  ({duration_ms} ms)  {detail}")


def rand_str(n=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))


def cleanup_test_users():
    """清理之前留下的测试用户"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # 删除所有带 TEST_DB_ 前缀的测试用户（级联影响的表也清理）
        cur.execute("SELECT id FROM users WHERE username LIKE %s", (TEST_PREFIX + "%",))
        rows = cur.fetchall()
        uids = [r[0] for r in rows]
        for uid in uids:
            for tbl in ["answer_records", "favorites", "ability_matrix",
                        "api_responses", "user_uploads", "functions_used"]:
                try:
                    cur.execute(f"DELETE FROM {tbl} WHERE user_id = %s", (uid,))
                except Exception:
                    pass
            cur.execute("DELETE FROM users WHERE id = %s", (uid,))
        conn.commit()
        # 清理测试用题
        cur.execute("DELETE FROM problems WHERE title LIKE %s", (TEST_PREFIX + "%",))
        conn.commit()
        print(f"  🧹 清理 {len(uids)} 个历史测试用户")
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()


# =====================================================
# T1. 数据库连接 & 初始化
# =====================================================
def test_connection_and_init():
    name = "T1-01 初始化数据库连接 + 建表"
    t0 = time.time()
    try:
        ok = init_database()
        duration = int((time.time() - t0) * 1000)
        record_case(name, ok,
                    f"USE_POSTGRESQL={USE_POSTGRESQL}" if ok else "init_database 返回 False",
                    duration)
        return ok
    except Exception as e:
        duration = int((time.time() - t0) * 1000)
        record_case(name, False, str(e), duration)
        print("    " + traceback.format_exc())
        return False


# =====================================================
# T2. 用户模块 (users / verification_codes)
# =====================================================
TEST_USERNAME = None
TEST_EMAIL = None
TEST_PASSWORD = "Test@123456"

from app.models.user_login import (
    register_user,
    check_user_exists,
    insert_verification_code,
    verify_verification_code,
    handle_login,
    get_user_profile,
    handle_register,
)


def test_user_module():
    global TEST_USERNAME, TEST_EMAIL
    TEST_USERNAME = f"{TEST_PREFIX}{rand_str()}"
    TEST_EMAIL = f"{TEST_USERNAME}@example.com"

    # T2-01
    t0 = time.time()
    try:
        ex = check_user_exists(username=TEST_USERNAME, email=TEST_EMAIL)
        record_case("T2-01 新用户首次检查不存在", not ex,
                    "exists=" + str(ex),
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T2-01 新用户首次检查不存在", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T2-02 验证码插入 + 验证
    t0 = time.time()
    code = rand_str(6)
    try:
        insert_verification_code(TEST_EMAIL, code)
        ok = verify_verification_code(TEST_EMAIL, code)
        record_case("T2-02 验证码写入+验证", ok,
                    "email=" + TEST_EMAIL,
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T2-02 验证码写入+验证", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T2-03 注册（通过 register_user，跳过发送邮件）
    t0 = time.time()
    try:
        r = register_user(TEST_USERNAME, TEST_PASSWORD, TEST_EMAIL)
        record_case("T2-03 注册用户", r.get("status") == "success",
                    r.get("message", ""),
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T2-03 注册用户", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T2-04 注册后 check_user_exists 为 True
    t0 = time.time()
    try:
        ex = check_user_exists(username=TEST_USERNAME)
        record_case("T2-04 注册后存在性检查=真", ex, "exists=" + str(ex),
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T2-04 注册后存在性检查=真", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T2-05 登录
    t0 = time.time()
    try:
        r = handle_login(TEST_USERNAME, TEST_PASSWORD)
        record_case("T2-05 登录成功", r.get("status") == "success",
                    r.get("message", ""),
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T2-05 登录成功", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T2-06 错误密码登录失败
    t0 = time.time()
    try:
        r = handle_login(TEST_USERNAME, "WrongPass")
        record_case("T2-06 错误密码登录=失败", r.get("status") == "error",
                    r.get("message", ""),
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T2-06 错误密码登录=失败", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T2-07 获取用户资料
    t0 = time.time()
    try:
        p = get_user_profile(TEST_USERNAME)
        ok = p and p.get("username") == TEST_USERNAME and p.get("email") == TEST_EMAIL
        record_case("T2-07 读取用户资料", ok, str(p),
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T2-07 读取用户资料", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# T3. 题库模块 problems
# =====================================================
from app.models.question_db import (
    insert_question,
    get_all_questions,
    get_question_by_id,
    search_questions_by_title,
    update_question,
)

PROBLEM_ID = None


def test_question_module():
    global PROBLEM_ID
    title = f"{TEST_PREFIX}_算法题_{rand_str()}"
    content = {
        "题目描述": "给定数组，返回两数之和等于 target 的下标",
        "示例": [
            "输入 nums=[2,7,11,15], target=9 → 输出 [0,1]",
        ]
    }
    difficulty = "简单"
    tags = "数组,哈希表"

    # T3-01 插入题目
    t0 = time.time()
    try:
        r, code = insert_question(title, content, difficulty, tags)
        ok = (code == 201)
        record_case("T3-01 插入题目", ok, f"HTTP={code} {r}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T3-01 插入题目", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T3-02 获取全部题目列表
    t0 = time.time()
    try:
        r, code = get_all_questions()
        qs = r.get("questions") or []
        target = [q for q in qs if q.get("title") == title]
        if target:
            PROBLEM_ID = target[0]["id"]
        ok = (code == 200) and len(target) > 0
        record_case("T3-02 列表查询包含新题", ok,
                    f"count={len(qs)}, found={len(target)}, id={PROBLEM_ID}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T3-02 列表查询包含新题", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T3-03 按 ID 查询详情
    t0 = time.time()
    try:
        if PROBLEM_ID is None:
            raise RuntimeError("PROBLEM_ID 未获取到")
        r, code = get_question_by_id(PROBLEM_ID)
        ok = (code == 200) and r.get("question", {}).get("title") == title
        record_case("T3-03 按ID查询详情", ok,
                    f"id={PROBLEM_ID}, title={r.get('question',{}).get('title')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T3-03 按ID查询详情", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T3-04 按标题模糊搜索
    t0 = time.time()
    try:
        r, code = search_questions_by_title(TEST_PREFIX)
        ok = (code == 200) and len(r.get("questions", [])) > 0
        record_case("T3-04 模糊标题搜索", ok,
                    f"匹配={len(r.get('questions', []))}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T3-04 模糊标题搜索", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T3-05 更新题目
    t0 = time.time()
    try:
        new_title = f"{title}_UPD"
        r, code = update_question(PROBLEM_ID, title=new_title, difficulty="中等")
        ok = code == 200
        if ok:
            r2, _ = get_question_by_id(PROBLEM_ID)
            ok = r2.get("question", {}).get("difficulty") == "中等" and \
                 r2.get("question", {}).get("title") == new_title
        record_case("T3-05 更新题目", ok, f"HTTP={code}, {r}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T3-05 更新题目", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# T4. 收藏夹 favorites
# =====================================================
from app.models.favorites_topics import (
    add_favorite,
    get_favorites_with_question,
    search_favorites_by_title,
    delete_favorite,
)

FAV_ID = None


def test_favorites_module():
    global FAV_ID, TEST_USERNAME, PROBLEM_ID
    if TEST_USERNAME is None:
        print("  ⚠️  SKIP（缺少用户）")
        return
    uid = TEST_USERNAME
    title = f"{TEST_PREFIX}_收藏题_{rand_str()}"
    question = "两数之和示例：nums=[2,7,11,15], target=9"

    # T4-01 新增收藏
    t0 = time.time()
    try:
        r, code = add_favorite(uid, title, question, "简单", "数组")
        ok = (code == 200)
        record_case("T4-01 新增收藏", ok, f"HTTP={code} {r}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T4-01 新增收藏", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())
        return

    # T4-02 收藏列表包含新收藏
    t0 = time.time()
    try:
        r, code = get_favorites_with_question(uid)
        favs = r.get("favorites", [])
        target = [f for f in favs if f.get("title") == title]
        if target:
            FAV_ID = target[0]["id"]
        ok = (code == 200) and len(target) > 0
        record_case("T4-02 查询收藏列表", ok,
                    f"count={len(favs)}, found={len(target)}, id={FAV_ID}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T4-02 查询收藏列表", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T4-03 搜索收藏
    t0 = time.time()
    try:
        r, code = search_favorites_by_title(uid, TEST_PREFIX)
        ok = (code == 200) and len(r.get("favorites", [])) > 0
        record_case("T4-03 搜索收藏", ok,
                    f"count={len(r.get('favorites',[]))}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T4-03 搜索收藏", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T4-04 删除收藏
    t0 = time.time()
    try:
        if FAV_ID is None:
            raise RuntimeError("FAV_ID 未获取到")
        r, code = delete_favorite(FAV_ID, uid)
        ok = (code == 200)
        if ok:
            r2, _ = get_favorites_with_question(uid)
            ok = all(f.get("id") != FAV_ID for f in r2.get("favorites", []))
        record_case("T4-04 删除收藏", ok, f"HTTP={code} {r}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T4-04 删除收藏", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# T5. 用户操作记录 functions_used / user_uploads / api_responses
# =====================================================
from app.models.user_operation_records import (
    log_function_usage,
    upload_file_to_db,
    log_api_response,
    get_user_history_combined,
    delete_history_record,
)


def test_operation_records_module():
    if TEST_USERNAME is None:
        print("  ⚠️  SKIP（缺少用户）")
        return
    uid = TEST_USERNAME

    # T5-01 功能使用日志
    t0 = time.time()
    try:
        log_function_usage(uid, "code_review")
        hist = get_user_history_combined(uid) or []
        ok = any(
            r.get("record_type") == "function" and r.get("name") == "code_review"
            for r in hist
        )
        record_case("T5-01 功能使用日志写入+查询", ok,
                    f"history_rows={len(hist)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T5-01 功能使用日志写入+查询", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T5-02 上传文件记录
    t0 = time.time()
    upload_id = None
    try:
        fake_path = f"/tmp/{TEST_PREFIX}_{rand_str()}.py"
        upload_file_to_db(uid, fake_path, "python")
        hist = get_user_history_combined(uid) or []
        uploads = [r for r in hist if r.get("record_type") == "upload"]
        if uploads:
            upload_id = uploads[0].get("id")
        ok = len(uploads) > 0
        record_case("T5-02 上传文件记录写入", ok,
                    f"upload_id={upload_id}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T5-02 上传文件记录写入", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T5-03 API 响应文件记录
    t0 = time.time()
    try:
        if upload_id is None:
            raise RuntimeError("upload_id 未获取到")
        content = "# 代码审查结果 \n\n ```python\nprint('hello')\n```"
        log_api_response(upload_id, f"{TEST_PREFIX}_review.md", content)
        hist = get_user_history_combined(uid) or []
        api_rows = [r for r in hist if r.get("record_type") == "api_response"]
        ok = len(api_rows) > 0
        record_case("T5-03 API响应记录写入", ok,
                    f"api_responses={len(api_rows)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T5-03 API响应记录写入", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# T6. 能力矩阵 ability_matrix
# =====================================================
from app.models.ability_matrix_model import (
    upsert_ability_matrix,
    get_ability_matrix,
    save_submission_record,
    get_submission_history,
)
from app.service.ability_matrix_service import AbilityMatrixService


def test_ability_matrix_module():
    if TEST_USERNAME is None:
        print("  ⚠️  SKIP（缺少用户）")
        return
    uid = TEST_USERNAME

    # T6-01 写入能力矩阵
    t0 = time.time()
    try:
        flat = upsert_ability_matrix(uid, syntax_score=85.0, algorithm_score=60.0,
                                     project_score=70.0, debug_score=55.0,
                                     security_score=50.0)
        ok = flat and flat.get("syntax_score") == 85.0
        # get_ability_matrix 返回 (dict, status_code) 二元组
        r2, st2 = get_ability_matrix(uid)
        matrix = r2.get("matrix") or {}
        ok = ok and st2 == 200 and matrix.get("syntax_score") == 85.0
        record_case("T6-01 能力矩阵插入+读取", ok,
                    f"syntax={matrix.get('syntax_score')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T6-01 能力矩阵插入+读取", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T6-02 保存一次提交记录
    t0 = time.time()
    try:
        scores = {"syntax_score": 80, "algorithm_score": 55, "project_score": 72,
                  "debug_score": 60, "security_score": 48}
        save_submission_record(uid, "algorithm_submit", PROBLEM_ID or 1, scores)
        r, st = get_submission_history(uid)  # (dict, status)
        hist = (r or {}).get("history") or []
        ok = st == 200 and len(hist) >= 1
        record_case("T6-02 提交记录写入", ok, f"history_rows={len(hist)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T6-02 提交记录写入", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # T6-03 计算推荐
    t0 = time.time()
    try:
        recs_result, _ = AbilityMatrixService.get_learning_recommendations(uid)
        recs = recs_result.get("recommendations", []) if isinstance(recs_result, dict) else []
        ok = isinstance(recs, list)
        record_case("T6-03 推荐计算返回List", ok, f"items={len(recs)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("T6-03 推荐计算返回List", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# Main
# =====================================================
def main():
    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)
    print("=" * 60)
    print("CodeMind Studio 数据库链路测试（真实 Supabase PostgreSQL）")
    print(f"开始时间: {results['started_at']}")
    print("=" * 60)

    if not os.environ.get("DATABASE_URL"):
        print("⚠️  未设置 DATABASE_URL —— 请先配置 .env 或环境变量")
        print("   示例: postgresql://postgres:密码@db.xxx.supabase.co:5432/postgres")
        print("=" * 60)

    try:
        cleanup_test_users()
    except Exception as e:
        print(f"  清理失败（可能首次运行）：{e}")

    print("")
    print("【T1 基础连接】")
    ok = test_connection_and_init()
    if not ok:
        print("")
        print("❌ 数据库初始化失败，后续测试中止")
    else:
        print("")
        print("【T2 用户模块】")
        test_user_module()
        print("")
        print("【T3 题库模块】")
        test_question_module()
        print("")
        print("【T4 收藏夹模块】")
        test_favorites_module()
        print("")
        print("【T5 操作记录模块】")
        test_operation_records_module()
        print("")
        print("【T6 能力矩阵模块】")
        test_ability_matrix_module()

        print("")
        try:
            cleanup_test_users()
        except Exception as e:
            print(f"  ⚠️  收尾清理失败：{e}")

    results["finished_at"] = datetime.now().isoformat()
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"总用例={results['total']}  通过={results['passed']}  失败={results['failed']}")
    rate = (results["passed"] / results["total"] * 100) if results["total"] else 0
    print(f"通过率: {rate:.1f}%")
    print(f"结果文件: {RESULT_FILE}")
    print("=" * 60)
    return results["failed"] == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
