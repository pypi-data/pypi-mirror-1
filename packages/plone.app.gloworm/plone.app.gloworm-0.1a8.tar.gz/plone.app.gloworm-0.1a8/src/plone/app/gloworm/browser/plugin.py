from kss.core import CommandSet
from interfaces import IGloWormCommands
from zope.interface import implements

import logging
logger = logging.getLogger('plone.app.gloworm')

class GloWormCommands(CommandSet):
    implements(IGloWormCommands)
    
    def resizePanel(self):
        """ Update the size of the GloWorm panel (and page content wrapper) to fit its current contents. """
        command = self.commands.addCommand('resizePanel')
        logger.debug("in GloWormCommands.resizePanel")
        
    def scrollNavTree(self, selector):
        """ Scroll the nav tree to show the selected element
        """
        command = self.commands.addCommand('scrollNavTree', selector)
        logger.debug("in GloWormCommands.scrollNavTree")
        return "bar"
        