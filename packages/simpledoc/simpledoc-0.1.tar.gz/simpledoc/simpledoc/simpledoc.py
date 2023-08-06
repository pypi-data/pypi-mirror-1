#!/usr/bin/env python
"""Generates HTML documentation for Python modules.

This is mostly just hacked together over a couple days.
If I have more time I'll be cleaning this up and all that.

You should create a command-line script to call simpledoc.cli()
like so (assuming *nix-based systems):

    #!/usr/bin/env python

    import simpledoc
    if __name__ == '__main__':
        simpledoc.cli()

simpledoc is built on top of pydoc."""

__author__ = 'David Reynolds'
__version__ = '0.1'

import inspect
import pydoc
import pkgutil
from string import find, rstrip
import os, sys, re
from pygments import highlight
from pygments.styles import get_style_by_name
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def getmoduleclasses(module):
    """Return a list of classes in this module"""
    classes = [klass for name, klass in inspect.getmembers(module) if inspect.isclass(klass)]
    return classes

def getclassmethods(klass):
    """Return a list of methods for this class"""
    methods = [method for name, method in inspect.getmembers(klass) if inspect.ismethod(method)]
    return methods

def page(title, body):
    """Generate the basic HTML for the docs"""
    return """
    <html>
        <head>
            <title>%s</title>
            <link rel="stylesheet" type="text/css" href="css/native.css" />
            <style type="text/css">
                body { background: #fff; font: 13px Lucida Grande; color: #333; }
                p { margin: 0; }
                .docstring { color: #666; }
                a { color: #00f; text-decoration: none; }
                a:hover { color: #fff; background: #00f; text-decoration: none; }
                ul { list-style-type: none; }
            </style>

            <script type="text/javascript">
                function show_source(id) {
                    elem = document.getElementById(id);
                    if (elem.style.display == 'none') {
                        elem.style.display = 'block';
                    } else {
                        elem.style.display = 'none';
                    }
                }
            </script>
        </head>
        <body>
            %s
        </body>
    </html>
    """ % (title, body)

def header(title, **kwargs):
    """Generate the HTML header for this page"""
    version = kwargs.get('version')
    desc = title
    if version is not None:
        desc += ' <span style="font-size: 12px;">(Version: %s)</span>' % version

    return """
    <div style="padding: 5px; background: #efefef;">
        <span style="font-size: 18px; font-weight: bold;">%s</span>
    </div>
    """ % desc

def section(title):
    return '<h3>%s</h3>' % title

def formatvalue(obj):
    return '='+repr(obj)

def doc_method(method):
    """Generate the docs for a class method"""
    args, varargs, varkw, defaults = inspect.getargspec(method)
    argspec = inspect.formatargspec(
        args, varargs, varkw, defaults,
        formatvalue=formatvalue)
    
    classlink = """
    %s%s
    """ % (method.__name__, argspec)

    doc = inspect.getdoc(method)
    if doc is None:
        doc = ''
    else:
        doc = '<p class="docstring" style="margin-left: 30px;">%s</p>' % doc.replace('\n', '<br />')

    nav = """
    <div style="margin-top: 10px; margin-left: 30px;">
        [<a href="#" onclick="show_source('%s_%s_%s');">show source</a>]
    </div>""" % (method.__module__, method.im_class.__name__, method.__name__)

    code = inspect.getsource(method)
    code = highlight(code, PythonLexer(), HtmlFormatter(classprefix="native_", style=get_style_by_name('native')))

    sourcediv = """
    <div id="%s_%s_%s" style="display: none; margin-left: 30px; margin-top: 10px;">
        %s
    </div>
    """ % (method.__module__, method.im_class.__name__, method.__name__, code)

    return '<div style="margin: 10px 0;">' + classlink + doc + nav + sourcediv + '</div>'

def doc_function(func):
    """Generate the docs for a given function"""
    args, varargs, varkw, defaults = inspect.getargspec(func)
    argspec = inspect.formatargspec(
        args, varargs, varkw, defaults,
        formatvalue=formatvalue)

    link = """
    %s%s
    """ % (func.__name__, argspec)

    doc = getdoc(func)
    if doc is None:
        doc = ''
    else:
        doc = '<p class="docstring" style="margin-left: 30px;">%s</p>' % doc.replace('\n', '<br />')

    nav = """
    <div style="margin-top: 10px;">
        [<a href="#" onclick="show_source('%s_%s');">show source</a>]
    </div>""" % (func.__module__, func.__name__)

    code = inspect.getsource(func)
    code = highlight(code, PythonLexer(), HtmlFormatter(classprefix="native_", style=get_style_by_name('native')))

    sourcediv = """
    <div id="%s_%s" style="display: none; margin-top: 10px;">
        %s
    </div>
    """ % (func.__module__, func.__name__, code)

    return '<div style="margin: 10px 0;">' + link + doc + nav + sourcediv + '</div>'

