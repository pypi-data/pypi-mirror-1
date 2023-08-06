from zope import component

from zope.configuration import xmlconfig
import zope.configuration.config

from zope.component.zcml import handler
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject, Path
from zope.interface import Interface
from zope.schema import TextLine

from repoze.bfg.interfaces import IRequest

from interfaces import ITemplateDirectory
from template import TemplateDirectory

class IHTMLPageDirective(Interface):
    directory = Path(
        title=u"Directory",
        description=u"""
        Path to the directory containing the templates.""",
        required=True
        )

    for_ = GlobalObject(
        title=u"The interface or class the layouts are for.",
        required=False
        )

    request_type = GlobalObject(
        title=u"""The request type interface for the view""",
        description=(u"The view will be called if the interface represented by "
                     u"'request_type' is implemented by the request.  The "
                     u"default request type is repoze.bfg.interfaces.IRequest"),
        required=False
        )    

def htmlpage(_context, directory, for_=None, request_type=IRequest):
    _context.action(
        discriminator = ('htmlpage', directory, for_, request_type),
        callable = handler,
        args = ('registerAdapter',
                TemplateDirectory(directory),
                (for_, request_type), ITemplateDirectory, directory,
                _context.info),
        )

