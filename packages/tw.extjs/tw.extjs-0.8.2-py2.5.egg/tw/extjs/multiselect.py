from tw.api import Widget, JSLink, CSSLink, JSSource
from tw.core.resources import Resource

from tw.extjs import all
from tw.extjs import all_css, gray_theme

ddview_js = JSLink(modname="tw.extjs", filename='static/DDView.js')
multiselect_css = CSSLink(modname="tw.extjs",
                          filename='static/resources/css/Multiselect.css')
multiselect_js = JSLink(modname="tw.extjs",
                        filename='static/Multiselect.js',
                        javascript=[ddview_js],
                        css=[multiselect_css])

class ItemSelectorJS(JSSource):

    resources = []
    source_vars = ["divID", "width", "url", "fieldLabel", "labelWidth",
		   "fromData", "toData", "msWidth", "msHeight",
		   "dataFields", "valueField", "displayField",
		   "fromLegend", "toLegend", "submitText", "resetText"]

    src = """
formItemSelector = null;

panelItem = {
            xtype:"itemselector",
            name:"itemselector",
            fieldLabel:"$fieldLabel",
            dataFields:$dataFields,
            fromData:$fromData,
            toData:$toData,
            msWidth:$msWidth,
            msHeight:$msHeight,
            valueField:"$valueField",
            displayField:"$displayField",
            toLegend:"$toLegend",
            fromLegend:"$fromLegend",
            TBar:[{
                text:"Clear",
                handler:function(){
                    var i=formItemSelector.getForm().findField("itemselector");
                    i.reset.call(i);
                }
            }]
    }

buttonSave = {
            text: "$submitText",
            handler: function() {
                formItemSelector.getForm().submit(
                {
                    method: 'POST',
                    waitMsg:'Submitting...',
                    reset : false,
                    success : function() {
                        Ext.Msg.alert("Success!");
                    },
                    failure: function(form, action){Ext.Msg.alert('Error',action.result.text);}
                });
            }
    }

buttonReset = {     
            text:"$resetText",
            handler: function() {
                var i=formItemSelector.getForm().findField("itemselector");
                i.reset.call(i);
            }
    }

Ext.onReady(function(){

    formItemSelector = new Ext.form.FormPanel({ 
        labelWidth:$labelWidth,
        width:$width,
        url:"$url",
        items:panelItem,
        buttons:[buttonSave, buttonReset]
    });

    formItemSelector.render("$divID");
});
    """
    template_engine="genshi"
    javascript=[all]
    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
        super(ItemSelectorJS, self).update_params(d)
    def post_init(self, *args, **kw):
        pass
    location = Resource.valid_locations.head

class ItemSelector(Widget):
    item_selector_js_obj = ItemSelectorJS
    params = js_params = ["divID", "width", "url", "fieldLabel", "labelWidth",
		   "fromData", "toData", "msWidth", "msHeight",
		   "dataFields", "valueField", "displayField",
		   "fromLegend", "toLegend", "submitText", "resetText"]
    submitText = "Submit"
    resetText = "Reset"
    css = [all_css, multiselect_css]

    template = """
    <div style="width:600px;">
        <div class="x-box-tl"><div class="x-box-tr"><div class="x-box-tc"></div></div></div>
        <div class="x-box-ml"><div class="x-box-mr"><div class="x-box-mc">
          <div id="$divID"></div>
        </div></div></div>
        <div class="x-box-bl"><div class="x-box-br"><div class="x-box-bc"></div></div></div>
    </div>
    """

    def __init__(self, *args, **kw):
        super(ItemSelector, self).__init__(*args, **kw)
        d = {}
        for param in self.js_params:
            value = getattr(self, param)
            if value is not None:
                d[param] = getattr(self, param)
        item_selector_js = self.item_selector_js_obj(**d)
        self.javascript = [item_selector_js, multiselect_js]

    def update_params(self, d):
        super(ItemSelector, self).update_params(d)
        if not getattr(d,"divID",None):
            raise ValueError, "ItemSelector requires a divID!"
