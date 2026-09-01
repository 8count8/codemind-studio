"""Learning dashboard, submission history and favorite-topic persistence."""

import json
import threading
from datetime import date, timedelta

from app.models.db import get_db_connection, fetch_dict, fetch_one_dict


_schema_lock = threading.Lock()
_schema_ready = False


def _ensure_extended_schema(connection):
    """Apply backwards-compatible migrations for an existing database volume."""
    global _schema_ready
    if _schema_ready:
        return
    with _schema_lock:
        if _schema_ready:
            return
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorite_topics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(80) NOT NULL,
                description VARCHAR(255) DEFAULT '',
                tags VARCHAR(255) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY idx_favorite_topics_user_name (user_id, name),
                INDEX idx_favorite_topics_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_drafts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                question_id VARCHAR(50) NOT NULL,
                language VARCHAR(30) DEFAULT 'python',
                code LONGTEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY idx_user_drafts_user_question (user_id, question_id),
                INDEX idx_user_drafts_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        migrations = {
            "favorites": {"topic_id": "INT NULL"},
            "answer_records": {
                "language": "VARCHAR(30) DEFAULT 'python'",
                "execution_result": "LONGTEXT",
                "score": "FLOAT DEFAULT 0",
                "run_time_ms": "INT DEFAULT 0",
                "task_id": "VARCHAR(64)",
            },
            "user_uploads": {"file_content": "LONGTEXT"},
        }
        for table, columns in migrations.items():
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            existing = {row[0] for row in cursor.fetchall()}
            for column, ddl in columns.items():
                if column not in existing:
                    cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {ddl}")
        connection.commit()
        _schema_ready = True


def save_submission(user_id, question_id, language, code, run_result, task_id=None):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        total = int((run_result or {}).get("total_cases") or 0)
        passed = int((run_result or {}).get("passed_cases") or 0)
        is_correct = int(total > 0 and passed == total)
        score = round((passed / total * 100) if total else 0, 2)
        seconds = sum(float(item.get("run_time") or 0) for item in (run_result or {}).get("results", []))
        cursor.execute("""
            INSERT INTO answer_records
                (user_id, question_id, user_answer, is_correct, time_spent,
                 language, execution_result, score, run_time_ms, task_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, str(question_id or ""), code, is_correct, None, language,
            json.dumps(run_result or {}, ensure_ascii=False), score,
            int(seconds * 1000), task_id,
        ))
        connection.commit()
        return {"id": cursor.lastrowid, "is_correct": bool(is_correct), "score": score}
    finally:
        connection.close()


def get_dashboard_summary(user_id):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
              (SELECT COUNT(DISTINCT question_id) FROM answer_records WHERE user_id=%s) AS answers,
              (SELECT COUNT(*) FROM answer_records WHERE user_id=%s) AS submissions,
              (SELECT COUNT(*) FROM favorites WHERE user_id=%s) AS favorites,
              (SELECT COUNT(*) FROM ability_submissions WHERE user_id=%s) AS evaluations
        """, (user_id, user_id, user_id, user_id))
        stats = fetch_one_dict(cursor) or {}
        cursor.execute("""
            SELECT syntax_score, algorithm_score, project_score, debug_score,
                   security_score, updated_at
            FROM ability_matrix WHERE user_id=%s
        """, (user_id,))
        ability = fetch_one_dict(cursor) or {}
        cursor.execute("""
            SELECT ar.question_id, p.title, ar.language, ar.created_at
            FROM answer_records ar
            LEFT JOIN problems p ON p.id = CAST(ar.question_id AS UNSIGNED)
            WHERE ar.user_id=%s ORDER BY ar.created_at DESC LIMIT 1
        """, (user_id,))
        recent = fetch_one_dict(cursor)
        cursor.execute("""
            SELECT DISTINCT activity_date FROM (
              SELECT DATE(created_at) AS activity_date FROM answer_records WHERE user_id=%s
              UNION
              SELECT DATE(created_at) AS activity_date FROM ability_submissions WHERE user_id=%s
            ) activity ORDER BY activity_date DESC
        """, (user_id, user_id))
        activity_dates = []
        for row in cursor.fetchall():
            value = row[0]
            if hasattr(value, "date"):
                value = value.date()
            if isinstance(value, str):
                value = date.fromisoformat(value[:10])
            activity_dates.append(value)
        streak = 0
        expected = date.today()
        if activity_dates and activity_dates[0] == expected - timedelta(days=1):
            expected -= timedelta(days=1)
        for value in activity_dates:
            if value == expected:
                streak += 1
                expected -= timedelta(days=1)
            elif value < expected:
                break
        normalized_stats = {key: int(stats.get(key) or 0) for key in ("answers", "submissions", "favorites", "evaluations")}
        return {
            "stats": normalized_stats,
            "streak_days": streak,
            "ability": ability,
            "recent_practice": recent,
            "total_questions_answered": normalized_stats["answers"],
            "total_submissions": normalized_stats["submissions"],
            "favorites_count": normalized_stats["favorites"],
            "ability_snapshot": ability,
            "recent_activity": recent,
        }
    finally:
        connection.close()


