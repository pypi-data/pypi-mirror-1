# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from z3c.rml import rml2pdf

_template = '''<?xml version="1.0" encoding="iso-8859-1" standalone="no"?>
<!DOCTYPE document SYSTEM "rml.dtd">

<document
    pagesize="A4"
    filename="tag-para.pdf"
    xmlns:doc="http://namespaces.zope.org/rml/doc">
  <stylesheet doc:example="">
    <paraStyle
        name="list_item"
        spaceAfter="0.1cm"
        alignement="center"
        />
  </stylesheet>

  <template>
    <pageTemplate id="main">
      <frame id="first" x1="1cm" y1="1cm" width="19cm" height="27cm"/>
    </pageTemplate>
  </template>
  <story doc:example="">
    %s
  </story>
</document>
'''

def xml2rml(xml):
    d = pq(xml.encode('utf-8'))

    for l in d('list_item'):
        pq(l).html(pq(l).text())

    for name in ('docinfo', 'target', 'comment', 'image'):
        d(name).remove()

    for name in ('document', 'section'):
        d(name).removeAttr('ids')
        d(name).removeAttr('names')
    for name in ('bullet_list',):
        d(name).removeAttr('bullet')

    html = d.html()
    for name, newname in (
                 ('title', 'h1'),
                 ('paragraph', 'para'),
                 ('list_item', 'para style="list_item"'),
                 ):
        html = html.replace('<%s>' % name, '<%s> ' % newname)
        html = html.replace('</%s>' % name, '</%s>\n' % newname.split()[0])
    for name in ('section', 'bullet_list'):
        html = html.replace('<%s>' % name, '')
        html = html.replace('</%s>' % name, '')
    rml = _template % html
    #print rml
    return rml2pdf.parseString(rml)
