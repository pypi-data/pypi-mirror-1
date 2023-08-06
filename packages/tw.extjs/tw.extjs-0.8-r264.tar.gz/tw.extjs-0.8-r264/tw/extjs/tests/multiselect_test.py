from tw.api import Widget, JSLink, CSSLink, JSSource
from tw.core.resources import Resource

from tw.jsunit import JSUnit
from tw.extjs import all_debug as all
from tw.extjs.multiselect import multiselect_js, ddview_js, multiselect_css

test_js = JSLink(modname=__name__, filename='static/multiselect_test.js')

class ItemSelectorTest(JSUnit):

    def __init__(self, *args, **kw):
        super(ItemSelectorTest, self).__init__(*args, **kw)
        self.javascript.append(all)
        self.javascript.append(multiselect_js)
        self.javascript.append(ddview_js)
        self.javascript.append(test_js)
        self.css.append(multiselect_css)

    def update_params(self, d):
        super(ItemSelectorTest, self).update_params(d)
