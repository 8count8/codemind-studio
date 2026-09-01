import os

# 若开启反向代理将此改为部署地址
HOST = None


class Config:
    """基础配置类"""

    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456'

    DEBUG = False
    WHITELIST_ROUTES = []
    # ``main`` also owns authenticated pages such as /dashboard, so only
    # authentication/static blueprints are exempted as a whole.
    WHITELIST_BLUEPRINTS = ["auth", "static", None]
    ADMIN_USERNAMES = os.environ.get("ADMIN_USERNAMES", "admin")


class API_Docs_Config:
    """API 文档配置"""
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "host": HOST
    }

    SWAGGER_TEMPLATE = {
        "schemes": ["http"],
        "host": HOST
    }


class DevelopmentConfig(Config, API_Docs_Config):
    """开发环境配置"""
    DEBUG = True
    WHITELIST_BLUEPRINTS = ["auth", "static", None, "api_doc", "flasgger"]


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config, API_Docs_Config):
    """生产环境配置 (云服务器部署)"""
    DEBUG = False
    WHITELIST_BLUEPRINTS = ["auth", "static", None, "api_doc", "flasgger"]
    WHITELIST_ROUTES = [
        "health_check",
        "root",
    ]
