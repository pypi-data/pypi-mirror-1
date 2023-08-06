"""
dijit widgets
"""
from tw.dojo.core import DojoBase
from tw.core import CSSLink

dijit_css = CSSLink(
    modname = 'tw.dojo',
    filename = 'static/dijit/themes/dijit.css'
)

class DojoProgressBar(DojoBase):
    require = ['dijit.ProgressBar']
    dojoType = 'dijit.ProgressBar'
    params = ['id', 'jsId']
    store = None
    rootLabel = None
    childrenAttrs = None
    onClick = None
    template = """
    <span xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" py:strip="">
    <div dojoType="dijit.ProgressBar"
         jsId="$jsId" id="$id"></div>
    </span>"""
