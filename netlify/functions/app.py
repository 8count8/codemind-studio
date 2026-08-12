"""
Netlify Function - 极简测试版
不依赖任何 Flask 或项目模块
"""
import json
import os
import sys

def handler(event, context):
    """最小化的 Function handler - 测试 Netlify Functions 是否工作"""
    path = event.get('rawPath') or event.get('path', '/')
    
    # 基本信息
    info = {
        "function": "app",
        "status": "working",
        "path": path,
        "rawPath": event.get('rawPath', ''),
        "eventPath": event.get('path', ''),
        "httpMethod": event.get('httpMethod', ''),
    }
    
    # 如果是 /health，返回更多诊断信息
    if path == '/health' or path == '/.netlify/functions/app':
        import socket
        
        # 邮件环境变量
        email_vars = {
            "EMAIL_TYPE": os.getenv("EMAIL_TYPE", "NOT_SET"),
            "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS", "NOT_SET"),
            "EMAIL_PASSWORD": "SET" if os.getenv("EMAIL_PASSWORD") else "NOT_SET",
        }
        info["email_env"] = email_vars
        
        # SMTP 连接测试
        try:
            socket.setdefaulttimeout(3)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("smtp.163.com", 465))
            s.close()
            info["smtp"] = "ok"
        except Exception as e:
            info["smtp"] = f"failed: {str(e)}"
        
        # 数据库测试
        try:
            import psycopg2
            conn = psycopg2.connect(os.getenv("DATABASE_URL", ""))
            conn.close()
            info["database"] = "ok"
        except ImportError:
            info["database"] = "skipped (no psycopg2)"
        except Exception as e:
            info["database"] = f"failed: {str(e)}"
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(info)
    }
