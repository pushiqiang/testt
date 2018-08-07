# -*- coding: utf-8 -*-

import asyncio
import uvloop
import aiohttp

from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket

import functools
import json

APPLICATION_JSON = 'application/json'

DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 30


# loop = uvloop.new_event_loop()
# loop = asyncio.get_event_loop()


class WebSocketClient(object):
    """Base for web socket clients.
    """

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

    def __init__(self, io_loop=None):
        self._io_loop = io_loop
        self._session = aiohttp.ClientSession(loop=self._io_loop)
        self._ws_connection = None
        self._connect_status = self.DISCONNECTED

    def connect(self, url, auto_reconnet=True, reconnet_interval=10):
        self.ws_url = url
        self.auto_reconnet = auto_reconnet
        self.reconnect_interval = reconnet_interval
        self._connect_status = self.CONNECTING

        headers = {'Content-Type': APPLICATION_JSON}

        ws_conn = self._session.ws_connect(url, headers=headers)
        ws_conn.add_done_callback(self._connect_callback)

    async def send(self, data):
        """Send message to the server
        :param str data: message.
        """

        if self._ws_connection:
            print('Send message=%s' % data)
            await self._ws_connection.send_json(data)

    def close(self, reason=''):
        """Close connection.
        """

        if self._connect_status != self.DISCONNECTED:
            self._connect_status = self.DISCONNECTED
            self._session and self._session.close()
            self._session = None
            self._ws_connection and self._ws_connection.close()
            self._ws_connection = None
            self.on_connection_close(reason)

    def _connect_callback(self, future):
        if future.exception() is None:
            self._connect_status = self.CONNECTED
            self._ws_connection = future.result()
            self.on_connection_success()
            await self._read_messages()
        else:
            self.close(future.exception())

    @property
    def is_connected(self):
        return self._ws_connection is not None

    async def _read_messages(self):
        while True:
            msg = await self._ws_connection.receive()
            if msg is None:
                self.close()
                break

            self.on_message(msg)

    def on_message(self, msg):
        print '[%s]on_message msg=%s' % (id(self), msg)
        self._io_loop.call_later(self.heartbeat_interval_in_secs,
                                 functools.partial(self.send, self.hb_msg))

    def on_connection_success(self):
        print('Connected!')
        self.send(self.msg)

    def on_connection_close(self, reason):
        print('Connection closed reason=%s' % (reason,))
        self.reconnect()

    def reconnect(self):
        print 'reconnect'
        if not self.is_connected() and self.auto_reconnet:
            self._io_loop.call_later(self.reconnect_interval, .connect, self.ws_url)

