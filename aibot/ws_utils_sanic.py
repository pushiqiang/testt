# -*- coding: utf-8 -*-

import uuid

import asyncio
import aiohttp

from functools import partial


APPLICATION_JSON = 'application/json'

DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 30


class WebSocketClient(object):
    """Base for web socket clients.
    """

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

    msg = {'type': 'msg', 'from': 'Frankie',
           'to': 'Peter', 'body': 'Hello, Peter'}
    hb_msg = {'type': 'hb'}  # hearbeat


    def __init__(self, io_loop=None):
        self.key = str(uuid.uuid4())

        self._io_loop = io_loop
        self._session = aiohttp.ClientSession(loop=self._io_loop)
        self._ws_connection = None
        self._connect_status = self.DISCONNECTED

    async def connect(self, url, auto_reconnet=True, reconnet_interval=10):
        self.ws_url = url
        self.auto_reconnet = auto_reconnet
        self.reconnect_interval = reconnet_interval
        self._connect_status = self.CONNECTING

        headers = {'Content-Type': APPLICATION_JSON}

        ws_conn_future = asyncio.ensure_future(self._session.ws_connect(url, headers=headers))
        ws_conn_future.add_done_callback(self._connect_callback)

    def _connect_callback(self, future):
        if future.done():
            self._connect_status = self.CONNECTED
            self._ws_connection = future.result()
            asyncio.ensure_future(self.on_connection_success())
            asyncio.ensure_future(self._read_messages())
        else:
            asyncio.ensure_future(self.close())

    async def send(self, data):
        """Send message to the server
        :param str data: message.
        """

        if self._ws_connection:
            print('Send message=%s' % data)
            await self._ws_connection.send_json(data)

    async def close(self, reason=''):
        """Close connection.
        """
        if self._connect_status != self.DISCONNECTED:
            self._connect_status = self.DISCONNECTED

            self._session and await self._session.close()
            self._session = None

            self._ws_connection and await self._ws_connection.close()
            self._ws_connection = None
            # self.on_connection_close(reason)

    @property
    def is_connected(self):
        return self._ws_connection is not None

    async def _read_messages(self):
        while True:
            msg = await self._ws_connection.receive()
            if msg is None:
                await self.close()
                break

            await self.on_message(msg)

    async def on_message(self, msg):
        print('[{}]on_message msg={}'.format(id(self), msg))
        await self.send(self.hb_msg)

    async def on_connection_success(self):
        print('Connected!')
        await self.send(self.msg)

    async def on_connection_close(self, reason):
        print('Connection closed reason={}'.format(reason))
        await self.reconnect()

    async def reconnect(self):
        """断开重连"""
        if not self.is_connected() and self.auto_reconnet:
            await self._io_loop.call_later(self.reconnect_interval, partial(self.connect, self.ws_url))
