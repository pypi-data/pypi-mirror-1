from tw.api import Widget, JSLink, CSSLink, JSSource
from tw.core.util import Enum, OrderedSet

from tw.extjs import all

class GridJS(JSSource):
    
    _resources = []
    source_vars = params = ["divID", "width", "height", "collapsible", "title", "frame"]
    
    src= """Ext.onReady(function() {
        var myData = {
  'results': 2, 'rows': [
    { 'id': 1, 'company': 'Apple', price: 1 },
    { 'id': 2, 'company': 'Ext', price: 2 } ]
}

 var record = Ext.data.Record.create([
    {name: 'company'},
    {name: 'price'}
]);

         var myReader = new Ext.data.JsonReader({root:'rows', 'id':id}, record);

	var grid = new Ext.grid.GridPanel({
		store: new Ext.data.Store({
			data: myData,
			reader: myReader
		}),
		columns: [
			{header: 'Company', resizable:true, sortable: true, dataIndex: 'company'},
			{header: 'Price', sortable: true, dataIndex: 'price'},
		],
		renderTo: '${divID}',
		title: 'My First Grid',
		width: 500,
		frame: true,
                collapsible: true
	});
 
	grid.getSelectionModel().selectFirstRow();
});
"""
    template_engine="genshi"
    javascript=[all]
    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
            if isinstance(value, bool):
                d[param] = str(value).lower()
        super(GridJS, self).update_params(d)
    def post_init(self, *args, **kw):
        pass
    valid_locations = Enum('head', 'bodytop', 'bodybottom')
    location = valid_locations.bodybottom

class Grid(Widget):
    treeview_js_obj = GridJS
    params = js_params = ['divID']

    template = """<div id="$divID" />"""
    
    def __new__(cls, *args, **kw):
        cls = Widget.__new__(cls, *args, **kw)
        d = {}
        
        #copy in parameters from this class to the javascript class (keeps all of the params in one place)
        for param in cls.js_params:
            value = getattr(cls, param)
            if value is not None:
                d[param] = getattr(cls, param)
        treeview_js = cls.treeview_js_obj(**d)
        cls.javascript = [treeview_js,]
        return cls
    
