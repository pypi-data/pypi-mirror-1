import logging
logger = logging.getLogger('plone.app.gloworm')
#from Products.GenericSetup import EXTENSION, profile_registry
#from Globals import DevelopmentMode
#from Globals import package_home
#import Products.CMFPlone.interfaces
#
#
#
def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    # Monkey patch Products.PageTemplates.PageTemplate.PageTemplate so that we can use the showTAL debug flag.
    # At some point this might not be necessary if https://bugs.launchpad.net/zope2/+bug/229549
    # is accepted.
    
    def pt_render(self, source=False, extra_context={}):
        c = self.pt_getContext()
        c.update(extra_context)
        # Fix would belong here...
        debug = getattr(c['request'], 'debug', None)
        if debug is not None:
            showtal = getattr(debug, 'showTAL', False)
            sourceAnnotations = getattr(debug, 'sourceAnnotations', False)
        else:
            showtal = sourceAnnotations = False
        return super(PageTemplate, self).pt_render(c, source=source, sourceAnnotations=sourceAnnotations,
                   showtal=showtal)

    from Products.PageTemplates.PageTemplate import PageTemplate
    PageTemplate.pt_render = pt_render
    logger.info('PageTemplate.pt_render Monkey patch installed.')



    from zope.interface import implements
    from zope.component import getUtility, getAdapters, queryUtility, getMultiAdapter, queryMultiAdapter, getSiteManager
    
    from zope.viewlet.interfaces import IViewlet
    from zope.contentprovider.interfaces import IContentProvider
    from zope.publisher.interfaces.browser import IBrowserRequest
    
    from zope.interface import providedBy
    
    from Acquisition import aq_base
    from AccessControl.ZopeGuards import guarded_hasattr
    from Products.Five import BrowserView
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    
    from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
    from plone.app.viewletmanager.interfaces import IViewletManagementView
    
    from plone.app.customerize import registration
    from five.customerize.interfaces import ITTWViewTemplate
    from zope.viewlet.interfaces import IViewletManager
    
    from cgi import parse_qs
    from urllib import urlencode
    import binascii

    def render(self):
        if self.template:
            print "skipping viewlet tag for %s" % self.__name__
            return self.template(viewlets=self.viewlets)
        else:
            outstr = ""
            for_name=u"zope.interface.Interface" # TODO: hardcoded!
            try:
                type_name = list(providedBy(self).flattened())[0].__identifier__
            except: # TODO make this more specific
                type_name = u""
            manager_name = self.__name__
            outstr += "<tal:viewletmanager class='kssattr-viewletmanagername-%s'>" % manager_name.replace('.', '-')
            for viewlet in self.viewlets:
                # customized viewlet TTWViewletRenderer don't have a __name__ attached, grab it from the template id
                if hasattr(viewlet, '__name__'):
                    view_name = viewlet.__name__
                else:
                    view_name = viewlet.template.id.split('-')[-1]
                hashedInfo = binascii.b2a_hex("%s\n%s\n%s\n%s" % (for_name, type_name, view_name, manager_name))
                outstr += u"<tal:viewlet class='kssattr-viewlethash-%s'>\n%s\n</tal:viewlet>\n" % (hashedInfo, viewlet.render())
            outstr += "</tal:viewletmanager>"
            return outstr

    from plone.app.viewletmanager.manager import BaseOrderedViewletManager
    BaseOrderedViewletManager.render = render
    logger.info('BaseOrderedViewletManager.render monkey patch installed.')

    #    logger.info('Initializing Product')
    #    # Only register gloworm parts if debug mode is active.
    #    if DevelopmentMode:
    #        logger.info('Debug Mode active, registering profile.')
    #
    #        profile_registry.registerProfile( 
    #            name='default', 
    #            title=u'GloWorm', 
    #            description=u'Extension profile for plone.app.gloworm.', 
    #            path='profiles/default', 
    #            product='plone.app.gloworm', 
    #            profile_type=EXTENSION, 
    #            for_=Products.CMFPlone.interfaces.IPloneSiteRoot) 
    #
    #    else:
    #        # do an uninstall profile?
    #        logger.info('Debug Mode not active, unregistering profile.')
