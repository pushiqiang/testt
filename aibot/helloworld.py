import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

from ws_utils import RTCWebSocketClient


define("port", default=8888, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        io_loop = tornado.ioloop.IOLoop.current()

        client = RTCWebSocketClient(io_loop)
        # ws_url = 'ws://127.0.0.1:8090/ws'
        ws_url = 'ws://echo.websocket.org'
        client.connect(ws_url, auto_reconnet=True, reconnet_interval=10)

        self.write("Hello, world")


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
