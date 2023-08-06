# -*- coding: utf-8 -*-
from docutils.core import publish_parts


def rst2html(value):
    docutils_settings = {}
    parts = publish_parts(source=value,
            writer_name="html4css1",
            settings_overrides=docutils_settings)
    return parts['whole']

def rst2txt(value):
    return value

