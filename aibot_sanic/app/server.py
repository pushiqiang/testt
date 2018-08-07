"""
sanic server
"""

from app import app
from views.routers import blueprint


app.blueprint(blueprint)


def run_server():
    """启动服务器
    根据启动参数加载配置, 如果没有相应的配置文件直接抛出错误
    """
    app.run(
        host=app.config.HOST,
        port=app.config.PORT,
        workers=app.config.WORKERS,
        debug=app.config.DEBUG)
