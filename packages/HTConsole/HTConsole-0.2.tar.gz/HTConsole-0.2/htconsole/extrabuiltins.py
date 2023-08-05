import sys
from cStringIO import StringIO
import os
from webhelpers.util import html_escape
import pydoc

class ExtraBuiltins(object):

    def __init__(self, servlet):
        self.servlet = servlet
        self.context = None
        self.result = None
    
    def clear(self):
        """
        Clear the output
        """
        self.result = {'clear_screen': True}

    def save(self, filename):
        """
        Save the output to the given file
        """
        filename = self.servlet.clean_filename(filename)
        filename = os.path.join(self.servlet.config['save_dir'], filename)
        if not os.path.splitext(filename)[1]:
            filename += '.py'
        c = self.context.history_content()
        f = open(filename, 'w')
        f.write(c)
        f.close()
        print 'File %s saved' % filename

    def load(self, filename=None):
        """
        Load the file.  If no filename is given,
        show the filenames available.
        """
        if filename is None:
            return self._show_load()
        save_dir = self.servlet.config['save_dir']
        filename = self.servlet.clean_filename(filename)
        filename = os.path.join(save_dir, filename)
        f = open(filename)
        c = f.read()
        f.close()
        response = self.context.exec_expr_response(c)
        self.result = response

    def _show_load(self):
        save_dir = self.servlet.config['save_dir']
        files = [fn for fn in os.listdir(save_dir)
                 if not fn.startswith('.')]
        options = []
        for file in files:
            file = html_escape(file)
            options.append(
                '<option value="%s">%s</option>'
                % (file, file))
        id = self.context.get_id()
        html = (
            '<div>load from: <select id="%(id)s">'
            '%(options)s</select>'
            '<button onclick="return sendCommand('
            '\'load(&quot;\'+$(\'%(id)s\').value'
            '+\'&quot;)\')">load</button>'
            '<button onclick="return sendCommand('
            '\'show_file(&quot;\'+$(\'%(id)s\').value'
            '+\'&quot;)\')">show</button></div>'
            % {'id': id,
               'options': '\n'.join(options)})
        self.result = {'result_html': html}

    def show_file(self, filename):
        """
        Show the contents of the file
        """
        js = (
            "window.open('./?_action_=display"
            "&filename=%s', '_blank')"
            % html_escape(filename))
        self.result = {
            'result_javascript': js}
        

    def doctest(self, filename=None):
        """
        Run the doctest.  If no filename is given,
        show the filenames available.
        """
        print "I'm not done yet :("

    def dir(self, obj=None):
        if obj is None:
            names = [n for n in
                     sorted(self.context.namespace.keys())
                     if not n.startswith('_')]
            title = 'dir() of all objects'
            def getter(n):
                return self.context.namespace[n]
        else:
            names = dir(obj)
            title = 'dir(%s)' % self.context.html_repr(obj)
            def getter(n):
                return getattr(obj, n)
        rows = []
        rows.append(
            '<tr><th colspan="2">%s</th></tr>'
            % title)
        for name in names:
            try:
                value = getter(name)
            except Exception, e:
                html = '<span class="error">Could not fetch: %s</span>' % html_escape(str(e))
                h = ''
            else:
                html = self.context.html_repr(value)
                h = get_help(value)
            rows.append(
                '<tr>'
                '<td class="py-label"><span title="%s">%s</span></td>'
                '<td class="py-repr">%s</td>'
                '</tr>'
                % (html_escape(h[:10]), html_escape(name),
                   html))
        table = '<table class="py-dir">%s</table>' % (
            ''.join(rows))
        self.result = {'result_html': table}
        return None
        
def get_help(obj):
    old_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out
        pydoc.doc(obj)
        lines = out.getvalue().splitlines(True)
        return ''.join(lines[2:])
    finally:
        sys.stdout = old_stdout
