import os
import config
from app import create_app

# 根据环境变量选择配置类
env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    app_config = config.ProductionConfig
else:
    app_config = config.DevelopmentConfig

app = create_app(config=app_config)

# 初始化数据库（自动选择 SQLite 或 PostgreSQL）
try:
    from app.models.db import init_database
    init_database()
except Exception as e:
    print(f"数据库初始化警告: {e}")

# 可选的 Swagger 文档支持
swagger = None
try:
    from flasgger import Swagger
    if config.HOST is None:
        swagger = Swagger(app)
    else:
        swagger = Swagger(
            app,
            config=config.API_Docs_Config.swagger_config,
            template=config.API_Docs_Config.SWAGGER_TEMPLATE)
except ImportError:
    print("警告: flasgger 未安装，API 文档功能不可用")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run("0.0.0.0", port)