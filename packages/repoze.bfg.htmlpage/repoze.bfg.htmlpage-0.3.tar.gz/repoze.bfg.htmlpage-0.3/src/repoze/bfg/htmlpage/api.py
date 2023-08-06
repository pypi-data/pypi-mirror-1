from zope import component

from repoze.bfg.skins.template import SkinApi

from repoze.bfg.htmlpage.template import get_htmlpage
from repoze.bfg.htmlpage.interfaces import IHTMLPage
from chameleon.core.template import Macro

class HTMLPageApi(SkinApi):
    """HTML-page helper."""
    
    def __call__(self, name=None):
        if name is not None:
            htmlpage = get_htmlpage(self.context, self.request, name)
        else:
            htmlpage = component.getMultiAdapter(
                (self.context, self.request), IHTMLPage)

        def render(**kwargs):
            return htmlpage.template.render_macro(
                "", global_scope=False, parameters=kwargs)
        
        return Macro(render)
