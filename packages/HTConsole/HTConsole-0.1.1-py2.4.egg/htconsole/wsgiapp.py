import os
from paste.deploy.config import ConfigMiddleware
from wareweb.wsgiapp import make_wareweb_app

def make_app(
    global_conf,
    **kw):
    # This is a WSGI application:
    app = make_wareweb_app(
        global_conf,
        package_name='htconsole',
        root_path=os.path.dirname(__file__),
        **kw)
    return app