def doc_class(klass, name):
    """Generate docs for a given class"""
    body = []
    methods = getclassmethods(klass)
    for meth in methods:
        body.append('<li>' + doc_method(meth) + '</li>')

    return """
    <div style="margin: 10px 20px; padding: 5px;">
        <span style="font-size: 14px; font-weight: bold;">class %s</span>
        <p class="docstring" style="margin-top: 5px;">%s</p>

        <ul>
            <p>Methods defined here:</p>
            <div style="margin: 10px 0;">%s</div>
        </ul>
    </div>
    """ % (klass.__name__, getdoc(klass).replace('\n', '<br />'), '\n'.join(body))

def getmodpackages(module):
    """Return a list of all the modules in this package"""
    name = module.__name__
    pkgs = []
    for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
        pkgs.append((modname, name, ispkg, 0))
    pkgs.sort()
    return pkgs

def document(obj, name):
    """Top-level document generator

    Dispatches objects to their correct doc generator."""
    if inspect.ismodule(obj):
        return docmodule(obj, name)
    if inspect.isclass(obj):
        return doc_class(obj, name)

def getdoc(obj):
    """Wrapper for inspect.getdoc"""
    result = inspect.getdoc(obj) or inspect.getcomments(obj)
    return result and re.sub('^ *\n', '', rstrip(result)) or ''

def visiblename(name, all=None):
    if name in ('__builtins__', '__doc__', '__file__', '__path__',
                '__module__', '__name__', '__slots__'): return 0
    if name.startswith('__') and name.endswith('__'): return 1
    if all is not None:
        return name in all
    else:
        return not name.startswith('_')

def docmodule(obj, name):
    """Generate docs for this module"""
    try:
        all = obj.__all__
    except:
        all = None

    version = None
    try:
        version = getattr(obj, '__version__')
    except:
        pass

    result = header(name, version=version)
    result += '<p class="docstring" style="margin: 10px 0;">%s</p>' % getdoc(obj).replace('\n', '<br />')

    modules = inspect.getmembers(obj, inspect.ismodule)
    classes = []
    for k, v in inspect.getmembers(obj, inspect.isclass):
        if (all is not None or
            (inspect.getmodule(v) or obj) is obj):
            if visiblename(k, all):
                classes.append((k, v))

    functions = []
    for k, v in inspect.getmembers(obj, inspect.isroutine):
        if (all is not None or
            inspect.isbuiltin(v) or inspect.getmodule(v) is obj):
            if visiblename(k, all):
                functions.append((k, v))

    if hasattr(obj, '__path__'):
        modpkgs = getmodpackages(obj)
        contents = ', '.join(['<a href="%s.%s.html">%s</a>' % (name, pkg[0], pkg[0]) for pkg in modpkgs])
        result = result + section('Package contents:') + contents
    elif modules:
        mod_section = '<span style="font-size: 14px; font-weight: bold;">Modules:</span><br />'
        mod_section += '<p style="margin-top: 5px;">' + ', '.join([mod[0] for mod in modules]) + '</p>'
        result += '<div style="margin: 10px 0; padding: 5px; background: #efefef;">%s</div>' % mod_section

    if classes:
        classlist = map(lambda (k, v): v, classes)

        class_section = '<span style="font-size: 14px; font-weight: bold;">Classes:</span><br />'
        class_section += '<p style="margin-top: 5px;">' + ', '.join([klass.__name__ for klass in classlist]) + '</p>'
        result += '<div style="padding: 5px; background: #efefef;">%s</div>' % class_section

        contents = []
        for k, v in classes:
            contents.append(document(v, k))
        result += ''.join(contents)

    func_list = []
    for k, v in functions:
        func_list.append('<li>' + doc_function(v) + '</li>')

    result += """
    <div style="padding: 5px; background: #efefef;">
        <span style="font-size: 14px; font-weight: bold;">Module functions:</span>
    </div>
    <ul style="margin: 0 20px; padding: 5px;">
        %s
    </ul>
    """ % ''.join(func_list)

    return result

def writedoc(thing):
    """Create HTML pages for `thing`"""
    try:
        obj, name = pydoc.resolve(thing)
        p = page(pydoc.describe(obj), document(obj, name))
        f = file(name+'.html', 'w')
        f.write(p)
        f.close()
        print 'wrote', name+'.html'
    except ImportError, e:
        print e

def ispath(x):
    return isinstance(x, str) and find(x, os.sep) >= 0

def cli():
    if len(sys.argv) < 2:
        raise SystemExit('You need to choose what modules to document.')
    args = sys.argv[1:]
    for arg in args:
        if ispath(arg) and os.path.isdir(arg):
            for importer, modname, ispkg in pkgutil.walk_packages([arg], ''):
                writedoc(modname)
        else:
            writedoc(arg)

if __name__ == '__main__':
    cli()
