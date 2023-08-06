
import logging
logger = logging.getLogger('plone.app.gloworm')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.warning("plone.app.gloworm has been deprecated. Please use Products.Gloworm instead.")