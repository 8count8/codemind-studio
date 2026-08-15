"""
CodeMind Studio - 后端 Flask API 集成测试（真实 DB，不使用 Mock）
- 使用 Flask test_client 发请求
- 覆盖: 注册/登录/CSRF/状态检查  +  题库 CRUD  +  收藏夹  +  能力矩阵
  操作记录  +  代码审查接口（需 AI_KEY 才通过全流程）
目录：software-testing/api-tests/
"""
import os
import sys
import json
import time
import random
import string
import traceback
import tempfile
from datetime import datetime

# 确保项目根目录在 sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 加载 .env（本地测试用；生产环境由环境变量注入）
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, '.env'))
except Exception:
    pass

TEST_PREFIX = "TEST_API_"
RESULT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "reports",
    "api-test-report.json",
)

results = {
    "started_at": datetime.now().isoformat(),
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": [],
}


def rand_str(n=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))


USERNAME = f"{TEST_PREFIX}_{rand_str()}"
EMAIL = f"{USERNAME}@example.com"
PASSWORD = "Test@123456"


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


# =====================================================
# 创建 Flask test_client + 初始化 DB
# =====================================================
def create_test_client():
    import config
    from app import create_app
    from app.models.db import init_database

    # 测试配置：使用 ProductionConfig（强制真实 DB；不伪造 SQLite）
    # 如果本地没有 DB_HOST，就会抛异常
    app = create_app(config=config.TestingConfig
                     if hasattr(config, 'TestingConfig')
                     else config.ProductionConfig)

    # 为了 test_client 能正确保存 session cookie，关闭测试模式
    app.config["TESTING"] = False
    app.config["WTF_CSRF_ENABLED"] = True

    with app.app_context():
        try:
            init_database()
            print("  🔗 MySQL 初始化成功")
        except Exception as e:
            print(f"  ⚠️  初始化数据库跳过: {e}")

    return app.test_client(use_cookies=True)


# =====================================================
# A 组：CSRF + 认证链路
# =====================================================
CSRF_TOKEN = None


