from cStringIO import StringIO
import traceback
import threading
import pdb
import sys
import re
import weakref
from itertools import count
import time
import simplejson
import textwrap
from htconsole.htmlrepr import html_repr
from webhelpers.util import html_escape

exec_lock = threading.RLock()

now = time.time()
count_start = (now % 10000) * 1000
counter = count(int(count_start))

class ObjectGone(Exception):
    """
    Raised when doing a callback to an object that has
    disappeared
    """

class EvalContext(object):

    """
    Class that represents a interactive interface.  It has its own
    namespace.  Use eval_context.exec_expr(expr) to run commands; the
    output of those commands is returned, as are print statements.

    This is essentially what doctest does, and is taken directly from
    doctest (with a bunch of extensions).
    """

    def __init__(self, make_callback, builtin):
        self.namespace = {}
        self.callbacks = {}
        self.make_callback = make_callback
        self.history = []
        self.builtin = builtin
        for name in dir(builtin):
            if name.startswith('_'):
                continue
            method = getattr(builtin, name)
            self.namespace[name] = method
        self.stdout = None

    def snapshot(self):
        """
        Returns an object that can be used to see changes
        with ``self.objects_changed(snapshot)``
        """
        return dict((name, id(ob))
                    for name, ob in self.namespace.items()
                    if name != '__builtins__')

    def get_http_callback(self, obj, callback, weak=False):
        """
        Return a link that can be used to call back with
        the given function and object.  If weak is true,
        then this will be garbage-collectable
        """
        pair = (obj, callback)
        pair_id = id(pair)
        if weak:
            try:
                pair = weakref.ref(pair)
            except TypeError:
                # @@: can't weakrefify it
                pass
        self.callbacks[pair_id] = pair
        return str(self.make_callback(pair_id))

    def get_js_callback(self, obj, callback, weak=False,
                        insert_into=None, js_args=None):
        """
        Get a Javascript statement (e.g., to be put into an onclick
        attribute) that will make the callback.

        If ``insert_into`` is given, then the response of that
        callback will be inserted into the element of the given
        (Javascript/DOM) id.
        """
        js_args = js_args or {}
        uri = self.get_http_callback(
            obj, callback, weak=weak)
        js_args = [str(uri), insert_into, js_args]
        js_args = [simplejson.dumps(j) for j in js_args]
        return 'doCallback(%s)' % ', '.join(js_args)

    def get_id(self):
        """
        Get an ID that should be unique, and hopefully unique over
        restarts.
        """
        return 'ob-%s' % counter.next()

    def do_callback(self, pair_id, *args, **kw):
        pair_id = int(pair_id)
        if pair_id not in self.callbacks:
            raise ObjectGone(
                "The object by the id %s no longer "
                "exists; has the server been restarted?"
                % pair_id)
        ref = self.callbacks[pair_id]
        if isinstance(ref, weakref.ReferenceType):
            ref = ref()
        if ref is None:
            raise ObjectGone(
                "The object by the id %s has been "
                "garbage collected and is not available"
                % pair_id)
        obj, callback = ref
        return callback(obj, self, *args, **kw)

    def html_repr(self, obj, verbosity=1, interactive=False):
        return html_repr(obj, self, verbosity, interactive)

    def objects_changed(self, snapshot):
        """
        Returns a dictionary of all objects in the current
        namespace that have changed since the snapshot
        was taken
        """
        return dict((name, ob)
                    for name, ob in self.namespace.items()
                    if id(ob) != snapshot.get(name)
                    and name != '__builtins__')

    def objects_removed(self, snapshot):
        """
        Returns a list of names removed since the snapshot
        """
        return [name for name in snapshot.keys()
                if name not in self.namespace]

    _func_re = re.compile(
        r'^def\s+([a-z_][a-z0-9_]*).*[)]:[ \t]*(?:[\n\r])?',
        re.I | re.S)

    def exec_expr(self, s):
        """
        Executes the expression in this context
        """
        out = HTMLStdout()
        exec_lock.acquire()
        save_stdout = sys.stdout
        try:
            debugger = _OutputRedirectingPdb(save_stdout)
            debugger.reset()
            pdb.set_trace = debugger.set_trace
            sys.stdout = out
            self.stdout = out
            had_error = False
            try:
                value = exec_maybe_eval(s, self.namespace)
                self.print_altrepr(value)
                match = self._func_re.search(s)
                if match:
                    func_name = match.group(1)
                    body = s[match.end():]
                    body = textwrap.dedent(body)
                    func = self.namespace.get(func_name)
                    if func:
                        func.body = body
                debugger.set_continue()
            except KeyboardInterrupt:
                raise
            except:
                traceback.print_exc(file=out)
                had_error = True
                debugger.set_continue()
        finally:
            sys.stdout = save_stdout
            self.stdout = None
            exec_lock.release()
        html = out.gethtml()
        text = out.gettext()
        if had_error:
            # Take ourselves out of traceback
            lines = text.splitlines()
            text = '\n'.join(lines[:1] + lines[3:])
            html = html_escape(text)
        self.history.append((s, had_error, text, html))
        return text, html

    def print_altrepr(self, value):
        if value is None:
            return
        self.stdout.write_html(
            self.html_repr(value, interactive=True))

    def exec_expr_response(self, s):
        exec_lock.acquire()
        try:
            snapshot = self.snapshot()
            self.builtin.result = None
            self.builtin.context = self
            text, html = self.exec_expr(s)
            response = {
                'result_html': html,
                'changed': {},
                }
            for name, value in self.objects_changed(snapshot).items():
                response['changed'][name] = self.html_repr(value)
            response['removed'] = self.objects_removed(snapshot)
            if self.builtin.result is not None:
                response.update(self.builtin.result)
                self.builtin.result = None
            return response
        finally:
            exec_lock.release()

    def history_content(self):
        """
        Return all the commands that were not erroneous leading up to
        the current state.
        """
        out = StringIO()
        for input, had_error, output in self.history:
            if had_error:
                continue
            out.write(input)
            out.write('\n')
        return out.getvalue()

    def doctest_content(self):
        """
        Return all the commands plus output, leading up to the current
        state.
        """
        out = StringIO()
        for input, had_error, output in self.history:
            lines = input.splitlines(True)
            out.write('>>> %s' % lines[0])
            for line in lines[1:]:
                out.write('... %s' % line)
            if had_error:
                # leave out detail
                lines = output.splitlines(True)
                out.write(lines[0])
                out.write('    ...\n')
                out.write(lines[-1])
            else:
                out.write(output)
        return out.getvalue()

