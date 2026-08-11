"""
数据库模块 — Supabase PostgreSQL（Netlify 部署唯一数据源）

本模块作为统一入口，从子模块重导出所有公共 API：
- db_constants: 常量 (VALID_DIFFICULTIES, USE_POSTGRESQL)
- db_connection: 连接管理 (get_db_connection, init_database, get_create_statements)
- db_utils: 游标工具 (fetch_dict, fetch_one_dict, get_current_timestamp)
- db_converters: 格式转换 (dict_to_markdown)

通过环境变量 DATABASE_URL 连接 Supabase PostgreSQL。
"""

# --- 常量 ---
from app.models.db_constants import (
    USE_POSTGRESQL,
    VALID_DIFFICULTIES,
)

# --- 连接管理 ---
from app.models.db_connection import (
    get_db_connection,
    init_database,
    get_create_statements,
)

# --- 游标工具 ---
from app.models.db_utils import (
    fetch_dict,
    fetch_one_dict,
    get_current_timestamp,
)

# --- 格式转换 ---
from app.models.db_converters import (
    dict_to_markdown,
)

# 为兼容旧代码保留的 json 导入（部分模块通过 db.py 间接使用）
import json

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    init_database()