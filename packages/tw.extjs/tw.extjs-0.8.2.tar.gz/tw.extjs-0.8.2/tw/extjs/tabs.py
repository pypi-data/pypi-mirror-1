from tw.api import Widget, js_function
from tw.extjs import all, all_css



class SimpleTab(Widget):
    javascript=[all]
    css = [all_css]
    params = source_vars = ["tabs", "items", "width", "renderTo", "activeTab", "frame","tabList"]
    tabs = {'Tab Title 1': 'Tab content 1','Tab Title 2': 'Tab content 2'}
    items = [{'contentEl': k.replace(" ","").lower(), 'title': k} for k in tabs.keys()]
    tabList = [(k.replace(" ","").lower(),v) for k, v in tabs.items()]
    frame = True
    renderTo="tab1"
    activeTab=0
    width = "300"
    include_dynamic_js_calls = True
    
    engine_name = "genshi"
    template = """
    <div  xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" >
        <div  id="${renderTo}">
            <div py:for="tab in tabList" id="${tab[0]}">
                <p> ${tab[1]} </p>
            </div>
        </div>
    </div>
    """
    def update_params(self, d):
        super(SimpleTab, self).update_params(d)
        for param in self.source_vars:
            value = getattr(self,param)
            d[param] = value
            
        jsParams = dict(items=self.items, 
                        width=self.width,
                        renderTo=self.renderTo,
                        frame=str(self.frame).lower(),
                        activeTab=self.activeTab)
                        
        call =  js_function('new Ext.TabPanel')(jsParams)
        
        self.add_call(call)


 
    