def exec_maybe_eval(code, globs, locs=None, name='<web>'):
    c_single = compile(code, name, 'single', 0, 1)
    c_exec = compile(code, name, 'exec', 0, 1)
    if c_single.co_code == c_exec.co_code:
        # this is a statement
        if locs is None:
            exec c_exec in globs
        else:
            exec c_exec in globs, locs
        return None
    else:
        c_eval = compile(code, name, 'eval', 0, 1)
        if locs is None:
            value = eval(c_eval, globs)
        else:
            value = eval(c_eval, globs, locs)
        return value
    

# From doctest
class _OutputRedirectingPdb(pdb.Pdb):
    """
    A specialized version of the python debugger that redirects stdout
    to a given stream when interacting with the user.  Stdout is *not*
    redirected when traced code is executed.
    """
    def __init__(self, out):
        self.__out = out
        pdb.Pdb.__init__(self)

    def trace_dispatch(self, *args):
        # Redirect stdout to the given stream.
        save_stdout = sys.stdout
        sys.stdout = self.__out
        # Call Pdb's trace dispatch method.
        try:
            return pdb.Pdb.trace_dispatch(self, *args)
        finally:
            sys.stdout = save_stdout

class HTMLStdout(object):

    def __init__(self, echo=None, quote_whitespace=True):
        self.html = []
        self.text = []
        self.echo = echo
        self.quote_whitespace = quote_whitespace
        if self.quote_whitespace:
            self.escape = html_escape_quote
        else:
            self.escape = html_escape

    def write(self, v):
        self.text.append(v)
        self.html.append(self.escape(v))
        if self.echo:
            self.echo.write(v)

    def write_html(self, v, text=None):
        if text is None:
            # @@: Unhtmlify?
            self.text.append(v)
        else:
            self.text.append(text)
        self.html.append(v)
        if self.echo:
            self.echo.write(v)

    def gethtml(self):
        return ''.join(self.html)

    def gettext(self):
        return ''.join(self.text)

def html_escape_quote(v):
    v = html_escape(v)
    v = v.replace('\n', '<br>\n')
    v = re.sub(r'  +', lambda m:
               '&nbsp;'*(len(m.group(0))-1)+' ', v)
    return v
