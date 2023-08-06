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

def template(name, title):
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

    tmpl = Template(filename=os.path.join(dirname, '%s.tmpl' % name),
                 default_filters=['decode.utf8'],
                 input_encoding='utf-8',
                 output_encoding='utf-8')

    filename = normalize(title)

    try:
        title = title.decode('utf-8')
    except:
        title = title.decode('iso-8859-1')

    value = tmpl.render_unicode(title=title, name=name, filename=filename)

    filename += '.txt'
    fd = open(filename, 'w')
    print 'Writing', filename
    fd.write(value.encode('utf-8'))
    fd.close()

