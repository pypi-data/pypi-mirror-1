import dispatch
import types
import inspect
import os
import textwrap
import itertools
from cStringIO import StringIO
import traceback
from webhelpers.util import html_escape
import simplejson

py_doc_base = 'http://python.org/doc/current/lib/module-%s.html'
stdlib_dir = os.path.dirname(inspect.__file__)

@dispatch.generic()
def html_repr(obj, context, verbosity, interactive):
    """Return the HTML representation of the object

    verbosity is an integer:

    0:
      very brief (like repr(), but maybe shorter)
    1:
      normal, but not excessive
    2:
      pretty verbose/complete
    3:
      complete, maybe recursively complete

    interactive is an boolean
    """
    pass

obj_memory = {}
obj_counter = itertools.count()

@html_repr.when("isinstance(obj, object)")
def html_repr_object(obj, context, verbosity, interactive):
    if hasattr(obj, '__html_repr__'):
        return obj.__html_repr__(verbosity)
    try:
        concrete_repr = obj.__class__.__repr__
    except AttributeError:
        concrete_repr = None
    if concrete_repr is object.__repr__:
        # The default repr, boo!
        ob_id = id(obj)
        if ob_id in obj_memory:
            small_id = obj_memory[ob_id]
        else:
            small_id = obj_memory[ob_id] = obj_counter.next()
        class_name = obj.__class__.__name__
        if obj.__class__.__module__ != '__builtin__':
            class_name = obj.__class__.__module__ + '.' + class_name
        return '''
        <code class="py-repr">&lt;<span
         title="%s">%s</span> object
         %s&gt;</code>''' % (class_name,
                             obj.__class__.__name__,
                             small_id)
    return '<code class="py-repr">%s</code>' % html_escape(repr(obj))

@html_repr.when("isinstance(obj, (list, tuple))")
def html_repr_list(obj, context, type,
                   verbosity, interactive):
    if isinstance(obj, list):
        sep = '[]'
    else:
        sep = '()'
    content = ''.join([
        '&nbsp; &nbsp; %s,<br>\n' % html_repr(item, context, verbosity-1)
        for item in obj])
    return '%s: %s<br>\n%s%s' % (
        type(obj).__name__, sep[0], content, sep[1])

@html_repr.when("isinstance(obj, types.FunctionType)")
def html_repr_func(obj, context, verbosity, interactive):
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
    uri = context.get_http_callback(obj, _html_set_func)

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
    expr = 'def %s(%s):\n%s' % (name, args, indent(body))
    ns = {}
    try:
        exec expr in ns
    except:
        out = StringIO()
        traceback.print_exc(file=out)
        result = {'error': out.getvalue()}
    else:
        new_func = ns[name]
        obj.func_code = new_func.func_code
        obj.func_defaults = new_func.func_defaults
        obj.func_doc = new_func.func_doc
        obj.body = body
        result = {'result': html_repr(obj, context, 1, False)}
    return simplejson.dumps(result)

@html_repr.when("isinstance(obj, types.MethodType)")
def html_repr_method(obj, context, verbosity, interactive):
    if obj.im_self is None:
        parent_rel = 'unbound method of'
        parent = obj.im_class
    else:
        parent_rel = 'method of'
        parent = obj.im_self
    func_repr = html_repr(obj.im_func, context, verbosity, interactive)
    parent_repr = html_repr(parent, context, 0, interactive)
    return '''
    <div>%s <span type="py-method-parent">%s</span>:<br>
    %s
    </div>''' % (parent_rel, parent_repr, func_repr)

@html_repr.when("obj is None")
def html_repr_None(obj, context, verbosity, interactive):
    return '<span class="py-none">None</span>'

def indent(s, level=4):
    lines = s.splitlines(True)
    return ''.join([' '*level+l for l in lines])
    
@html_repr.when("isinstance(obj, types.ModuleType)")
def html_repr_module(obj, context, verbosity, interactive):
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
def html_repr_string(obj, context, verbosity, interactive):
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
def html_repr_class(obj, context, verbosity, interactive):
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
        % (html_escape(name), html_repr(value, context, verbosity-1))
        for name, value in attrs])
    methods = sorted(methods.items())
    methods = '<br>\n'.join([
        html_repr(value, context, verbosity-1)
        for name, value in methods])
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

