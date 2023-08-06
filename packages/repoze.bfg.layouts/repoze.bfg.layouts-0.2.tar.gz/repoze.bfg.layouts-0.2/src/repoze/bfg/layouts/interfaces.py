from zope import interface

class ILayout(interface.Interface):
    slots = interface.Attribute(
        """Slot names.""")

    attributes = interface.Attribute(
        """Element attributes.""")

    def render(content, attributes, **kwargs):
        """Renders the layout, inserting content into the slots. The
        ``content`` parameter must be a dictionary mapping slot names
        to unicode strings (document content). To have resources
        automatically rebased, ``context`` and ``request`` must also
        be passed as keyword arguments."""

    def get_resource(path):
        """Return file stream for the resource located at ``path``
        (which is relative to the location of the layout file)."""

class ILayoutDirectory(interface.Interface):
    """A layout directory represents a file-system directory which
    contains dynamic layouts (.html files). This class provides
    dict-like access to layouts using the layout name as key."""

