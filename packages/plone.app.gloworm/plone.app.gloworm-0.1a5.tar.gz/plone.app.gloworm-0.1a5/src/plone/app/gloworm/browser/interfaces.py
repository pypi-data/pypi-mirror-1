from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager, IViewlet
from plone.theme.interfaces import IDefaultPloneLayer

class IGlowormPanel(IViewletManager):
    """A viewlet manager that displays the gloworm panel
    """
    pass
    
class IInspectorView(Interface):
    pass

class IGloWormCommands(Interface):
    def resizePanel(self):
        """ Update the size of the GloWorm panel (and page content wrapper) to fit its current contents. """