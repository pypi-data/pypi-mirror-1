import re
import os
from pkg_resources import resource_filename

from tw.api import JSLink, CSSLink, Link

__all__ = ['all', 'all_debug', 'core', 'core_debug', 'all_css','gray_theme', 'black_theme', 'locale']

adapter = JSLink(modname="tw.extjs",
                 filename='static/adapter/ext/ext-base.js')

all_css = CSSLink(modname="tw.extjs",
                  filename='static/resources/css/ext-all.css')

gray_theme = CSSLink(modname="tw.extjs",
                     filename='static/resources/css/ytheme-gray.css')
black_theme = CSSLink(modname="tw.extjs",
                     filename='static/resources/css/xtheme-black.css')
#TODO: Wrap the other themes

blank_img = Link(modname="tw.extjs", filename='static/s.gif')

class ExtJSLinkAutoInit(JSLink):
    """Custom JSLink that initializes some Ext constants at bodybottom"""
    include_dynamic_js_calls = True

    css = [all_css,]
    def update_params(self, d):
        super(ExtJSLinkAutoInit, self).update_params(d)
        self.add_call("Ext.BLANK_IMAGE_URL = %r;" % blank_img.link)

all = ExtJSLinkAutoInit(modname="tw.extjs", filename='static/ext-all.js',
                        javascript=[adapter])

#XXX Deprecate me
all_debug = all

core = ExtJSLinkAutoInit(modname="tw.extjs",
                         filename='static/ext-core.js',
                         javascript=[adapter])

#XXX Deprecate me too
core_debug = core


class LocaleBunch(object):
    """An object which has as attributes the JSLinks for each locale. To 
    override the locale include on of these *after* Ext has been included.
    Eg:
    
    >>> from tw.api import Widget
    >>> from tw import extjs
    >>> spanish_extjs = extjs.locale.es

    >>> class MyWidget(Widget):
    ...     javascript = [extjs.all, extjs.all_css, spanish_extjs]
    """
    def __init__(self, modname, locale_dir, locale_re):
        if isinstance(locale_re, basestring):
            locale_re = re.compile(locale_re)
        for fname in os.listdir(resource_filename(modname, locale_dir)):
            m = locale_re.match(fname)
            if m:
                link = JSLink(modname = modname, location="bodytop",
                              filename = os.path.join(locale_dir, fname))
                setattr(self, m.group(1), link)

locale = LocaleBunch("tw.extjs", 'static/locale', r'extjs-lang-([^\.]+).js')

