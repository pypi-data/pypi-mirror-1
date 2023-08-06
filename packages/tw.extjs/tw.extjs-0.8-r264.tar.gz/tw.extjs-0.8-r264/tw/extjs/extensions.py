from base import ExtJSLinkAutoInit, all_debug, all


autogrid_debug_js = ExtJSLinkAutoInit(modname=__name__, filename='static/ux/autogrid.js',
                        javascript=[all_debug])

autogrid_js = ExtJSLinkAutoInit(modname=__name__, filename='static/ux/autogrid.js',
                        javascript=[all])
