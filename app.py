import config
from app import create_app
from flasgger import Swagger

app = create_app(config=config.DevelopmentConfig)

swagger = None
if config.HOST is None:
    swagger = Swagger(app)
else:
    swagger = Swagger(
        app,
        config=config.API_Docs_Config.swagger_config,
        template=config.API_Docs_Config.SWAGGER_TEMPLATE)

if __name__ == '__main__':
    app.run("0.0.0.0", 5000)
