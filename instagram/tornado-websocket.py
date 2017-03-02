import signal
import time

from collections import defaultdict
from urllib.parse import urlparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_command_line, options
from tornado.web import Application
from tornado.websocket import WebSocketHandler, WebSocketClosedError

define('debug', default=False, type=bool, help='Run in debug mode')
define('port', default=8080, type=int, help='Server post')
define('allowed_hosts', default='localhost:8000', multiple=True,
       help="Allowed hosts for cross domain connections")


class CommentHandler(WebSocketHandler):
    def check_origin(self, origin):
        allowed = super().check_origin(origin)
        parsed = urlparse(origin.lower())
        matched = any(parsed.netloc == host for host in options.allowed_hosts)
        return options.debug or allowed or matched

    def open(self, comment):
        self.comment = comment
        self.application.add_subscriber(self.comment, self)

    def on_message(self, message):
        self.application.broadcast(message, channel=self.comment, sender=self)

    def on_close(self):
        self.application.remove_subscriber(self.comment, self)


class InsApplication(Application):

    def __init__(self, **kwargs):
        routes = [
            (r'/(?P<comment>\d+)', CommentHandler),
        ]
        super().__init__(routes, **kwargs)
        self.subscriptions = defaultdict(list)

    def add_subscriber(self, channel, subscriber):
        self.subscriptions[channel].append(subscriber)

    def remove_subscriber(self, channel, subscriber):
        self.subscriptions[channel].remove(subscriber)

    def get_subscriber(self, channel):
        return self.subscriptions[channel]

    def broadcast(self, message, channel=None, sender=None):
        if channel is None:
            for c in self.subscriptions.keys():
                self.broadcast(message, channel=c, sender=sender)

        else:
            peers = self.get_subscriber(channel)
            for peer in peers:
                if peer != sender:
                    try:
                        peer.write_message(message)
                    except WebSocketClosedError:
                        self.remove_subscriber(channel, peer)


def shutdown(server):
    ioloop = IOLoop.instance()
    server.stop()

    def finalize():
        ioloop.stop()

    ioloop.add_timeout(time.time() + 1.5, finalize)


if __name__ == "__main__":
    parse_command_line()
    application = InsApplication(debug=options.debug)
    server = HTTPServer(application)
    server.listen(options.port)
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown(server))
    IOLoop.instance().start()