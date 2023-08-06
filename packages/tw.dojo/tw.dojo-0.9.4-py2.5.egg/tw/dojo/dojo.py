"""
Dojo 1.1 widget for ToscaWidgets

To download and install::

  easy_install tw.dojo

"""
from tw.api import Resource, Link ,JSLink, JSSource, CSSLink, CSSSource, Widget, js_function, locations
from tw.api import RequestLocalDescriptor
from tw.core.resources import JSDynamicFunctionCalls
import simplejson
#class DojoTheme(CSSLink):
#    engine_name='genshi'
#    template = """<style type="text/css">
#            @import </style>"""
#    params = ["themename"]
#    themename='tundra'

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
class DojoUpdateValues(JSSource):
    _resource = []
    update_url = ''
    object_type = ''
    template_engine = "genshi"
    source_vars = ["object_type"]
    src = """function updateValue(update_url,object_type,object_id,field,value){
        var identifier=object_type+'_id';
        var array=new Array();
        array[field]=value;
        array[identifier]=object_id;
  		var wgt=dijit.byId(object_type+'_'+object_id+'_'+field);
  		try{valid=wgt.isValid();}
  		catch (errore){valid=true;}
        if (valid){var kw={url:update_url,content:array,load:function(data){},error:function(data){},timeout:2000};dojo.xhrGet(kw);};
        };"""

    def __init__(self, location=None, **kw):
        if location:
            if location not in locations:
                raise ValueError, "JSSource location should be in %s" % locations
            self.location = location
        super(DojoUpdateValues, self).__init__(**kw)
        self.object_type = kw.pop('object_type','')
        self.update_url = kw.pop('update_url','')
        for param in self.source_vars:
            value = getattr(self, param)
            if isinstance(value, bool):
                d[param] = str(value).lower()

    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
            if isinstance(value, bool):
                d[param] = str(value).lower()
        super(DojoUpdateValues, self).update_params(d)


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

class DojoButton(DojoBase):
    require = ['dijit.form.Button']
    dojoType = 'dijit.form.Button'
    onClick = None
    title = ''
    attrs = {}
    params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    template = """<div xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    dojoType='${dojoType}' py:attrs="dict(attrs,onClick=onClick)">${title}</div>"""

class DojoTextBox(DojoBase):
    require = ['dijit.form.TextBox']
    dojoType = 'dijit.form.TextBox'
    title = ''
    lowercase = None
    maxlength = None
    propercase = None
    size = None
    trim = None
    uppercase = None
    name = None
    required = None
    attrs = {}
    #params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    params = ['attrs','lowercase','maxlength','propercase','size','trim','uppercase','name','style','required','value','cssclass','dojoType','id']
    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    dojoType='${dojoType}' type="text" class="${cssclass}"
    py:attrs="dict(attrs,lowercase=lowercase,maxlength=maxlength,propercase=propercase,size=size,trim=trim,
    uppercase=uppercase,name=name,style=style,required=required,value=value)"/>"""

class DojoDateTextBox(DojoTextBox):
    require = ['dijit.form.DateTextBox']
    dojoType = 'dijit.form.DateTextBox'
    #params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    params = ['attrs','lowercase','maxlength','propercase','size','trim','uppercase','name','style','required','value','cssclass',
    'dojoType','id','datePattern','timePattern']

    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,title=title,lowercase=lowercase,maxlength=maxlength,propercase=propercase,size=size,
    trim=trim,uppercase=uppercase,name=name,style=style,required=required,value=value,datePattern=datePattern,
    timePattern=timePattern)"/>"""

class DojoCurrencyTextBox(DojoTextBox):
    require = ['dijit.form.CurrencyTextBox']
    dojoType = 'dijit.form.CurrencyTextBox'
    currency = None
    fractional = None
    symbol = None
    params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,title=title,lowercase=lowercase,maxlength=maxlength,propercase=propercase,size=size,
    trim=trim,uppercase=uppercase,name=name,style=style,required=required,value=value,currency=currency,
    fractional=fractional,symbol=symbol)"/>"""

