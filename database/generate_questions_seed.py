"""校验 250_questions.json 并生成可重复执行的 MySQL 题库种子脚本。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


VALID_DIFFICULTIES = {"简单", "中等", "困难"}


def _sql(value: object) -> str:
    """生成 MySQL UTF-8 字符串字面量。"""
    text = "" if value is None else str(value)
    text = (
        text.replace("\\", "\\\\")
        .replace("'", "''")
        .replace("\0", "\\0")
        .replace("\r", "\\r")
    )
    return f"'{text}'"


def load_and_validate(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 250:
        raise ValueError(f"题库必须恰好包含 250 题，当前为 {len(data) if isinstance(data, list) else '非数组'}")

    seen: set[str] = set()
    for index, question in enumerate(data, 1):
        if not isinstance(question, dict):
            raise ValueError(f"第 {index} 题不是对象")
        title = question.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"第 {index} 题缺少 title")
        if title in seen:
            raise ValueError(f"题目标题重复: {title}")
        seen.add(title)
        if question.get("difficulty") not in VALID_DIFFICULTIES:
            raise ValueError(f"{title}: difficulty 必须是 {sorted(VALID_DIFFICULTIES)} 之一")
        if not isinstance(question.get("content"), str) or not question["content"].strip():
            raise ValueError(f"{title}: content 不能为空")
        if not isinstance(question.get("tags"), list):
            raise ValueError(f"{title}: tags 必须是数组")
        cases = question.get("test_cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError(f"{title}: 至少需要一个 test_case")
        for case_index, case in enumerate(cases, 1):
            if not isinstance(case, dict):
                raise ValueError(f"{title}: 第 {case_index} 个测试用例不是对象")
            if not isinstance(case.get("input", ""), str) or not isinstance(case.get("output", ""), str):
                raise ValueError(f"{title}: 第 {case_index} 个测试用例 input/output 必须是字符串")
    return data


def render_sql(questions: list[dict], source_name: str) -> str:
    case_count = sum(len(q["test_cases"]) for q in questions)
    lines = [
        "-- 此文件由 database/generate_questions_seed.py 自动生成，请勿手工编辑。",
        f"-- 来源: {source_name}; 题目: {len(questions)}; 测试用例: {case_count}",
        "SET NAMES utf8mb4;",
        "SET @has_description = (SELECT COUNT(*) FROM information_schema.COLUMNS",
        "  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'test_cases' AND COLUMN_NAME = 'description');",
        "SET @migration_sql = IF(@has_description = 0,",
        "  'ALTER TABLE test_cases ADD COLUMN description VARCHAR(255) DEFAULT ''''', 'SELECT 1');",
        "PREPARE migration_stmt FROM @migration_sql;",
        "EXECUTE migration_stmt;",
        "DEALLOCATE PREPARE migration_stmt;",
        "START TRANSACTION;",
        "DELETE FROM test_cases;",
        "DELETE FROM problems;",
        "ALTER TABLE test_cases AUTO_INCREMENT = 1;",
        "ALTER TABLE problems AUTO_INCREMENT = 1;",
        "",
    ]
    for question in questions:
        tags = json.dumps(question["tags"], ensure_ascii=False, separators=(",", ":"))
        lines.extend([
            "INSERT INTO problems (title, content, difficulty, tags) VALUES (",
            f"  {_sql(question['title'])}, {_sql(question['content'])},",
            f"  {_sql(question['difficulty'])}, {_sql(tags)}",
            ");",
            "SET @problem_id = LAST_INSERT_ID();",
        ])
        for case in question["test_cases"]:
            lines.extend([
                "INSERT INTO test_cases (problem_id, input_data, expected_output, description) VALUES (",
                f"  @problem_id, {_sql(case.get('input', ''))}, {_sql(case.get('output', ''))},",
                f"  {_sql(case.get('description', ''))}",
                ");",
            ])
        lines.append("")
    lines.extend([
        "COMMIT;",
        "SELECT COUNT(*) AS question_count FROM problems;",
        "SELECT COUNT(*) AS test_case_count FROM test_cases;",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent
    parser.add_argument("--input", type=Path, default=base / "250_questions.json")
    parser.add_argument("--output", type=Path, default=base / "250_questions_seed.sql")
    parser.add_argument("--check", action="store_true", help="verify that output is current without rewriting it")
    args = parser.parse_args()

    questions = load_and_validate(args.input)
    rendered = render_sql(questions, args.input.name)
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"题库 SQL 已过期，请重新运行: {args.output}")
        cases = sum(len(q["test_cases"]) for q in questions)
        print(f"题库 SQL 已同步: {len(questions)} 题, {cases} 个测试用例")
        return
    args.output.write_text(rendered, encoding="utf-8", newline="\n")
    cases = sum(len(q["test_cases"]) for q in questions)
    print(f"已生成 {args.output}: {len(questions)} 题, {cases} 个测试用例")


if __name__ == "__main__":
    main()
