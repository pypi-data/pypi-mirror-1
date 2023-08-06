# -*- coding: utf-8 -*-
from wsgioauth.mock import filter_factory, app_factory

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    app = app_factory()
    server = make_server('localhost', 8080, app)
    server.serve_forever()
