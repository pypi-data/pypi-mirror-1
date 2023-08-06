# -*- coding: utf-8 -*-
from rstctl.template import sphinx_templates
import sys

def builder_inited(app):
    sphinx_templates(app=app)

def setup(app):
    app.add_config_value('rstctl_exclude', [], False)
    app.connect('builder-inited', builder_inited)
