import os

# 若开启反向代理将此改为部署地址
HOST = None


class Config:
    """基础配置类"""

    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456'

    DEBUG = False
    WHITELIST_ROUTES = []
    WHITELIST_BLUEPRINTS = ["auth", "main", "static", None]


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
    WHITELIST_BLUEPRINTS = ["auth", "main", "static", None, "api_doc", "answerpad", "flasgger", "code_review",
                            "quizbank", "favorites", "answer", "user_api", "ai_question", "profile", "ability_matrix"]


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True


class ProductionConfig(Config):
    """生产环境配置 (云服务器部署)"""
    DEBUG = False
    WHITELIST_BLUEPRINTS = [
        "auth", "main", "static", None,
        "api_doc", "answerpad", "flasgger", "code_review",
        "quizbank", "favorites", "answer", "user_api",
        "ai_question", "profile", "ability_matrix"
    ]
    WHITELIST_ROUTES = [
        "health_check",
        "root",
    ]
