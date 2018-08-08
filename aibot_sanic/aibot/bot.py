# -*- coding: utf-8 -*-

import uuid

import asyncio
import aiohttp

from aiohttp.client_exceptions import ClientError

from functools import partial


APPLICATION_JSON = 'application/json'

DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 30


class AIBot(object):
    """Base for web socket clients.
    """

    # ws status
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

    # bot status
    PREPARE = 'prepare'
    PLAYING = 'playing'


    def __init__(self, io_loop=None):
        self.key = str(uuid.uuid4())
        self.status = self.PREPARE
        
        self._io_loop = io_loop
        self._session = aiohttp.ClientSession(loop=self._io_loop)
        self._ws_connection = None
        self._ws_connect_status = self.DISCONNECTED
        
    async def ws_connect(self, url, headers=None, auto_reconnet=True, reconnet_interval=10):
        self.ws_url = url
        self.auto_reconnet = auto_reconnet
        self.reconnect_interval = reconnet_interval
        self._ws_connect_status = self.CONNECTING

        headers = headers or {'Content-Type': APPLICATION_JSON}

        try:
            self._ws_connection = await self._session.ws_connect(url, headers=headers)
        except ClientError as e:
            print('Error: %s' % e)
            await self.ws_close()
        else:
            self._ws_connect_status = self.CONNECTED

    async def ws_send(self, data):
        """Send message to the server
        :param str data: message.
        """

        if self._ws_connection:
            await self._ws_connection.send_json(data)

    async def ws_close(self, reason=''):
        """Close connection.
        """
        if self._ws_connect_status != self.DISCONNECTED:
            self._ws_connection and await self._ws_connection.close()
            self._ws_connection = None

            self._session and await self._session.close()
            self._session = None
            self._ws_connect_status = self.DISCONNECTED

    @property
    def is_ws_connected(self):
        return self._ws_connection is not None

    async def ws_reconnect(self):
        """断开重连"""
        if not self.is_ws_connected and self.auto_reconnet:
            self._io_loop.call_later(self.reconnect_interval, partial(self.ws_connect, self.ws_url))

    async def receive(self):
        return await self._ws_connection.receive()

    async def start(self):
        """开始游戏"""
        ws_url = 'ws://echo.websocket.org'
        await self.ws_connect(ws_url)
        asyncio.ensure_future(self.playing())

    async def action_future(self, task):
        """响应动作注册后立即返回"""
        asyncio.ensure_future(task)
    
    async def playing(self):
        """bot逻辑代码"""

        # 游戏逻辑
        # 加入房间
        # 叫地主
        # 进行游戏

        self.status = self.PLAYING

        print('Started game...')
        hb_msg = {'type': 'hb'}  # hearbeat
        await self.ws_send(hb_msg)

        while(True):
            msg = await self.receive()
            if msg.type == aiohttp.WSMsgType.CLOSED:
                print('Bot [{}] closed'.format(self.key))
                return
            elif msg.type == aiohttp.WSMsgType.ERROR:
                msg = None

            await self.ws_send(hb_msg)
            print('Bot [{}]: {}'.format(self.key, msg))
