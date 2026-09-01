"""
admin_routes.py — 管理员后台 API

包含三部分：
  1. 用户管理：     GET  /api/admin/users           列出所有用户
                   POST /api/admin/users/<id>/reset_password   重置密码
  2. 题目 CRUD：   GET    /api/admin/questions           列出所有题目
                   POST   /api/admin/questions           新增题目
                   PUT    /api/admin/questions/<id>      更新题目
                   DELETE /api/admin/questions/<id>      删除题目
  3. 操作记录审计： GET /api/admin/audit_logs   所有用户的 functions_used / user_uploads / api_responses 合表

注意：项目没有角色权限体系（项目规范明确），所有已登录用户都能访问这些端点。
如果后续要增加角色，仅需在每个路由上加 `@require_auth` 之后的装饰器即可。
"""
from __future__ import annotations

import logging
from typing import Optional

from flask import jsonify, request

from . import admin_bp
from app.models.db import (
    get_db_connection,
    fetch_dict,
    fetch_one_dict,
    VALID_DIFFICULTIES,
)
from app.models.question_db import clear_question_cache
from app.utils.auth import require_admin

log = logging.getLogger('admin_routes')


def _ok(data=None, message="success"):
    return jsonify({"status": 200, "message": message, "data": data})


def _err(message: str, code: int = 400, data=None):
    return jsonify({"status": code, "message": message, "data": data}), code


# =========================================================================
# 1. 用户管理
# =========================================================================
@admin_bp.route('/api/admin/users', methods=['GET'])
@require_admin
def list_users():
    """返回所有注册用户（不返回密码散列），支持按 username / email 模糊搜索"""
    kw = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 200) or 200)
    limit = max(1, min(limit, 1000))

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if kw:
            cur.execute(
                """
                SELECT id, username, email, created_at, last_login
                FROM users
                WHERE username LIKE %s OR email LIKE %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (f"%{kw}%", f"%{kw}%", limit),
            )
        else:
            cur.execute(
                """
                SELECT id, username, email, created_at, last_login
                FROM users
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
        rows = fetch_dict(cur)
        return _ok({
            "total": len(rows),
            "items": [
                {
                    "id": r.get("id"),
                    "username": r.get("username"),
                    "email": r.get("email"),
                    "created_at": str(r.get("created_at")) if r.get("created_at") else None,
                    "last_login": str(r.get("last_login")) if r.get("last_login") else None,
                }
                for r in rows
            ],
        })
    except Exception as e:
        log.exception("list_users 失败")
        return _err(f"数据库错误: {e}", 500)
    finally:
        if conn:
            conn.close()


# =========================================================================
# 2. 题目 CRUD
# =========================================================================
@admin_bp.route('/api/admin/questions', methods=['GET'])
@require_admin
def list_questions():
    kw = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 500) or 500)
    limit = max(1, min(limit, 2000))

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = """
            SELECT id, title, difficulty, tags, content, created_at
            FROM problems
            {}
            ORDER BY id DESC
            LIMIT %s
        """
        params = []
        where = ""
        if kw:
            where = "WHERE title LIKE %s OR content LIKE %s OR tags LIKE %s"
            like = f"%{kw}%"
            params = [like, like, like]
        params.append(limit)
        cur.execute(sql.format(where), params)
        rows = fetch_dict(cur)
        return _ok({"total": len(rows), "items": rows})
    except Exception as e:
        log.exception("list_questions 失败")
        return _err(f"数据库错误: {e}", 500)
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/admin/questions/<int:qid>', methods=['GET'])
@require_admin
def get_question(qid: int):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, content, difficulty, tags, created_at FROM problems WHERE id = %s",
            (qid,),
        )
        row = fetch_one_dict(cur)
        if not row:
            return _err("题目不存在", 404)
        # 同时把测试用例一起返回
        cur.execute(
            """SELECT id, input_data AS input, expected_output AS output, description
               FROM test_cases WHERE problem_id = %s ORDER BY id ASC""",
            (qid,),
        )
        test_cases = fetch_dict(cur)
        row["test_cases"] = test_cases
        return _ok(row)
    except Exception as e:
        log.exception("get_question 失败")
        return _err(f"数据库错误: {e}", 500)
    finally:
        if conn:
            conn.close()


