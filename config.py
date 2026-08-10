import os

# 若开启反向代理将此改为部署地址
HOST = None


class Config:
    """ 基础配置类 """

    # 设置密钥和数据库连接
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456'
    # 设置数据库连接(mysql)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or '127.0.0.1:3306/CMS'
    # 关闭跟踪数据库的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    # 白名单：不需要登录的路由/蓝本
    WHITELIST_ROUTES = []
    WHITELIST_BLUEPRINTS = ["auth", "main", "static", None]


class API_Docs_Config:
    # Swagger 配置
    # 配置Swagger文档的生成和展示
    swagger_config = {
        "headers": [],  # 自定义请求头
        "specs": [
            {
                "endpoint": 'apispec_1',  # API规范的端点名称
                "route": '/apispec_1.json',  # API规范的JSON文件路径
                "rule_filter": lambda rule: True,  # 过滤规则，返回True表示不过滤
                "model_filter": lambda tag: True,  # 过滤模型，返回True表示不过滤
            }
        ],
        "static_url_path": "/flasgger_static",  # 静态文件的URL路径
        "swagger_ui": True,  # 是否启用Swagger UI
        "specs_route": "/apidocs/",  # Swagger UI的访问路径
        "host": HOST  # API文档的主机名
    }

    # Swagger模板配置
    # 定义Swagger文档的协议和主机名
    SWAGGER_TEMPLATE = {
        "schemes": ["http"],  # 支持的协议
        "host": HOST  # API文档的主机名
    }


class DevelopmentConfig(Config, API_Docs_Config):
    """ 开发环境配置 """
    DEBUG = True
    WHITELIST_BLUEPRINTS = ["auth", "main", "static", None, "api_doc", "answerpad", "flasgger", "code_review",
                            "quizbank", "favorites", "answer", "user_api", "ai_question", "profile", "ability_matrix"]


class TestingConfig(Config):
    """ 测试环境配置 """
    TESTING = True
    # 使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """ 生产环境配置 """
    DEBUG = False
    # 使用生产环境数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
