# -*- coding: utf-8 -*-
from mako.template import Template
import urllib
import os

def normalize(title):
    filename = urllib.quote_plus(title)
    for i, o in (('%E8', 'e'), ('%E9', 'e'),
                 ('%20', '_'), ('+', '_')
                ):
        filename = filename.replace(i, o)
    return filename

def template(name, title, **kwargs):
    if not title:
        print 'title required'
        return

    for dirname in (os.path.dirname(__file__),
                    os.path.expanduser('~/.config/rstctl')):
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        path = os.path.join(dirname, '%s.tmpl' % name)
        if os.path.isfile(path):
            break

    if not os.path.isfile(path):
        print 'Template %s does not exist' % path
        return
    print "Using %s" % path

    tmpl = Template(filename=path,
                 default_filters=['decode.utf8'],
                 input_encoding='utf-8',
                 output_encoding='utf-8')

    filename = normalize(title)

    try:
        title = title.decode('utf-8')
    except:
        title = title.decode('iso-8859-1')

    value = tmpl.render_unicode(title=title, name=name, filename=filename, **kwargs)

    if 'dst' in kwargs:
        filename = kwargs.pop('dst')
    else:
        filename += '.txt'
    fd = open(filename, 'w')
    print 'Writing', filename
    fd.write(value.encode('utf-8'))
    fd.close()

def extract_module(pkg):
    classes = []
    functions = []
    try:
        mod = __import__(pkg, [''], [''])
    except ImportError, e:
        print 'Cant import %s: %r' % (pkg, e)
        return []
    else:
        if '.' in pkg:
            splited = pkg.split('.')[1:]
            while splited:
                mod = getattr(mod, splited.pop(0))
    names = getattr(mod, '__all__', dir(mod))
    for name in names:
        if name.startswith('_'):
            continue
        obj = getattr(mod, name, None)
        if hasattr(obj, '__file__'):
            continue
        if hasattr(obj, 'func_name') and hasattr(obj, '__doc__'):
            if getattr(obj, '__module__', None) == pkg:
                functions.append(obj.func_name)
        elif hasattr(obj, '__name__') and hasattr(obj, '__doc__'):
            if getattr(obj, '__module__', None) == pkg:
                classes.append(obj.__name__)
    if classes or functions:
        return dict(classes=classes, functions=functions)


def sphinx_templates(conf_file):
    import sys
    import inspect
    from setuptools import find_packages
    sys.path.insert(0, '.')
    data = {}
    modules = []
    if not os.path.isfile(conf_file):
        print '%s dos not exist' % conf_file

    dirname = os.path.dirname(conf_file)
    sys.path.insert(0, dirname)
    conf = __import__('conf')

    if 'sphinx.ext.autodoc' not in conf.extensions:
        print 'sphinx.ext.autodoc is required. Please add it in your %s file' % conf_file

    modules_dirname = os.path.join(dirname, 'modules')
    ext = conf.source_suffix
    excludes = getattr(conf, 'rstctl_exclude', [])

    if not os.path.isdir(modules_dirname):
        os.makedirs(modules_dirname)

    for pkg in find_packages():
        for root, dirnames, filenames in os.walk(pkg):
            for filename in filenames:
                if filename.endswith('.py'):
                    name = root.replace(os.sep, '.')
                    if filename != '__init__.py':
                        name += '.'+filename[:-3]
                    exclude = False
                    for e in excludes:
                        if name.startswith(e):
                            print 'Skipping %s excluded by conf.py' % name
                            exclude = True
                            break
                    if not exclude and '.config' not in name and '.test' not in name:
                        data = extract_module(name)
                        if data:
                            modules.append(name)
                            template('module', name,
                                     dst=os.path.join(modules_dirname, name+ext),
                                     **data)
    if modules:
        print 'Writing index'
        fd = open(os.path.join(modules_dirname, 'index'+ext), 'w')
        fd.write("""
=========
Modules
=========

.. toctree::
   :maxdepth: 3

""".lstrip())
        for name in sorted(modules):
            fd.write('   %s\n' % name)
        fd.close()
