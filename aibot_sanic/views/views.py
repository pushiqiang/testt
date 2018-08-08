import uuid

from views.utils import APIBaseView, CreateView, ok_response
from views.serializers import ExampleSerializer

# from bot.ws_utils import WebSocketClient
from aibot.bot import AIBot
from aibot.models import AIBotRecord

from app import app


class AIBotListView(APIBaseView):

    async def post(self, request, *args, **kwargs):
        bot = AIBot(app.loop)
        await bot.start()

        AIBotRecord.add_bot(bot.key, bot)

        # ws_client = WebSocketClient(app.loop)
        # ws_url = 'ws://echo.websocket.org'
        # await ws_client.connect(ws_url)
        # AIBotRecord.add_bot(ws_client.key, ws_client)

        return ok_response({'bot_key': bot.key})

    async def get(self, request, *args, **kwargs):
        result = AIBotRecord.all()

        return ok_response(result)


class AIBotDetailView(APIBaseView):

    async def get(self, request, *args, **kwargs):
        key =  kwargs.get('key')
        result = AIBotRecord.get_bot(key)
        return ok_response(result)

    async def delete(self, request, *args, **kwargs):
        key = kwargs.get('key')
        await AIBotRecord.delete(key)
        return ok_response({})
