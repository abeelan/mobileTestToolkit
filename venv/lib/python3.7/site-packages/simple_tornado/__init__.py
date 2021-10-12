# coding: utf-8
#

__all__ = ['listen_and_serve']

import argparse
import os
import signal
import socket
import sys
from typing import Optional, Union

import tornado.httpserver
import tornado.web
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.log import enable_pretty_logging


def _is_port_listening(port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('localhost', port))
        return False
    except OSError:
        return True
    finally:
        s.close()


class CorsMixin:
    def initialize(self):
        self.set_header('Connection', 'close')
        self.request.connection.no_keep_alive = True

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()


def patch_for_windows():
    if sys.platform == 'win32':
        # add perodic call to let ctrl-c work
        if sys.version_info[:2] == (3, 8):
            import asyncio
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())

        def _signal_handler(signum, frame):
            print('Signal Interrupt catched, exiting...')
            IOLoop.instance().stop()

        # must put after set_event_loop_policy
        signal.signal(signal.SIGINT, _signal_handler)
        PeriodicCallback(lambda: None, 100).start()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--addr",
                        type=str,
                        default=":5000",
                        help="listen port [default :5000]")
    return parser.parse_args()


def listen_and_serve(addr: Union[str, int],
                     handler: Union[tornado.web.Application, list],
                     debug: Optional[bool] = None,
                     root_dir: str = ".",
                     xheaders: bool = False,
                     ioloop_start: bool = True):
    """
    Listen and serve

    Usage example:
        listen_and_serve(":5000", [
            (r"/", MainHandler),
            (r"/simple", SimpleHandler),
        ])
    """
    if isinstance(addr, int):
        port = addr
    else:
        host, port = addr.split(":", 1)
        port = int(port)

    if debug is None:
        debug = (os.getenv("DEBUG") == "true")

    #if _is_port_listening(port):
    #    sys.exit("[simple_tornado] Warning, localhost:{} is already listening".format(port))

    settings = {
        'static_path': os.path.join(root_dir, 'static'),
        'template_path': os.path.join(root_dir, 'templates'),
        'debug': debug,
    }

    if isinstance(handler, list):
        handler = tornado.web.Application(handler, debug=debug)

    if xheaders:
        http_server = tornado.httpserver.HTTPServer(handler, xheaders=True)
        http_server.listen(port)
    else:
        handler.listen(port)

    if debug:
        enable_pretty_logging()

    #if sys.platform == 'win32' and sys.version_info[:2] == (3, 8):
    #    import asyncio
    #    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if ioloop_start:
        try:
            print("[simple_tornado] Listening on {}".format(addr))
            IOLoop.instance().start()
        except KeyboardInterrupt:
            IOLoop.instance().stop()
