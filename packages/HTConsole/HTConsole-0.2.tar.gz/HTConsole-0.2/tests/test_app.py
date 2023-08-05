from paste.fixture import TestApp
from htconsole.wsgiapp import make_app

wsgi_app = make_app({})
app = TestApp(wsgi_app)

def test_app():
    app.get('/')
    
