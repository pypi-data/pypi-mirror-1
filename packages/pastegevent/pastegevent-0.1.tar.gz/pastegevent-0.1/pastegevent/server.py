"""Entry point for PasteDeploy."""

from gevent import reinit
from gevent.wsgi import WSGIServer
from gevent.monkey import patch_all

__all__ = ["server_factory",
           "server_factory_patched"]

def server_factory(global_conf, host, port):
    port = int(port)
    def serve(app):
        reinit()
        WSGIServer((host, port), app).serve_forever()
    return serve


def server_factory_patched(global_conf, host, port):
    port = int(port)
    def serve(app):
        reinit()
        patch_all(dns=False)
        WSGIServer((host, port), app).serve_forever()
    return serve
