import os

from zope import interface
from zope import component

import interfaces

from chameleon.html import template

class Layout(object):
    interface.implements(interfaces.ILayout)
    
    def __init__(self, filename):
        self.template = template.DynamicHTMLFile(filename)
        self.filename = filename
        self.path = os.path.dirname(filename)
        
    def __repr__(self):
        return '<Layout filename="%s">' % self.template.filename

    @property
    def slots(self):
        return tuple(self.template.parser.slots)

    @property
    def attributes(self):
        return tuple(self.template.parser.attributes)

    def get_resource(self, path):
        try:
            return file(os.path.join(self.path, path))
        except IOError:
            raise IOError(
                "Unable to locate resource %s referenced in layout %s." % (
                repr(path), repr(self.filename)))
            
    def render(self, content, attributes, **kwargs):
        return self.template(content=content, attributes=attributes, **kwargs)

class LayoutDirectory(object):
    interface.implements(interfaces.ILayoutDirectory)

    def __init__(self, path):
        self.path = path
        self.registry = {}
         
    def __repr__(self):
        return '<LayoutDirectory files="%d">' % len(self.registry)

    def __call__(self, context, request):
        """Allows using this class as an adapter."""

        return self
    
    def __getitem__(self, name):
        layout = self.registry.get(name)
        if layout is not None:
            return layout

        # since the layout was not yet initialized, create a new
        # layout (if the filename is found in this directory)
        filename = os.path.join(self.path, "%s.html" % name)
        if os.path.exists(filename):
            layout = Layout(filename)
            self.registry[name] = layout
            return layout
        
        raise KeyError(name)

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

def get_layout(context, request, name):
    """Search layout directories for a layout with the specified
    name. First match is returned."""

    for component_name, directory in component.getAdapters(
        (context, request), interfaces.ILayoutDirectory):
        layout = directory.get(name)
        if layout is not None:
            return layout
    raise component.ComponentLookupError(
        "No such layout: %s." % repr(name))
