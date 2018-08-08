"""
路由 http 请求
"""
from sanic.blueprints import Blueprint

from views import views

blueprint = Blueprint('bot', version='1')

# create, list bot
blueprint.add_route(
    views.AIBotListView.as_view(),
    '/bots', methods=['GET', 'POST'])

# get，delete bot
blueprint.add_route(
    views.AIBotDetailView.as_view(),
    '/bots/<key:[-a-f0-9]+>/',
    methods=['GET', 'DELETE'])