class DojoValidationTextBox(DojoTextBox):
    require = ['dijit.form.ValidationTextBox']
    dojoType = 'dijit.form.ValidationTextBox'
    constraints = None
    invalidMessage = None
    #params = {'onClick':'the onClick method','title':'Button title','attrs':'Additional attributes for the widget'}
    params = ['attrs','lowercase','maxlength','propercase','size','trim','uppercase','name','style','required','value','cssclass',
    'dojoType','id','constraints','invalidMessage','promptMessage','rangeMessage','regExp']

    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,title=title,lowercase=lowercase,maxlength=maxlength,propercase=propercase,size=size,
    trim=trim,uppercase=uppercase,name=name,style=style,required=required,value=value,constraints=constraints,
    invalidMessage=invalidMessage,promptMessage=promptMessage,rangeMessage=rangeMessage,regExp=regExp)"/>"""

class DojoCheckbox(DojoBase):
    require = ['dijit.form.Checkbox']
    dojoType = 'dijit.form.Checkbox'
    checked = None
    params = ['attrs','size','name','style','value','cssclass','dojoType','id','checked']

    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,size=size,name=name,style=style,value=value,checked=checked)"/>"""

class DojoRadioButton(DojoBase):
    require = ['dijit.form.RadioButton']
    dojoType = 'dijit.form.RadioButton'
    checked = None
    params = ['attrs','size','name','style','value','cssclass','dojoType','id','checked']
    template ="""
    <input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id='${id}'
    class="${cssclass}" dojoType='${dojoType}' type="text"
    py:attrs="dict(attrs,size=size,name=name,style=style,value=value,checked=checked)"/>"""

class DojoInlineEditFarm(DojoBase):
    dojoType = 'dijit.InlineEditBox'
    engine_name = 'genshi'
    upload_url = ''
    object_type = ''
    params = ["update_url", "object_type","object_id", "object_type", "field", "value", "editor", "editorParams",
            "onChange", "autoSave", "style", "attrs"]
    js_params = ["update_url", "object_type"]
    #dojo_update_values = DojoUpdateValues
    value = ''
    required = 'false'
    style = ''
    onChange = 'updateValue'
    autoSave = ''
    field = ''
    editor = ''
    regExp = ''
    promptMessage = ''
    invalidMessage = ''
    object_type = ''
    attrs = {}
    template = """
    <span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id="${object_type}_${object_id}_${field}"
    editorParams="${editorParams}" py:attrs="dict(attrs,editor=editor,style=style,autoSave=autoSave,dojoType=dojoType)"
    onChange="${onChange}('${update_url}','${object_type}','${object_id}','${field}',this.value)">${value}
    </span>"""
    def __init__(self,**kw):
        super(DojoInlineEditFarm, self).__init__(**kw)
        d = {}
        for param in self.js_params:
            value = getattr(self, param)
            if value is not None:
                d[param] = getattr(self, param)
        self.dojo_update_js = DojoUpdateValues(update_url=kw.get('update_url'),object_type=kw.get('object_type'))
        self.javascript.append(self.dojo_update_js)
        #self.onChange = 'updateValue'

    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
            if isinstance(value, bool):
                d[param] = str(value).lower()
        super(DojoInlineEditFarm, self).update_params(d)

class DojoFilteringSelect(DojoBase):
    """DojoFilteringSelect is a drop-down field with autocomplete built from a DojoDataStore
    ${SampleFilteringSelect(id='sample',store='store',searchAttr='label',onChange='alert(this.value);')}
    """
    require = ['dijit.form.FilteringSelect']
    dojoType = 'dijit.form.FilteringSelect'
    searchAttr = None
    required = 'false'
    value = None
    style = None
    onChange = None
    params = {'onChange':'the onChange method','required':'Specify if required','value':'initial value',
        'style':'CSS style'}
    template = """<input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id="${id}" dojoType="${dojoType}"
    py:attrs="dict(attrs,style=style,searchAttr=searchAttr,name=name,value=value,store=store,onChange=onChange,required=required)" />"""

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
