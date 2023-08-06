from tw.dojo.core import DojoBase
from tw.core import CSSLink, JSLink

tree_css = CSSLink(
    modname = 'tw.dojo',
    filename = 'static/dijit/themes/tundra/Tree.css'
    )

dijit_css = CSSLink(
    modname = 'tw.dojo',
    filename = 'static/dijit/themes/dijit.css'
)

lazy_store_js = JSLink(modname='tw.dojo'
                         'static/twdojo/LazyLoadStore.js')

from tw.dojo.core import DojoBase
from tw.core import CSSLink, JSLink
from tw.dojo.tree import tree_css, lazy_store_js, dijit_css

class DojoTreeFilePicker(DojoBase):
    require = [
      "dojox.data.FileStore",
      "dijit.Tree",
      "dijit.ColorPalette",
      "dijit.Menu",
      "dojo.parser",
    ]
    dojoType = 'dijit.Tree'
    params = ['id', 
              'attrs', 
              'jsId', 
              'cssclass', 
              'url'
              ]
    delayScroll = "true"
    css = [tree_css, dijit_css]
    javascript = [lazy_store_js]
    cssclass=""
    rowsPerPage = 20
    columns = []
    columnReordering = "true"
    columnResizing="false"
    include_dynamic_js_calls = True
    action='.json'
    model = None
    actions = True
    template = "genshi:tw.dojo.templates.dojotreepicker"
    
class DojoTreeFileCheckboxPicker(DojoTreeFilePicker):
    require = [
      "dojox.data.FileStore",
      "dijit.Tree",
      "dijit.ColorPalette",
      "dijit.Menu",
      "dojo.parser",
      "twdojo.CheckedTree",
    ]
    template = "genshi:tw.dojo.templates.dojotreecheckboxpicker"