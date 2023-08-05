import dispatch
import types
import inspect
import os
import textwrap
from webhelpers.util import html_escape
import simplejson

py_doc_base = 'http://python.org/doc/current/lib/module-%s.html'
stdlib_dir = os.path.dirname(inspect.__file__)


@dispatch.generic()
def html_repr(obj, context):
    """Return the HTML representation of the object"""
    pass

@html_repr.when("isinstance(obj, object)")
def html_repr_object(obj, context):
    if hasattr(obj, '__html_repr__'):
        return obj.__html_repr__()
    return '<code>%s</code>' % html_escape(repr(obj))

@html_repr.when("isinstance(obj, (list, tuple))")
def html_repr_list(obj, context):
    if isinstance(obj, list):
        sep = '[]'
    else:
        sep = '()'
    content = ''.join([
        '&nbsp; &nbsp; %s,<br>\n' % html_repr(item, context)
        for item in obj])
    return '%s: %s<br>\n%s%s' % (
        type(obj).__name__, sep[0], content, sep[1])

@html_repr.when("isinstance(obj, types.FunctionType)")
def html_repr_func(obj, context):
    args = inspect.formatargspec(
        *inspect.getargspec(obj))[1:-1]
    try:
        body = inspect.getsource(obj)
        body = ''.join(body.splitlines(True)[1:])
        body = textwrap.dedent(body)
    except IOError:
        if getattr(obj, 'body', None):
            body = obj.body
        else:
            # cannot get source code :(
            body = '(code not found)'
    name = obj.func_name
    obj_id = context.get_id()
    uri = context.get_http_callback(None, _html_set_func)

    return '''
    <div id="%(id)s"><code>def
    <b id="%(id)s-name">%(name)s</b>(<span id="%(id)s-args">%(args)s</span>):</code>
    <a href="#" onclick="editFunc(%(id)r, %(uri)r)"
     title="edit this function"
     class="small-button">edit</a>
    <pre id="%(id)s-body" class="py-func-body">%(body)s</pre>
    </div>
    ''' % dict(id=obj_id, name=html_escape(name), args=html_escape(args), body=html_escape(body), uri=uri)

def _html_set_func(obj, context, name, args, body):
    assert obj is None
    expr = 'def %s(%s):\n%s' % (name, args, indent(body))
    output = context.exec_expr(expr)
    if output:
        result = {'error': output}
    else:
        func = context.namespace[name]
        result = {'result': html_repr(func, context)}
    return simplejson.dumps(result)

def indent(s, level=4):
    lines = s.splitlines()
    return ''.join([' '*level+l for l in lines])
    
@html_repr.when("isinstance(obj, types.ModuleType)")
def html_repr_module(obj, context):
    obj_dir = os.path.dirname(obj.__file__)
    if obj_dir == stdlib_dir:
        return (
            'Module <code class="py-module-name">%s</code> '
            'from <a href="%s" target="_blank">standard library</a>'
            % (obj.__name__,
               py_doc_base % obj.__name__))
    return (
        'Module <code class="py-module-name">%s</code> '
        'in <code class="py-module-file">%s</code>'
        % (obj.__name__, obj.__file__))

@html_repr.when("isinstance(obj, basestring)")
def html_repr_string(obj, context):
    r = repr(obj)
    if len(r) < 50:
        return '<code>%s</code>' % html_escape(r)
    expand_id = context.get_id()
    callback = context.get_js_callback(
        obj, _html_repr_string_long, insert_into=expand_id)
    return (
        '<code id="%s">' % expand_id
        + r[:40]
        + '<a href="#" onclick="return %s" title="click to expand to full width (%i characters)">...</a>' % (html_escape(callback), len(r))
        + r[-5:]
        + '</code>')

def _html_repr_string_long(obj, context):
    return html_escape(repr(obj))

@html_repr.when("isinstance(obj, (types.ClassType, type))")
def html_repr_class(obj, context):
    cls_name = obj.__name__
    bases = obj.__bases__
    if bases:
        bases = ', '.join([c.__name__ for c in bases])
        bases = '(%s)' % bases
    else:
        bases = ''
    attrs = {}
    methods = {}
    special = {}
    for name, value in obj.__dict__.items():
        if name in ['__doc__', '__module__', '__builtin__']:
            special[name] = value
            continue
        if isinstance(value, types.FunctionType):
            methods[name] = value
        else:
            attrs[name] = value
    if special.get('__doc__'):
        doc = html_repr(special['__doc__'], context)
        doc = '<div class="py-doc">%s</div>' % doc
    else:
        doc = ''
    attrs = sorted(attrs.items())
    attrs = '<br>\n'.join([
        '<code class="py-name">%s</code> = %s'
        % (html_escape(name), html_repr(value, context))
        for name, value in attrs])
    methods = sorted(methods.items())
    methods = '<br>\n'.join([
        html_repr(value, context) for name, value in methods])
    if not methods and not attrs and not doc:
        extra = '<code>pass</code>'
    else:
        extra = ''
    return (
        '<code>class <b>%(name)s</b>%(bases)s:</code>'
        '<blockquote class="py-class-body">\n'
        '%(doc)s %(attrs)s %(methods)s %(extra)s\n'
        '</blockquote>\n'
        % dict(name=cls_name, bases=bases, doc=doc or '',
               extra=extra, attrs=attrs, methods=methods))