def _validate_question_payload(body: dict) -> Optional[str]:
    """校验题目 + 测试用例 payload。校验失败返回错误信息字符串，成功返回 None。
    字段会原地规范化进 body（title/difficulty/tags/content/test_cases）。
    """
    if not isinstance(body, dict):
        return "请求体必须为 JSON 对象"

    title = (body.get("title") or "").strip()
    if len(title) < 1 or len(title) > 200:
        return "title 不能为空且长度不超过 200"
    body["title"] = title

    difficulty = (body.get("difficulty") or "中等").strip()
    if difficulty not in VALID_DIFFICULTIES:
        return f"difficulty 必须是 {VALID_DIFFICULTIES} 之一"
    body["difficulty"] = difficulty

    tags = body.get("tags")
    if isinstance(tags, list):
        tags_str = ",".join(str(t).strip() for t in tags if str(t).strip())
    elif isinstance(tags, str):
        tags_str = tags.strip()
    else:
        tags_str = ""
    if len(tags_str) > 255:
        return "tags 过长（最多 255 字符）"
    body["tags"] = tags_str

    content = (body.get("content") or "").strip()
    if len(content) < 1:
        return "content 不能为空"
    body["content"] = content

    test_cases = body.get("test_cases") or []
    if not isinstance(test_cases, list):
        return "test_cases 必须是数组"
    cleaned_cases = []
    for i, tc in enumerate(test_cases):
        if not isinstance(tc, dict):
            return f"test_cases[{i}] 不是对象"
        inp = tc.get("input") if tc.get("input") is not None else ""
        out = tc.get("output") if tc.get("output") is not None else ""
        if not isinstance(inp, str) or not isinstance(out, str):
            return f"test_cases[{i}] input/output 必须是字符串"
        cleaned_cases.append({
            "input": inp,
            "output": out,
            "description": (tc.get("description") or "").strip()[:255],
        })
    body["test_cases"] = cleaned_cases
    return None


