# Copyright 2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD License derivative - see egg-info
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.interface import Interface
from zope.component.zcml import handler
from zope.schema import TextLine
from zope.configuration.fields import Path
from zope.security.checker import CheckerPublic
from zope.security.checker import NamesChecker
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.publisher.browser.metadirectives import IBasicResourceInformation
from zope.app.publisher.browser.resourcemeta import allowed_names
from cornerstone.cssvar.interfaces import ICSSVariables
from cornerstone.cssvar.browser import CSSResourceFactory
from cornerstone.cssvar.browser import CSSVarDefFactory

class ICSSDirective(IBasicResourceInformation):
    """
    Defines a browser css resource with variable expansion
    """

    name = TextLine(
        title=u"The name of the resource",
        description=u"""
        This is the name used in css-resource urls. CSS-Resource urls are of
        the form site/@@/resourcename, where site is the url of
        "site", a folder with a site manager.

        We make css-resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=True)

    file = Path(
        title=u"CSS File",
        description=u"The file containing the CSS.",
        required=False)

class ICSSVarDefDirective(IBasicResourceInformation):
    """
    Defines a browser css resource with variable expansion
    """

    name = TextLine(
        title=u"The name of the resource",
        description=u"""
        This is the name used in css-resource urls. CSS-Resource urls are of
        the form site/@@/resourcename, where site is the url of
        "site", a folder with a site manager.

        We make css-resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=True)

    file = Path(
        title=u"CSS File with variable definitions",
        description=u"The file containing the CSS.",
        required=False)

def css(_context, name, layer=IDefaultBrowserLayer, permission='zope.Public', 
        file=None):
    if permission == 'zope.Public':
        permission = CheckerPublic
    checker = NamesChecker(allowed_names, permission)
    factory = CSSResourceFactory(file, checker, name)
    _context.action(
        discriminator=('css', name, IBrowserRequest, layer),
        callable=handler,
        args=('registerAdapter', factory, (layer,), Interface, name, 
              _context.info),
    )
    
def cssdef(_context, name, layer=IDefaultBrowserLayer, permission='zope.Public', 
          file=None):
    if permission == 'zope.Public':
        permission = CheckerPublic
    checker = NamesChecker(allowed_names, permission)
    factory = CSSVarDefFactory(file, checker, name)
    _context.action(
        discriminator=('css', name, IBrowserRequest, layer),
        callable=handler,
        args=('registerAdapter', factory, (layer,), ICSSVariables, name, 
              _context.info),
    )