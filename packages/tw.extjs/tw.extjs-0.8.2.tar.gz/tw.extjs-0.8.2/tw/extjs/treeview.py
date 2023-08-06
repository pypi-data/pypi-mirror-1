from tw.api import Widget, JSLink, CSSLink, JSSource

from tw.extjs import all

class TreeViewJS(JSSource):
    
    _resources = []
    source_vars = params = ["treeDiv", "title", "collapsible", 
                  "animCollapse", "border", 
                  "autoScroll", "animate", 
                  "enableDD", "containerScroll", "height",
                  "width", "fetch", "rootID", "rootText", "divID", "frame"]
    #treeDiv__doc=""
    treeDiv="treeView"
    title            = 'My Tree'
    collapsible      = True
    animCollapse     = True
    border           = True
    #id               = "treeView"
    divID            = "treeView"
    #el = divID
    autoScroll       = True
    animate          = True
    enableDD         = True
    containerScroll  = True
    height           = 300
    width            = 200
    fetch            = "fetch"
    frame            = True
    
    rootText = "Root"
    rootID   = "Root"
    src= """
Ext.onReady(function() {
    // Define Tree.
    var Tree_Category_Loader = new Ext.tree.TreeLoader({
        dataUrl   :"${fetch}"
    });
    var Tree_Category = new Ext.tree.TreePanel({
        title            : "$title",
        collapsible      : $collapsible,
        animCollapse     : $animCollapse,
        border           : $border,
        id               : "$divID",
        el               : "$divID",
        autoScroll       : $autoScroll,
        animate          : $animate,
        enableDD         : $enableDD,
        containerScroll  : $containerScroll,
        height           : $height,
        width            : $width,
        loader           : Tree_Category_Loader,
        frame            : $frame,
    });
 
    // SET the root node.
    var Tree_Category_Root = new Ext.tree.AsyncTreeNode({
        text		: '$rootText',
        draggable	: false,
        id		: '$rootID'
    });
 
    // Render the tree.
    Tree_Category.setRootNode(Tree_Category_Root);
    Tree_Category.render();
    Tree_Category_Root.expand();
});
"""
    template_engine="genshi"
    javascript=[all]
    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
            if isinstance(value, bool):
                d[param] = str(value).lower()
        super(TreeViewJS, self).update_params(d)
    def post_init(self, *args, **kw):
        pass
    
treeview_js = TreeViewJS()
    
class TreeView(Widget):
    treeview_js_obj = TreeViewJS
    params = js_params = ["treeDiv", 
                          "title", 
                          "collapsible", 
                          "animCollapse", 
                          "border",
                          "autoScroll", 
                          "animate", 
                          "enableDD", 
                          "containerScroll", 
                          "height",
                          "width", 
                          "fetch", 
                          "rootID", 
                          "rootText", 
                          "divID"]

    template = """<div id="$divID" />"""
    
    title = 'Override JS Title'
    
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
