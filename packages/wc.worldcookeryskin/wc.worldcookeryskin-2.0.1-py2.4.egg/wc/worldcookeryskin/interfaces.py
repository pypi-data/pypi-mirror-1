from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.interfaces import IViewletManager

class IWorldCookeryLayer(IBrowserRequest):
    """Skin layer that contains skin elements common to all
    WorldCookery applications"""

class IHeaders(IViewletManager):
    """Viewlets for the HTML header"""

class IToolbar(IViewletManager):
    """Viewlets for the toolbar (e.g. tabs and actions)"""

class ISidebar(IViewletManager):
    """Viewlets for the sidebar (e.g. add menu)"""

class IFooter(IViewletManager):
    """Viewlets for the footer (e.g. colophon)"""
