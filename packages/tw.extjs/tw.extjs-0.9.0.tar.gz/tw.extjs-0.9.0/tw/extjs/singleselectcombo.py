from tw.api import Widget, JSLink, CSSLink
from tw.api import js_function, js_callback
from tw.forms.fields import SingleSelectField

from tw.extjs.base import all
from tw.extjs.base import gray_theme

class SingleSelectCombo(SingleSelectField):

        params = ["typeAhead","triggerAction", "width", "forceSelection"]

        typeAhead__doc=""
        triggerAction__doc=""
        width_doc=""
        forceSelection_doc=""

        typeAhead=True
        triggerAction="all"
        width='auto'
        forceSelection=True

        javascript=[all, gray_theme]
        def update_params(self, d):
            super(SingleSelectCombo, self).update_params(d)
            if not getattr(d,"id",None):
                raise ValueError, "An id is needed for SingleSelectCombo"

            opts = dict(transform=d.id,
			   typeAhead=self.typeAhead,
			   triggerAction=self.triggerAction,
			   width=self.width,
			   forceSelection=self.forceSelection)
            
            call = js_function('new Ext.form.ComboBox')(opts)
            self.add_call(call)
