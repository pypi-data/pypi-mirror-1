"""
Dojo 1.1 widget for ToscaWidgets

To download and install::

  easy_install tw.dojo

"""
from tw.api import Resource, Link ,JSLink, JSSource, CSSLink, CSSSource, Widget, js_function, locations
from tw.api import RequestLocalDescriptor
from tw.core.resources import JSDynamicFunctionCalls
import simplejson

class DojoLink(JSLink):
    engine_name='genshi'
    template = """<script type="text/javascript" src="$link" djConfig="isDebug: ${isDebug and 'true' or 'false'},
    parseOnLoad: ${parseOnLoad and 'true' or 'false'}"/>"""
    params = ["isDebug","parseOnLoad"]
    isDebug=False
    parseOnLoad=True
    
dojo_js = DojoLink(
    modname = __name__, 
    filename = 'static/dojo/dojo.js',
    )

dojo_debug_js =     DojoLink(
        modname = __name__, 
        filename = 'static/dojo/dojo.js',
        isDebug = True
        )

dojo_css = CSSLink(
    modname = __name__, 
    filename = 'static/dojo/resources/dojo.css',
    )

grid_css = CSSLink(
    modname = __name__, 
    filename = 'static/dojox/grid/resources/Grid.css',
    )

dijit_dir = Link(
    modname = __name__, 
    filename = 'static/dijit/',
    )

dojox_dir = Link(
    modname = __name__, 
    filename = 'static/dojox/',
    )

twdojo_dir = Link(
    modname = __name__, 
    filename = 'static/twdojo/',
    )

tundra_css = CSSLink(
    modname = __name__, 
    filename = 'static/dijit/themes/tundra/tundra.css',
    )

soria_css = CSSLink(
    modname = __name__, 
    filename = 'static/dijit/themes/soria/soria.css',
    )

nihilo_css = CSSLink(
    modname = __name__, 
    filename = 'static/dijit/themes/nihilo/nihilo.css',
    )

tundragrid_css = CSSLink(
    modname = __name__, 
    filename = 'static/dojox/grid/resources/tundraGrid.css',
    )

soriagrid_css = CSSLink(
    modname = __name__, 
    filename = 'static/dojox/grid/resources/soriaGrid.css',
    )

nihilogrid_css = CSSLink(
    modname = __name__, 
    filename = 'static/dojox/grid/resources/nihiloGrid.css',
    )

themes_css = {'tundra':[tundra_css,tundragrid_css],'soria':[soria_css,soriagrid_css],'nihilo':[nihilo_css,nihilogrid_css]}

class DojoRequireCalls(JSDynamicFunctionCalls): 
    location = "headbottom" 
    javascript = [dojo_js]
    _resource = [dijit_dir,dojox_dir,twdojo_dir]
    css = [dojo_css,tundra_css]
    # This is an attribute which can hold requirements in a request-local 
    # set. anything added here will only be visible in the current request
    _require = RequestLocalDescriptor("dojo_require_calls", default=set())
    _new_request = RequestLocalDescriptor("dojo_request", default=True)
    def __init__(self,*args,**kwargs):
        if self._new_request: 
            self._require=set()
            self._new_request=False
        super(DojoRequireCalls,self).__init__(*args,**kwargs)
    def call_getter(self,location): 
        # return dojo.require calls. This is called by the superclass 
        return map(js_function('dojo.require'), self._require) 
    def require(self, requirement):
        if self._new_request: 
            self._require=set()
            self._new_request=False
        # Called by dojo widgets which want to inject a requirement 
        self._require.add(requirement)
        # Inject ourselves into the page fisrt time we're called (we can inject 
        # ourselves many times but only will get rendered once 
        self.inject()

dojo_require = DojoRequireCalls("dojo_require")

class DojoTheme(Widget):
    params = ['theme']
    css = []
    engine_name = 'genshi'
    theme='tundra'
    template = """<span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">${theme}</span>"""
    def __init__(self, themes=['tundra'], **kw):
        super(DojoTheme, self).__init__(**kw)
        self.object_type = kw.pop('object_type','')
        self.update_url = kw.pop('update_url','')
        for th in themes:
            if themes_css.has_key(th): self.css.extend(themes_css[th])
                
    
class Dojo(Widget):
    _resource = [dijit_dir,dojox_dir]
    css = [dojo_css,tundra_css]
    javascript = [dojo_js]

class DojoDebug(Widget):
    _resource = [dijit_dir,dojox_dir]
    css = [dojo_css,tundra_css]
    javascript = [dojo_debug_js]

class JSONHash(dict):
    properties=[]
    attributes_list=[]
    skip_attributes = False
    def __init__(self,**kwargs):
        for prop in self.properties: 
            value=kwargs.get(prop,None)
            if value!=None:
                self[prop]=value
        if not self.skip_attributes:
            self['attributes']={}
            for attribute in self.attributes_list:
                value=kwargs.get(attribute,None)
                if value!=None:
                    self['attributes'][attribute]=value

    def json(self):
        return simplejson.dumps(self)


dojo = Dojo()



class DojoBase(Widget):
    """DojoBase is the base dojo(dijit) widget.
    To write a new widget just subclass this, specify the required dojo resources (e.g. "dijit.form.Button")
    in the require list and specify the right dojoType.
    Needed dojo.require calls are automatically injected on head according to the require list content
    """
    require = ['dojo.parser']
    dojoType = ''
    engine_name = 'genshi'
    template = ''
    id = ''
    style = None
    cssclass = None
    params = {'dojoType':'The dojo type of specified widget','id': 'Id of created widget'}

    def update_params(self, d): 
        super(DojoBase, self).update_params(d)
        for r in self.require+['dojo.parser']:
            dojo_require.require(r)

class DojoTree(DojoBase):
    require = ['dijit.Tree']
    dojoType = 'dijit.Tree'
    params = ['store','rootLabel','childrenAttrs','onClick','labelAttr','id']
    store = None
    rootLabel = None
    childrenAttrs = None
    onClick = None
    template = """
    <span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">
    <div dojoType="dijit.tree.ForestStoreModel" py:attrs="dict(id=id+'_treemodel',jsId=id+'_treemodel',
    store=store,rootLabel=rootLabel,childrenAttrs=childrenAttrs)" />
    <div dojoType="${dojoType}" py:attrs="dict(attrs,model=id+'_treemodel',id=id,jsId=id,onClick=onClick,
    labelAttr=labelAttr)"/>
    </span>"""
