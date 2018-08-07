"""
路由 http 请求
"""
from sanic.blueprints import Blueprint

from views import views

blueprint = Blueprint('example', version='1')

blueprint.add_route(views.ExampleView.as_view(), '/example', methods=['POST'])