def get_submission_history(user_id, filters=None):
    filters = filters or {}
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        where = ["ar.user_id=%s"]
        params = [user_id]
        if filters.get("result") in ("passed", "failed"):
            where.append("ar.is_correct=%s")
            params.append(1 if filters["result"] == "passed" else 0)
        if filters.get("difficulty"):
            where.append("p.difficulty=%s")
            params.append(filters["difficulty"])
        if filters.get("keyword"):
            where.append("p.title LIKE %s")
            params.append(f"%{filters['keyword']}%")
        if filters.get("question_id") not in (None, ""):
            where.append("ar.question_id=%s")
            params.append(str(filters["question_id"]))
        if filters.get("date_from"):
            where.append("ar.created_at >= %s")
            params.append(filters["date_from"])
        if filters.get("date_to"):
            where.append("ar.created_at < DATE_ADD(%s, INTERVAL 1 DAY)")
            params.append(filters["date_to"])
        page = max(1, int(filters.get("page") or 1))
        per_page = min(50, max(1, int(filters.get("per_page") or 20)))
        where_sql = " AND ".join(where)
        cursor.execute(f"SELECT COUNT(*) AS total FROM answer_records ar LEFT JOIN problems p ON p.id=CAST(ar.question_id AS UNSIGNED) WHERE {where_sql}", tuple(params))
        total = int((fetch_one_dict(cursor) or {}).get("total") or 0)
        cursor.execute(f"""
            SELECT ar.id, ar.question_id, COALESCE(p.title, CONCAT('题目 #', ar.question_id)) AS title,
                   p.difficulty, ar.language, ar.is_correct, ar.score, ar.run_time_ms,
                   ar.task_id, ar.created_at
            FROM answer_records ar
            LEFT JOIN problems p ON p.id=CAST(ar.question_id AS UNSIGNED)
            WHERE {where_sql}
            ORDER BY ar.created_at DESC, ar.id DESC LIMIT %s OFFSET %s
        """, tuple(params + [per_page, (page - 1) * per_page]))
        return {"items": fetch_dict(cursor), "total": total, "page": page, "per_page": per_page}
    finally:
        connection.close()


def get_submission_detail(user_id, submission_id):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ar.id, ar.question_id, COALESCE(p.title, CONCAT('题目 #', ar.question_id)) AS title,
                   p.difficulty, ar.language, ar.user_answer AS code, ar.is_correct,
                   ar.score, ar.run_time_ms, ar.execution_result, ar.task_id, ar.created_at
            FROM answer_records ar
            LEFT JOIN problems p ON p.id=CAST(ar.question_id AS UNSIGNED)
            WHERE ar.user_id=%s AND ar.id=%s
        """, (user_id, submission_id))
        row = fetch_one_dict(cursor)
        if row and row.get("execution_result"):
            try:
                row["execution_result"] = json.loads(row["execution_result"])
            except (TypeError, ValueError):
                pass
        return row
    finally:
        connection.close()


def list_topics(user_id):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.description, t.tags, t.created_at, t.updated_at,
                   COUNT(f.id) AS item_count
            FROM favorite_topics t LEFT JOIN favorites f ON f.topic_id=t.id
            WHERE t.user_id=%s GROUP BY t.id ORDER BY t.updated_at DESC
        """, (user_id,))
        return fetch_dict(cursor)
    finally:
        connection.close()


def create_topic(user_id, name, description="", tags=""):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO favorite_topics (user_id, name, description, tags) VALUES (%s,%s,%s,%s)", (user_id, name, description, tags))
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def update_topic(user_id, topic_id, name, description="", tags=""):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        cursor.execute("UPDATE favorite_topics SET name=%s, description=%s, tags=%s WHERE id=%s AND user_id=%s", (name, description, tags, topic_id, user_id))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def delete_topic(user_id, topic_id):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        cursor.execute("UPDATE favorites SET topic_id=NULL WHERE topic_id=%s AND user_id=%s", (topic_id, user_id))
        cursor.execute("DELETE FROM favorite_topics WHERE id=%s AND user_id=%s", (topic_id, user_id))
        deleted = cursor.rowcount > 0
        connection.commit()
        return deleted
    finally:
        connection.close()


def assign_favorite_topic(user_id, question_id, topic_id):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        if topic_id is not None:
            cursor.execute("SELECT id FROM favorite_topics WHERE id=%s AND user_id=%s", (topic_id, user_id))
            if not cursor.fetchone():
                return False
        cursor.execute("UPDATE favorites SET topic_id=%s WHERE user_id=%s AND question_id=%s", (topic_id, user_id, str(question_id)))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def save_draft(user_id, question_id, language, code):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO user_drafts (user_id, question_id, language, code)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE language=VALUES(language), code=VALUES(code), updated_at=CURRENT_TIMESTAMP
        """, (user_id, str(question_id), language, code))
        connection.commit()
        return True
    finally:
        connection.close()


def get_draft(user_id, question_id):
    connection = get_db_connection()
    try:
        _ensure_extended_schema(connection)
        cursor = connection.cursor()
        cursor.execute("SELECT question_id, language, code, updated_at FROM user_drafts WHERE user_id=%s AND question_id=%s", (user_id, str(question_id)))
        return fetch_one_dict(cursor)
    finally:
        connection.close()
