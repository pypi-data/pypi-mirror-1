import os
from paste import wsgilib

def urlparser_hook(environ):
    if not environ.has_key('htconsole.base_url'):
        environ['htconsole.base_url'] = environ['SCRIPT_NAME']
