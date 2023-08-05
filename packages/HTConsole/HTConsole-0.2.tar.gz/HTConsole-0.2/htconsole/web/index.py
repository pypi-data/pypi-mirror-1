import simplejson
import time
import os
import sys
from htconsole.sitepage import SitePage
from htconsole.evalcontext import EvalContext
from htconsole import extrabuiltins

class index(SitePage):

    context = None

    def setup(self):
        if self.context is None:
            self.__class__.context = EvalContext(
                self.make_callback,
                extrabuiltins.ExtraBuiltins(self))
        self.title = 'Console'

    def make_callback(self, callback_id):
        return self.app_url(_action__='callback',
                            _id__=callback_id,
                            __='true')

    def action_default(self):
        self.namespace = []
        for name, value in sorted(
            self.context.namespace.items()):
            if name.startswith('_'):
                continue
            self.namespace.append(
                (name, self.context.html_repr(value)))
        self.saved_console = self.session.get(
            'saved_console', '')

    def action_callback(self):
        fields = self.fields.copy()
        id = fields.pop('_id_')
        del fields['_action_']
        if '_' in fields:
            del fields['_']
        if '__body__' in fields:
            args = simplejson.loads(fields.pop('__body__'))
            fields.update(args)
        result = self.context.do_callback(
            id, **dict(fields))
        self.write(result)
        self.template = None
    
    def action_run(self):
        expr = self.fields['command']
        lines = expr.splitlines(True)
        lines = ['>>> %s' % lines[0]] + [
            '... %s' % l for l in lines[1:]]
        sys.stdout.write(''.join(lines))
        if not expr.endswith('\n'):
            expr += '\n'
        response = self.context.exec_expr_response(expr)
        res_text = simplejson.dumps(response)
        self.set_header('content-type', 'text/plain')
        self.write(res_text)
        self.template = None

    def action_display(self):
        filename = self.fields['filename']
        filename = self.clean_filename(filename)
        filename = os.path.join(self.config['save_dir'], filename)
        f = open(filename)
        c = f.read()
        f.close()
        self.template = None
        self.set_header('content-type', 'text/plain')
        self.write(c)

    def action_save_console(self):
        console = self.fields['console']
        self.session['saved_console'] = console
        self.template = None
        self.write('OK')
    
    def clean_filename(self, fn):
        fn = fn.split('/')[-1]
        fn = fn.split(os.path.sep)[-1]
        return fn

