import os
from wareweb.servlet import Servlet
from wareweb.dispatch import ActionDispatch
from paste import httpexceptions
from paste.url import URL
from Cheetah.Template import Template

template_dir = os.path.join(os.path.dirname(__file__),
                            'templates')

base_filename = os.path.join(template_dir, 'standard.tmpl')

class SitePage(Servlet):

    dispatcher = ActionDispatch()

    def awake(self):
        Servlet.awake(self, call_setup=False)
        env = self.environ
        if env.get('REMOTE_ADDR', '127.0.0.1') != '127.0.0.1':
            raise httpexceptions.HTTPForbidden
        if env['wsgi.multiprocess']: # or env['wsgi.run_once']:
            raise httpexceptions.HTTPServerError(
                'This application can only be run under single-process '
                '(typically multi-threaded) long-running servers')
        self.app_url = URL(env['htconsole.base_url'])
        self.static_url = self.app_url('static')
        self.template = self.__class__.__name__
        self.setup()

    def respond(self):
        if self.template is None:
            return
        standard_template = Template.compile(file=base_filename)
        fn = os.path.join(template_dir, self.template+'.tmpl')
        template = standard_template.subclass(file=fn)
        inst = template(namespaces=[self.__dict__, self])
        self.write(str(inst))
