# 简单测试 Function - 诊断 Netlify Functions 是否正常工作
import json

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'ok',
            'message': 'Netlify Function is working!',
            'path': event.get('path', ''),
            'rawPath': event.get('rawPath', ''),
            'httpMethod': event.get('httpMethod', ''),
            'headers': dict(event.get('headers', {})),
        })
    }
