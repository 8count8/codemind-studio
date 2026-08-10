# 数据库连接测试脚本
# 使用方法: python test_db_connection.py

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_sqlite():
    """测试 SQLite 连接"""
    print("=" * 50)
    print("测试 1: SQLite 本地连接")
    print("=" * 50)
    
    try:
        import sqlite3
        db_path = os.environ.get('DATABASE_PATH', 'codemind.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建测试表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入测试数据
        cursor.execute("INSERT INTO test_connection (message) VALUES (?)", ("SQLite 连接测试成功！",))
        conn.commit()
        
        # 查询数据
        cursor.execute("SELECT * FROM test_connection ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        print(f"✅ SQLite 连接成功！")
        print(f"   数据库: {db_path}")
        print(f"   测试记录: {row[1]}")
        
        # 清理测试表
        cursor.execute("DROP TABLE test_connection")
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ SQLite 连接失败: {e}")
        return False


def test_postgresql():
    """测试 PostgreSQL (Supabase) 连接"""
    print("\n" + "=" * 50)
    print("测试 2: PostgreSQL (Supabase) 连接")
    print("=" * 50)
    
    database_url = os.environ.get('DATABASE_URL', '')
    
    if not database_url:
        print("⚠️  未设置 DATABASE_URL 环境变量，跳过 PostgreSQL 测试")
        print("   请在 .env 文件或环境变量中设置 DATABASE_URL")
        print("   格式: postgresql://postgres:密码@host:5432/postgres")
        return None
    
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 创建测试表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入测试数据
        cursor.execute("INSERT INTO test_connection (message) VALUES (%s)", ("PostgreSQL 连接测试成功！",))
        conn.commit()
        
        # 查询数据
        cursor.execute("SELECT * FROM test_connection ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        print(f"✅ PostgreSQL 连接成功！")
        print(f"   数据库: Supabase")
        print(f"   测试记录: {row[1]}")
        
        # 清理测试表
        cursor.execute("DROP TABLE test_connection")
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL 连接失败: {e}")
        return False


def init_database():
    """初始化完整数据库"""
    print("\n" + "=" * 50)
    print("初始化数据库表结构")
    print("=" * 50)
    
    try:
        from app.models.db import init_database as init_db
        result = init_db()
        if result:
            print("✅ 数据库初始化成功！")
        else:
            print("❌ 数据库初始化失败")
        return result
    except Exception as e:
        print(f"❌ 数据库初始化异常: {e}")
        return False


def main():
    print("\n" + "🎯 CodeMind Studio 数据库连接测试" + "\n")
    
    results = {}
    
    # 测试 SQLite
    results['sqlite'] = test_sqlite()
    
    # 测试 PostgreSQL
    results['postgresql'] = test_postgresql()
    
    # 初始化数据库
    init_db = input("\n是否初始化完整数据库表结构？(y/n): ").strip().lower()
    if init_db == 'y':
        init_database()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for db_type, success in results.items():
        if success is None:
            status = "⚠️  跳过"
        elif success:
            status = "✅ 通过"
        else:
            status = "❌ 失败"
        print(f"   {db_type}: {status}")
    
    print("\n" + "💡 提示:")
    print("   - 本地开发使用 SQLite（默认）")
    print("   - 生产部署使用 PostgreSQL (Supabase)")
    print("   - 设置 DATABASE_URL 环境变量即可切换到 PostgreSQL")
    print()


if __name__ == '__main__':
    main()