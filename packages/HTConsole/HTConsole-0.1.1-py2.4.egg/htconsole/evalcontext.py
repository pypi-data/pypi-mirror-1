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

    def html_repr(self, obj):
        return html_repr(obj, self)

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
        out = StringIO()
        exec_lock.acquire()
        save_stdout = sys.stdout
        try:
            debugger = _OutputRedirectingPdb(save_stdout)
            debugger.reset()
            pdb.set_trace = debugger.set_trace
            sys.stdout = out
            had_error = False
            try:
                code = compile(s, '<web>', "single", 0, 1)
                exec code in self.namespace
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
            exec_lock.release()
        text = out.getvalue()
        if had_error:
            # Take ourselves out of traceback
            lines = text.splitlines()
            text = '\n'.join(lines[:1] + lines[3:])
        self.history.append((s, had_error, text))
        return text

    def exec_expr_response(self, s):
        exec_lock.acquire()
        try:
            snapshot = self.snapshot()
            self.builtin.result = None
            self.builtin.context = self
            result = self.exec_expr(s)
            response = {
                'result': result,
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
