# -*- coding: utf-8 -*-
from rstctl import rst_directive
from pygments.formatters import HtmlFormatter
from docutils.core import publish_parts

PYGMENTS_CSS = '''<style type="test/css">
%s
</style>''' % HtmlFormatter().get_style_defs()

def rst2html(value):
    """
    >>> '<p>paragraphe</p>' in  rst2html('''title
    ... =======
    ...
    ... paragraphe
    ... ''')
    True
    """
    docutils_settings = {}
    parts = publish_parts(source=value,
            writer_name="html4css1",
            settings_overrides=docutils_settings)
    html = parts['whole']
    return html.replace('</head>', '%s</head>' % PYGMENTS_CSS)

def rst2pdf(value, filename=None):
    docutils_settings = {}
    parts = publish_parts(source=value,
            writer_name="xml",
            settings_overrides=docutils_settings)
    from pdf import xml2rml
    output = xml2rml(parts['whole'])
    if filename:
        import os
        fd = open(filename, 'w')
        fd.write(output.getvalue())
        fd.close()
        os.system('open %s' % filename)

def rst2txt(value):
    return value

