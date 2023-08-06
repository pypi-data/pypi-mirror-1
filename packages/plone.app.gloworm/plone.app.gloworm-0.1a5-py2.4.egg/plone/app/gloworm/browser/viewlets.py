from zope.publisher.base import DebugFlags
from zope.viewlet.interfaces import IViewletManager
from zope.component import getMultiAdapter

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.interface import implements
import re
from plone.app.gloworm.browser.interfaces import IInspectorView
from Globals import DevelopmentMode

class InspectorView(BrowserView):
    implements(IInspectorView)
    template = ViewPageTemplateFile('glowormView.pt')
    glowormPanelTemplate = ViewPageTemplateFile('glowormPanel.pt')
    
    def __call__(self):
        if DevelopmentMode:
            self.portal_type = self.context.getPortalTypeName()
            context_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_context_state')
            self.template_name = context_state.view_template_id()
            
            self.request.debug = DebugFlags()
            self.request.debug.showTAL = True
            # self.request.debug.sourceAnnotations = True
            # return self.template(self.context, self.request)
            renderedTemplate = self.template(self.context, self.request)
            
            # Insert the GloWorm panel and wrap the page content in a wrapper div so that we
            # can break the two into two different panels. To do that, we're forced to
            # do some ill-conceived html parsing. BeautifulSoup appears to be changing pages
            # with the TAL included, closing some tags that it shouldn't be and that breaks
            # the page layout. Javascript methods do the same. So, for now, we're stuck with
            # REGEX.
            
            glowormPanel = self.glowormPanelTemplate(self.context, self.request)
            regexp = r"(\</?body[^\>]*\>)([\S\s]*)(</body>)"
            replace = r"""
            \1
            %s
            <div id='glowormPageWrapper'>
            \2
            </div> <!-- Close glowormPageWrapper -->
            \3""" % glowormPanel
            updatedTemplate = re.sub(regexp, replace, renderedTemplate)
            
            return updatedTemplate
        else:
            return "Please enable Zope debug/development mode to continue."
    
    def saveTemplateEdits(self, viewlet):
        logger.debug("saving template edits for viewlet %s" % viewlet)

class GlowormPanelHeader(ViewletBase):
    render = ViewPageTemplateFile('glowormPanelHeader.pt')
    
    def update(self):
        self.close_url = self.context.absolute_url()

class GlowormPanelBody(ViewletBase):
    render = ViewPageTemplateFile('glowormPanelBody.pt')
    
    def update(self):
        self.portal_type = self.context.getPortalTypeName()
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
