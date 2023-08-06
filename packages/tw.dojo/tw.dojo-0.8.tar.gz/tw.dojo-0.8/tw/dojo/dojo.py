"""
Dojo 1.1 widget for ToscaWidgets

To download and install::

  easy_install tw.dojo

"""
from tw.api import Resource, Link ,JSLink, JSSource, CSSLink, CSSSource, Widget, js_function, locations
from tw.api import RequestLocalDescriptor
from tw.core.resources import JSDynamicFunctionCalls 
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

dojo_css = CSSLink(
    modname = __name__, 
    filename = 'static/dojo/resources/dojo.css',
    )

dijit_dir = Link(
    modname = __name__, 
    filename = 'static/dijit/',
    )

dojox_dir = Link(
    modname = __name__, 
    filename = 'static/dojox/',
    )

tundra_css = CSSLink(
    modname = __name__, 
    filename = 'static/dijit/themes/tundra/tundra.css',
    )

class DojoRequireCalls(JSDynamicFunctionCalls): 
    location = "head" 
    javascript = [dojo_js] 
    # This is an attribute which can hold requirements in a request-local 
    # set. anything added here will only be visible in the current request 
    _require = RequestLocalDescriptor("dojo_require_calls", default=set()) 
    def call_getter(self,location): 
        # return dojo.require calls. This is called by the superclass 
        return map(js_function('dojo.require'), self._require) 
    def require(self, requirement): 
        # Called by dojo widgets which want to inject a requirement 
        self._require.add(requirement)
        # Inject ourselves into the page fisrt time we're called (we can inject 
        # ourselves many times but only will get rendered once 
        self.inject()

dojo_require = DojoRequireCalls("dojo_require")

class Dojo(Widget):
    _resource = [dijit_dir,dojox_dir]
    css = [dojo_css,tundra_css]
    #javascript = [dojo_js]

dojo =Dojo()
class DojoUpdateValues(JSSource):
    _resource = []
    update_url = ''
    object_type = ''
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
    template_engine = "genshi"
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
    require = []
    dojoType = ''
    engine_name = 'genshi'
    template = ''
    id = ''
    params = {'dojoType':'The dojo type of specified widget','id': 'Id of created widget'}

    def update_params(self, d): 
        super(DojoBase, self).update_params(d)
        for r in self.require:
            dojo_require.require(r)

class DojoButton(DojoBase):
    require = ['dijit.form.Button']
    dojoType = 'dijit.form.Button'
    onClick = ''
    title = ''
    params = {'onClick':'the onClick method','title':'Button title'}
    template = "<div id='${id}' dojoType='${dojoType}' onClick='${onClick}'>${title}</div>"
    


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
    template = """<span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id="${object_type}_${object_id}_${field}"
    editorParams="${editorParams}" py:attrs="dict(attrs,editor=editor,style=style,autoSave=autoSave,dojoType=dojoType)"
    onChange="${onChange}('${update_url}','${object_type}','${object_id}','${field}',this.value)">${value}</span>"""
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
        
class DojoDataStore(DojoBase):
    url = ''
    params = {'url':'url of remote data'}

class DojoItemFileReadStore(DojoDataStore):
    require = ['dojo.data.ItemFileReadStore']
    dojoType = 'dojo.data.ItemFileReadStore'
    template = """<div dojoType="${dojoType}" jsId="${id}" url="${url}"/>"""
    
class DojoItemFileWriteStore(DojoDataStore):
    require = ['dojo.data.ItemFileWriteStore']
    dojoType = 'dojo.data.ItemFileWriteStore'
    template = """<div dojoType="${dojoType}" jsId="${id}" url="${url}"/>"""

class DojoFilteringSelect(DojoBase):
    require = ['dijit.form.FilteringSelect']
    dojoType = 'dijit.form.FilteringSelect'
    searchAttr = None
    required = 'false'
    value = None
    style = None
    onChange = None
    params = {'onChange':'the onChange method','required':'Specify if required','value':'initial value','style':'CSS style'}
    template = """<input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id="${id}" dojoType="${dojoType}" 
    py:attrs="dict(style=style,searchAttr=searchAttr,name=name,value=value,store=store,onChange=onChange,required=required)" />"""
    
    
class DojoGridOld(DojoBase):
    require = ['dojox.grid.Grid']
    dojoType = 'dojox.grid.Grid'
    params = ['style','name', 'query', 'clientSort']
    style = None
    name = None
    query = None
    clientSort = 'true'
    columns = []
    template = """<table xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" id="${id}" dojoType="${dojoType}"
    py:attrs="dict(style=style,name=name,store=store,query=query,clientSort=clientSort)"> 
    <thead> 
    <tr><th py:for="column in columns" field="${column.column_name}" py:attrs="column.attrs">${column.column_label}</th></tr> 
    </thead></table>"""
    
class DojoGrid(DojoBase):
    require = ['dojox.grid.Grid']
    dojoType = 'dojox.grid.Grid'
    params = ['style','name', 'query', 'clientSort']
    style = None
    name = None
    query = None
    clientSort = 'true'
    columns = []
    include_dynamic_js_calls = True
    template = """<span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip=""> 
    <script type="text/javascript">structure_${id}=${columns}</script>
    <div id="${id}" dojoType="${dojoType}"
    py:attrs="dict(attrs,style=style,name=name,store=store,query=query,clientSort=clientSort)" structure="structure_${id}"/></span>
    """
    
    def update_params(self, d):
        super(DojoGrid, self).update_params(d)
        #d['columns']=turbojson.jsonify.encode([dict(cells=d.columns)])
        d['columns']=grid_params(cells=d.columns)
        
class DojoGridColumn(dict):
    pass
    
def grid_params(*args,**kwargs):
    escape_int=['editor','formatter']
    cells=kwargs.pop('cells',[])
    out=''
    cols=[]
    cols_str=''
    for cellgroup in cells:
        cellgroup_list_str=''
        cellgroup_list=[]
        for cell in cellgroup:
            single_str=''
            single=[]
            for key in cell.keys():
                key_str=key+':'
                if key in escape_int:
                    key_str+=cell[key]
                else:
                    key_str+="'"+cell[key]+"'"
                key_str=key_str
                single.append(key_str)
            single_str=','.join(single)
            single_str='{'+single_str+'}'
            cellgroup_list.append(single_str)
        cellgroup_list_str=','.join(cellgroup_list)
        cellgroup_list_str='['+cellgroup_list_str+']'
        cols.append(cellgroup_list_str)
    cols_str=','.join(cols)
    cols_str='['+cols_str+']'
    others=[]
    out='[{cells:'+cols_str+'}]'
    print out
    return out