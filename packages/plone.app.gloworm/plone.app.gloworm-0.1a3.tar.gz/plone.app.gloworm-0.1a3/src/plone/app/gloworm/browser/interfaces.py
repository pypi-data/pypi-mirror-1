from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager, IViewlet


class IGlowormPanel(IViewletManager):
    """A viewlet manager that displays the gloworm panel
    """
    pass
    
class IInspectorView(Interface):
    pass