def test_auth_group(client):
    global CSRF_TOKEN

    # A01 获取 CSRF Token
    t0 = time.time()
    try:
        resp = client.get("/api/csrf-token")
        ok = resp.status_code == 200
        data = _safe_json(resp)
        CSRF_TOKEN = data.get("csrf_token")
        ok = ok and bool(CSRF_TOKEN)
        record_case("A01 GET /api/csrf-token", ok,
                    f"HTTP={resp.status_code}, token_len={len(CSRF_TOKEN or '')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("A01 GET /api/csrf-token", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # A02 注册前：新用户 auth/status = 未登录
    t0 = time.time()
    try:
        resp = client.get("/auth/status")
        data = _safe_json(resp)
        ok = resp.status_code == 200 and data.get("status") == "not_logged_in"
        record_case("A02 GET /auth/status(未登录)", ok,
                    f"HTTP={resp.status_code} body={_truncate(data)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("A02 GET /auth/status(未登录)", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # A03 注册（需要验证码 —— 这里直接走 验证码跳过通道 / register 接口：
    # 看 app_auth.py 实际表单参数形式）
    t0 = time.time()
    try:
        payload = _csrf_payload(CSRF_TOKEN, {
            "username": USERNAME,
            "password": PASSWORD,
            "confirm_password": PASSWORD,
            "email": EMAIL,
            # 验证码：先 insert 一条，再读出来
        })
        # 手工先写入一个测试验证码，再拿出来提交
        from app.models.user_login import insert_verification_code
        vc = rand_str(6)
        insert_verification_code(EMAIL, vc)
        payload["verification_code"] = vc
        resp = client.post("/register",
                           data=payload,
                           content_type="application/x-www-form-urlencoded",
                           follow_redirects=False)
        # 成功后可能重定向到 /dashboard
        ok = resp.status_code in (200, 302)
        data = None
        try:
            data = resp.get_json(silent=True)
        except Exception:
            pass
        record_case("A03 POST /register(真实验证码)", ok,
                    f"HTTP={resp.status_code} loc={resp.headers.get('Location','')} json={_truncate(data)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("A03 POST /register(真实验证码)", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # A04 登录
    t0 = time.time()
    try:
        payload = _csrf_payload(CSRF_TOKEN, {
            "username": USERNAME,
            "password": PASSWORD,
        })
        resp = client.post("/login",
                           data=payload,
                           content_type="application/x-www-form-urlencoded",
                           follow_redirects=False)
        ok = resp.status_code in (200, 302)
        set_cookie = resp.headers.get("Set-Cookie") or ""
        ok = ok and ("session" in set_cookie.lower() or resp.status_code == 302)
        record_case("A04 POST /login 登录成功", ok,
                    f"HTTP={resp.status_code} cookie_set={bool(set_cookie)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("A04 POST /login 登录成功", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # A05 登录后 auth/status = 已登录
    t0 = time.time()
    try:
        resp = client.get("/auth/status")
        data = _safe_json(resp)
        ok = resp.status_code == 200 and data.get("status") == "logged_in" \
            and data.get("username") == USERNAME
        record_case("A05 GET /auth/status(已登录)", ok,
                    f"HTTP={resp.status_code} body={_truncate(data)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("A05 GET /auth/status(已登录)", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # A06 未登录访问 /dashboard 应该重定向（旧服务端模板保留的访问控制）
    t0 = time.time()
    try:
        c2 = create_test_client()
        resp = c2.get("/dashboard", follow_redirects=False)
        ok = resp.status_code == 302 and "/login" in (resp.headers.get("Location") or "")
        record_case("A06 未登录访问/dashboard → 302 回登录", ok,
                    f"HTTP={resp.status_code} loc={resp.headers.get('Location','')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("A06 未登录访问/dashboard → 302 回登录", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# B 组：题库 /api/questions
# =====================================================
QUESTION_ID = None


def test_quizbank_group(client):
    global QUESTION_ID

    # B01 列表现有题目
    t0 = time.time()
    try:
        resp = client.get("/api/questions")
        data = _safe_json(resp)
        ok = resp.status_code == 200 and "questions" in data
        record_case("B01 GET /api/questions", ok,
                    f"HTTP={resp.status_code} count={len(data.get('questions',[]))}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("B01 GET /api/questions", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # B02 插入题目 (POST /quizbank)
    t0 = time.time()
    title = f"{TEST_PREFIX}_API插入题_{rand_str()}"
    try:
        content = json.dumps({"题目描述": "两数之和"}, ensure_ascii=False)
        payload = _csrf_payload(CSRF_TOKEN, {
            "title": title,
            "content": content,
            "difficulty": "简单",
            "tags": "数组",
        })
        resp = client.post("/quizbank", data=payload,
                           content_type="application/x-www-form-urlencoded",
                           follow_redirects=False)
        ok = resp.status_code in (200, 201, 302)
        record_case("B02 POST /quizbank 插入题目", ok,
                    f"HTTP={resp.status_code}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("B02 POST /quizbank 插入题目", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # B03 列表中读取新插入题目 ID
    t0 = time.time()
    try:
        resp = client.get("/api/questions")
        data = _safe_json(resp)
        target = [q for q in data.get("questions", []) if q.get("title") == title]
        if target:
            QUESTION_ID = target[0].get("id")
        ok = QUESTION_ID is not None
        record_case("B03 读回新插入题目ID", ok,
                    f"id={QUESTION_ID}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("B03 读回新插入题目ID", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# C 组：收藏夹 /favorites + /history + /api/user/favorites
# =====================================================
def test_favorites_history_group(client):
    # C01 GET /favorites 渲染页面（200，不是 302/500）
    t0 = time.time()
    try:
        resp = client.get("/favorites")
        ok = resp.status_code == 200
        record_case("C01 GET /favorites 页面", ok,
                    f"HTTP={resp.status_code}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("C01 GET /favorites 页面", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # C02 POST /api/user/favorites 新增收藏
    t0 = time.time()
    qid = str(QUESTION_ID or rand_str(5))
    qtitle = f"{TEST_PREFIX}_API收藏_{rand_str()}"
    try:
        import json as _json
        payload = {
            "questionId": qid,
            "title": qtitle,
            "content": "两数之和示例内容",
            "difficulty": "简单",
            "tags": ["数组"],
            "action": "add",
        }
        resp = client.post("/api/user/favorites",
                           data=_json.dumps(payload),
                           content_type="application/json",
                           follow_redirects=False)
        data = _safe_json(resp)
        ok = resp.status_code == 200
        record_case("C02 POST /api/user/favorites 新增收藏", ok,
                    f"HTTP={resp.status_code} json={_truncate(data)}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("C02 POST /api/user/favorites 新增收藏", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # C03 GET /api/user/favorites 列出收藏
    t0 = time.time()
    try:
        resp = client.get("/api/user/favorites")
        data = _safe_json(resp)
        ok = resp.status_code == 200 and isinstance(data.get("data"), list)
        record_case("C03 GET /api/user/favorites 列表", ok,
                    f"HTTP={resp.status_code} count={len(data.get('data',[]))}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("C03 GET /api/user/favorites 列表", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# D 组：能力矩阵 /api/ability-matrix/*
# =====================================================
def test_ability_matrix_group(client):
    # D01 GET /ability-matrix 页面
    t0 = time.time()
    try:
        resp = client.get("/ability-matrix")
        ok = resp.status_code == 200
        record_case("D01 GET /ability-matrix 页面", ok,
                    f"HTTP={resp.status_code}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("D01 GET /ability-matrix 页面", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # D02 GET /api/ability-matrix（要求登录，因为用了 session["username"]）
    t0 = time.time()
    try:
        resp = client.get("/api/ability-matrix")
        data = _safe_json(resp)
        ok = resp.status_code == 200 and "matrix" in data
        record_case("D02 GET /api/ability-matrix", ok,
                    f"HTTP={resp.status_code} keys={list(data.keys())[:6]}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("D02 GET /api/ability-matrix", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # D03 POST /api/ability-matrix/submit（代码评估提交）
    t0 = time.time()
    try:
        code = ("def two_sum(nums, target):\n"
                "    # 两数之和哈希法\n"
                "    seen = {}\n"
                "    for i, n in enumerate(nums):\n"
                "        if target - n in seen:\n"
                "            return [seen[target - n], i]\n"
                "        seen[n] = i\n")
        payload = _csrf_payload(CSRF_TOKEN, {
            "code": code,
            "question_id": str(QUESTION_ID or 1),
        })
        resp = client.post("/api/ability-matrix/submit",
                           data=payload,
                           content_type="application/x-www-form-urlencoded",
                           follow_redirects=False)
        data = _safe_json(resp)
        ok = resp.status_code == 200 and "scores" in data
        record_case("D03 POST /api/ability-matrix/submit 评估提交", ok,
                    f"HTTP={resp.status_code} keys={list(data.keys())[:5]}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("D03 POST /api/ability-matrix/submit 评估提交", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # D04 GET /api/ability-matrix/history
    t0 = time.time()
    try:
        resp = client.get("/api/ability-matrix/history")
        data = _safe_json(resp)
        ok = resp.status_code == 200 and "history" in data
        record_case("D04 GET /api/ability-matrix/history", ok,
                    f"HTTP={resp.status_code} count={len(data.get('history',[]))}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("D04 GET /api/ability-matrix/history", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # D05 GET /api/ability-matrix/recommendations
    t0 = time.time()
    try:
        resp = client.get("/api/ability-matrix/recommendations")
        data = _safe_json(resp)
        ok = resp.status_code == 200 and isinstance(data.get("recommendations"), list)
        record_case("D05 GET /api/ability-matrix/recommendations", ok,
                    f"HTTP={resp.status_code} count={len(data.get('recommendations',[]))}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("D05 GET /api/ability-matrix/recommendations", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# E 组：代码审查 /process_code
# =====================================================
def test_code_review_group(client):
    # E01 /code-review 页面
    t0 = time.time()
    try:
        resp = client.get("/code-review")
        ok = resp.status_code == 200
        record_case("E01 GET /code-review 页面", ok,
                    f"HTTP={resp.status_code}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("E01 GET /code-review 页面", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # E02 POST /process_code 带真实代码（没配置 AI KEY 也应该返回错误响应，不崩 500）
    t0 = time.time()
    try:
        code = '''
# 故意写一个有明显缺陷的 Python 代码
import sqlite3
def find_user(username):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    # 明显存在 SQL 注入
    cur.execute(f"SELECT * FROM users WHERE username='{username}'")
    return cur.fetchall()
'''
        payload = _csrf_payload(CSRF_TOKEN, {
            "file_name": f"{TEST_PREFIX}_bad.py",
            "request_type": "code_review",
            "code_text": code,
        })
        resp = client.post("/process_code",
                           data=payload,
                           content_type="application/x-www-form-urlencoded",
                           follow_redirects=False)
        # 无论成功还是报错（AI 未配置），都不该 500
        ok = resp.status_code < 500
        detail = f"HTTP={resp.status_code}"
        data = _safe_json(resp)
        if isinstance(data, dict) and "error" in data:
            detail += f" error={_truncate(data.get('error'))}"
        elif isinstance(data, dict) and "result" in data:
            detail += " result 返回"
        record_case("E02 POST /process_code（无500崩溃）", ok, detail,
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("E02 POST /process_code（无500崩溃）", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# G 组：错误路径 / 边界条件测试
# =====================================================
def test_error_paths_group(client):
    """使用独立的未登录客户端测试 401 错误"""
    unauth_client = create_test_client()

    # G01 未登录访问 GET /api/user/favorites → 401
    t0 = time.time()
    try:
        resp = unauth_client.get("/api/user/favorites")
        ok = resp.status_code == 401
        data = _safe_json(resp)
        record_case("G01 未登录 GET /api/user/favorites → 401", ok,
                    f"HTTP={resp.status_code} msg={data.get('message','')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("G01 未登录 GET /api/user/favorites → 401", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # G02 未登录访问 POST /api/user/favorites → 401
    t0 = time.time()
    try:
        payload = {"questionId": "test", "action": "add", "title": "test"}
        resp = unauth_client.post("/api/user/favorites",
                                  data=json.dumps(payload),
                                  content_type="application/json",
                                  follow_redirects=False)
        ok = resp.status_code == 401
        data = _safe_json(resp)
        record_case("G02 未登录 POST /api/user/favorites → 401", ok,
                    f"HTTP={resp.status_code} msg={data.get('message','')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("G02 未登录 POST /api/user/favorites → 401", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # G03 已登录 POST 收藏 - 无效 action → 400
    t0 = time.time()
    try:
        payload = {"questionId": "test_qid", "action": "invalid_action",
                    "title": "test", "difficulty": "简单", "tags": [],
                    "content": "test content"}
        resp = client.post("/api/user/favorites",
                           data=json.dumps(payload),
                           content_type="application/json",
                           follow_redirects=False)
        ok = resp.status_code == 400
        data = _safe_json(resp)
        record_case("G03 已登录 POST /api/user/favorites 无效 action → 400", ok,
                    f"HTTP={resp.status_code} msg={data.get('message','')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("G03 已登录 POST /api/user/favorites 无效 action → 400", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # G04 已登录 POST 收藏 - 缺少 questionId → 500 (当前未强制校验)
    t0 = time.time()
    try:
        payload = {"action": "add", "title": "orphan_fav",
                    "difficulty": "中等", "tags": [], "content": "no qid"}
        resp = client.post("/api/user/favorites",
                           data=json.dumps(payload),
                           content_type="application/json",
                           follow_redirects=False)
        ok = resp.status_code < 500
        data = _safe_json(resp)
        record_case("G04 已登录 POST 收藏 缺少 questionId → 不崩 500", ok,
                    f"HTTP={resp.status_code}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("G04 已登录 POST 收藏 缺少 questionId → 不崩 500", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # G05 POST 代码提交 - 空代码 → 400
    t0 = time.time()
    try:
        payload = {"code": "", "language": "python", "question_id": "1"}
        resp = client.post("/api/process_algorithm_code",
                           data=json.dumps(payload),
                           content_type="application/json",
                           follow_redirects=False)
        ok = resp.status_code == 400
        data = _safe_json(resp)
        record_case("G05 POST /api/process_algorithm_code 空代码 → 400", ok,
                    f"HTTP={resp.status_code} msg={data.get('message','')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("G05 POST /api/process_algorithm_code 空代码 → 400", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # G06 未登录访问 GET /api/ability-matrix → 401
    t0 = time.time()
    try:
        resp = unauth_client.get("/api/ability-matrix")
        ok = resp.status_code == 401
        data = _safe_json(resp)
        record_case("G06 未登录 GET /api/ability-matrix → 401", ok,
                    f"HTTP={resp.status_code} msg={data.get('message','')}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("G06 未登录 GET /api/ability-matrix → 401", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# F 组：登出 + 收尾清理
# =====================================================
def test_logout_and_cleanup(client):
    # F01 登出
    t0 = time.time()
    try:
        resp = client.get("/logout", follow_redirects=False)
        ok = resp.status_code in (200, 302)
        record_case("F01 GET /logout", ok,
                    f"HTTP={resp.status_code}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("F01 GET /logout", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())

    # F02 登出后 auth/status = 未登录
    t0 = time.time()
    try:
        resp = client.get("/auth/status")
        data = _safe_json(resp)
        ok = data.get("status") == "not_logged_in"
        record_case("F02 登出后 /auth/status = not_logged_in", ok,
                    f"HTTP={resp.status_code}",
                    int((time.time() - t0) * 1000))
    except Exception as e:
        record_case("F02 登出后 /auth/status = not_logged_in", False, str(e),
                    int((time.time() - t0) * 1000))
        print("    " + traceback.format_exc())


# =====================================================
# Helpers
# =====================================================
def _csrf_payload(token, form_data):
    from flask_wtf.csrf import _FlaskFormCSRF
    # flask_wtf 要求字段名 csrf_token
    d = {"csrf_token": token or ""}
    d.update(form_data or {})
    return d


def _safe_json(resp):
    try:
        data = resp.get_json(silent=True)
        if data is not None:
            return data
    except Exception:
        pass
    try:
        return json.loads(resp.data.decode("utf-8", errors="ignore"))
    except Exception:
        return {"_raw": resp.data.decode("utf-8", errors="ignore")[:500]}


def _truncate(obj, n=200):
    s = json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj
    return s[:n] + ("…" if len(s) > n else "")


def cleanup_test_users_db():
    from app.models.db import get_db_connection
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username LIKE %s", (TEST_PREFIX + "%",))
        rows = cur.fetchall()
        uids = [r[0] for r in rows]
        for uid in uids:
            for tbl in ["answer_records", "favorites", "ability_matrix",
                        "api_responses", "user_uploads", "functions_used",
                        "ability_submissions"]:
                try:
                    cur.execute(f"DELETE FROM {tbl} WHERE user_id = %s", (uid,))
                except Exception:
                    pass
            cur.execute("DELETE FROM users WHERE id = %s", (uid,))
        cur.execute("DELETE FROM problems WHERE title LIKE %s", (TEST_PREFIX + "%",))
        conn.commit()
        print(f"  🧹 API 测试收尾：清理 {len(uids)} 个用户")
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()


# =====================================================
# Main
# =====================================================
def main():
    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)
    print("=" * 60)
    print("CodeMind Studio Flask API 集成测试（真实 MySQL）")
    print("=" * 60)
    print(f"测试用户名: {USERNAME}")
    if not os.environ.get("DB_HOST"):
        print("⚠️  未设置 DB_HOST —— 请先在 .env 或环境变量配置 MySQL 连接")

    client = create_test_client()

    try:
        cleanup_test_users_db()
    except Exception as e:
        print(f"  清理历史数据跳过: {e}")

    print("")
    print("【A 认证链路】")
    test_auth_group(client)
    print("")
    print("【B 题库】")
    test_quizbank_group(client)
    print("")
    print("【C 收藏夹/历史】")
    test_favorites_history_group(client)
    print("")
    print("【D 能力矩阵】")
    test_ability_matrix_group(client)
    print("")
    print("【E 代码审查】")
    test_code_review_group(client)
    print("")
    print("【F 登出/收尾】")
    test_logout_and_cleanup(client)
    print("")
    print("【G 错误路径/边界条件】")
    test_error_paths_group(client)

    try:
        cleanup_test_users_db()
    except Exception as e:
        print(f"  收尾清理失败：{e}")

    results["finished_at"] = datetime.now().isoformat()
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("")
    print("=" * 60)
    print(f"总用例={results['total']}  通过={results['passed']}  失败={results['failed']}")
    rate = (results["passed"] / results["total"] * 100) if results["total"] else 0
    print(f"通过率: {rate:.1f}%")
    print(f"结果文件: {RESULT_FILE}")
    print("=" * 60)
    return results["failed"] == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
