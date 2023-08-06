# -*- coding: utf-8 -*-
import re
import os
import sys
import utils
import tempfile
import template
from optparse import OptionParser
from subprocess import Popen, PIPE

usage = "%prog [options] [file]"

parser = OptionParser()
parser.usage = usage
parser.add_option("-w", "--www", dest="browser",
                  action="store_true", default=False,
                  help="open html in a web browser")
parser.add_option("-s", "--serve", dest="serve",
                  action="store_true", default=False,
                  help="serve html at http://localhost:6969/ once")
parser.add_option("-c", "--cat", dest="cat",
                  action="store_true", default=False,
                  help="cat html to stdout")
parser.add_option("-p", "--pdf", dest="pdf",
                  action="store_true", default=False,
                  help="cat html to stdout")
parser.add_option("-t", "--template", dest="template",
                  action="store", default=None,
                  help="cat html to stdout")
parser.add_option("-l", "--links", dest="links",
                  action="store_true", default=False,
                  help="parse and add links to EOF")
parser.add_option("--sphinx", dest="sphinx",
                  action="store", default=None,
                  help="generate sphinx files for current module")

def main():
    (options, args) = parser.parse_args()
    if not args:
        if options.sphinx:
                template.sphinx_templates(options.sphinx)
                return
        elif os.path.isfile('setup.py'):
            filename = None
            cmd = [sys.executable, 'setup.py', '--long-description']
            env = os.environ.copy()
            env['PYTHONPATH'] = os.pathsep.join(sys.path)
            pipe = Popen(cmd, env=env, stdout=PIPE).stdout
            value = pipe.read()
        else:
            parser.parse_args(['-h'])
    elif options.template:
            name = options.template
            title = ' '.join(args)
            template.template(name, title)
            return
    else:
        filename = args[0]
        value = open(filename).read()

    if options.serve:
        from serve import publish
        publish(utils.rst2html(value), browser=False)
        return

    if options.browser:
        from serve import publish
        publish(utils.rst2html(value))
        return

    if options.cat:
        print utils.rst2html(value)
        return

    if options.pdf:
        filename = os.path.basename(filename)
        filename, ext = os.path.splitext(filename)
        filename += '.pdf'
        print utils.rst2pdf(value, filename=filename)
        return

    if options.links:
        value = utils.rst2html(value).encode('utf-8')
        links = re.findall(
                '.*Unknown target name: &quot;(.*)&quot;.*',
                value)
        text = '\n'.join(['.. _%s: ' % l for l in links])
        print '\n'
        print text
        print '\n'
        if filename:
            value = open(filename).read()
            fd = open(filename, 'w')
            fd.write(value)
            fd.write('\n')
            fd.write(text)
            fd.write('\n')
            print '%s links append to %s' % (len(links), filename)
        return

    parser.parse_args(['-h'])

