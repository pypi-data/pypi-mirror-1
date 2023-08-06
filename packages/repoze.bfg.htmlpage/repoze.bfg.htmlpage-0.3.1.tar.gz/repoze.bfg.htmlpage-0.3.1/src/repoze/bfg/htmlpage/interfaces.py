from zope import interface

class IHTMLPage(interface.Interface):
    slots = interface.Attribute(
        """Slot names.""")

    attributes = interface.Attribute(
        """Element attributes.""")

    def render(content, attributes, **kwargs):
        """Renders the template, inserting content into the slots. The
        ``content`` parameter must be a dictionary mapping slot names
        to unicode strings (document content). To have resources
        automatically rebased, ``context`` and ``request`` must also
        be passed as keyword arguments."""

    def get_resource(path):
        """Return file stream for the resource located at ``path``
        (which is relative to the location of the template file)."""

class ITemplateDirectory(interface.Interface):
    """A template directory represents a file-system directory which
    contains dynamic HTML pages (.html files). This class provides
    dict-like access to them using the template name as key."""

