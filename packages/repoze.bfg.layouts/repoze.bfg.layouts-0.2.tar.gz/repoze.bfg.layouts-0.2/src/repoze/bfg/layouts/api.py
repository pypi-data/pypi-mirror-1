from zope import component

from repoze.bfg.skins import TemplateAPI
from repoze.bfg.layouts import get_layout
from repoze.bfg.layouts.interfaces import ILayout
from chameleon.core.template import Macro
from copy import copy

class LayoutAPI(TemplateAPI):
    """Layout API; may be bound to a layout by using the call-method,
    otherwise a component lookup is attempted."""

    name = None
    
    def __call__(self, name):
        layout = copy(self)
        layout.name = name
        return layout

    @property
    def layout(self):
        # if the API has not been bound to a layout name, look up the
        # layout as a component, adapting on context and request
        if self.name is not None:
            return get_layout(self.context, self.request, self.name)
        
        return component.getMultiAdapter(
            (self.context, self.request), ILayout)
        
    @property
    def macro(self):
        """Return template macro."""

        def render(**kwargs):
            return self.layout.template.render_macro(
                "", global_scope=False, parameters=kwargs)
        
        return Macro(render)