@admin_bp.route('/api/admin/questions', methods=['POST'])
@require_admin
def create_question():
    body = request.get_json(silent=True) or {}
    err_msg = _validate_question_payload(body)
    if err_msg:
        return _err(err_msg, 400)

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO problems (title, content, difficulty, tags)
               VALUES (%s, %s, %s, %s)""",
            (body["title"], body["content"], body["difficulty"], body["tags"]),
        )
        new_id = cur.lastrowid
        for tc in body["test_cases"]:
            cur.execute(
                """INSERT INTO test_cases (problem_id, input_data, expected_output, description)
                   VALUES (%s, %s, %s, %s)""",
                (new_id, tc["input"], tc["output"], tc["description"]),
            )
        conn.commit()
        clear_question_cache()
        return _ok({"id": new_id}, "题目已创建"), 201
    except Exception as e:
        if conn:
            conn.rollback()
        log.exception("create_question 失败")
        return _err(f"数据库错误: {e}", 500)
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/quizbank/update', methods=['POST'])
@require_admin
def upsert_question_compat():
    """Compatibility endpoint documented for administrator question upserts."""
    body = request.get_json(silent=True) or {}
    question_id = body.get("id") or body.get("question_id")
    if question_id not in (None, ""):
        try:
            return update_question(int(question_id))
        except (TypeError, ValueError):
            return _err("id 必须为整数", 400)
    return create_question()


@admin_bp.route('/api/admin/questions/<int:qid>', methods=['PUT'])
@admin_bp.route('/api/quizbank/<int:qid>', methods=['PUT'])
@require_admin
def update_question(qid: int):
    body = request.get_json(silent=True) or {}
    # 更新允许部分字段，所以要兼容"没传的字段保持不变"
    title = body.get("title")
    difficulty = body.get("difficulty")
    tags = body.get("tags")
    content = body.get("content")
    test_cases = body.get("test_cases")  # None 表示不改；[] 表示清空

    if difficulty is not None and difficulty not in VALID_DIFFICULTIES:
        return _err(f"difficulty 必须是 {VALID_DIFFICULTIES} 之一")
    if isinstance(tags, list):
        tags = ",".join(str(t).strip() for t in tags if str(t).strip())

    # 先检查题目的存在性
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM problems WHERE id = %s", (qid,))
        row = cur.fetchone()
        if not row:
            return _err("题目不存在", 404)

        sets = []
        params = []
        if title is not None:
            sets.append("title = %s"); params.append(str(title).strip())
        if difficulty is not None:
            sets.append("difficulty = %s"); params.append(difficulty)
        if tags is not None:
            sets.append("tags = %s"); params.append(str(tags)[:255])
        if content is not None:
            sets.append("content = %s"); params.append(str(content))

        if sets:
            params.append(qid)
            cur.execute(f"UPDATE problems SET {', '.join(sets)} WHERE id = %s", params)

        if test_cases is not None:
            # 全量替换测试用例
            if not isinstance(test_cases, list):
                return _err("test_cases 必须是数组")
            cleaned = []
            for i, tc in enumerate(test_cases):
                if not isinstance(tc, dict):
                    return _err(f"test_cases[{i}] 不是对象")
                inp = tc.get("input") if tc.get("input") is not None else ""
                out = tc.get("output") if tc.get("output") is not None else ""
                if not isinstance(inp, str) or not isinstance(out, str):
                    return _err(f"test_cases[{i}] input/output 必须是字符串")
                cleaned.append((inp, out, (tc.get("description") or "").strip()[:255]))
            cur.execute("DELETE FROM test_cases WHERE problem_id = %s", (qid,))
            for inp, out, desc in cleaned:
                cur.execute(
                    """INSERT INTO test_cases (problem_id, input_data, expected_output, description)
                       VALUES (%s, %s, %s, %s)""",
                    (qid, inp, out, desc),
                )

        conn.commit()
        clear_question_cache()
        return _ok({"id": qid}, "题目已更新")
    except Exception as e:
        if conn:
            conn.rollback()
        log.exception("update_question 失败")
        return _err(f"数据库错误: {e}", 500)
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/admin/questions/<int:qid>', methods=['DELETE'])
@admin_bp.route('/api/quizbank/<int:qid>', methods=['DELETE'])
@require_admin
def delete_question(qid: int):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 先删测试用例 (没有 ON DELETE CASCADE 时兜底)
        cur.execute("DELETE FROM test_cases WHERE problem_id = %s", (qid,))
        cur.execute("DELETE FROM problems WHERE id = %s", (qid,))
        affected = cur.rowcount
        conn.commit()
        clear_question_cache()
        if affected == 0:
            return _err("题目不存在", 404)
        return _ok({"id": qid}, "题目已删除")
    except Exception as e:
        if conn:
            conn.rollback()
        log.exception("delete_question 失败")
        return _err(f"数据库错误: {e}", 500)
    finally:
        if conn:
            conn.close()


# =========================================================================
# 3. 操作记录审计（全用户合表）
# =========================================================================
@admin_bp.route('/api/admin/audit_logs', methods=['GET'])
@require_admin
def list_audit_logs():
    """
    按时间倒序返回"功能使用 + 文件上传 + API 响应"三种记录（所有用户混合）。
    Query args:
      - user_id:  只看某个用户
      - type:     function | upload | api_response
      - limit:    条数，默认 500
    """
    user_id = request.args.get('user_id')
    type_filter = (request.args.get('type') or '').strip().lower()
    limit = int(request.args.get('limit', 500) or 500)
    limit = max(1, min(limit, 3000))

    sql_parts = []
    params = []
    try:
        user_id_i = int(user_id) if user_id else None
    except (TypeError, ValueError):
        user_id_i = None

    # functions_used
    if type_filter in ('', 'function'):
        if user_id_i:
            sql_parts.append(
                "SELECT id, 'function' AS record_type, user_id, function_name AS name, "
                "NULL AS extra, timestamp FROM functions_used WHERE user_id = %s"
            )
            params.append(user_id_i)
        else:
            sql_parts.append(
                "SELECT id, 'function' AS record_type, user_id, function_name AS name, "
                "NULL AS extra, timestamp FROM functions_used"
            )

    # user_uploads
    if type_filter in ('', 'upload'):
        if user_id_i:
            sql_parts.append(
                "SELECT id, 'upload' AS record_type, user_id, file_name AS name, "
                "CONCAT('type=', file_type) AS extra, upload_time AS timestamp "
                "FROM user_uploads WHERE user_id = %s"
            )
            params.append(user_id_i)
        else:
            sql_parts.append(
                "SELECT id, 'upload' AS record_type, user_id, file_name AS name, "
                "CONCAT('type=', file_type) AS extra, upload_time AS timestamp "
                "FROM user_uploads"
            )

    # api_responses — 联 user_uploads 取 user_id
    if type_filter in ('', 'api_response'):
        base_sql = (
            "SELECT ar.id, 'api_response' AS record_type, u.user_id, ar.response_file_name AS name, "
            "LEFT(ar.response_file_content, 200) AS extra, ar.timestamp AS timestamp "
            "FROM api_responses ar JOIN user_uploads u ON u.id = ar.user_upload_id"
        )
        if user_id_i:
            sql_parts.append(base_sql + " WHERE u.user_id = %s")
            params.append(user_id_i)
        else:
            sql_parts.append(base_sql)

    if not sql_parts:
        return _ok({"total": 0, "items": []})

    union_sql = "\nUNION ALL\n".join(sql_parts) + " ORDER BY timestamp DESC LIMIT %s"
    params.append(limit)

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(union_sql, params)
        rows = fetch_dict(cur)
        items = []
        for r in rows:
            ts = r.get("timestamp")
            items.append({
                "id": r.get("id"),
                "record_type": r.get("record_type"),
                "user_id": r.get("user_id"),
                "name": r.get("name"),
                "extra": r.get("extra"),
                "timestamp": str(ts) if ts else None,
            })
        return _ok({"total": len(items), "items": items})
    except Exception as e:
        log.exception("list_audit_logs 失败")
        return _err(f"数据库错误: {e}", 500)
    finally:
        if conn:
            conn.close()


# =========================================================================
# 4. 概览（仪表盘用）
# =========================================================================
@admin_bp.route('/api/admin/summary', methods=['GET'])
@require_admin
def admin_summary():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        stats = {}
        for table in ('users', 'problems', 'test_cases', 'functions_used', 'user_uploads', 'answer_records'):
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                row = cur.fetchone()
                stats[table] = int(row[0]) if row and row[0] is not None else 0
            except Exception as e:
                log.warning("统计表 %s 失败: %s", table, e)
                stats[table] = 0
        return _ok(stats)
    except Exception as e:
        return _err(f"数据库错误: {e}", 500)
    finally:
        if conn:
            conn.close()
