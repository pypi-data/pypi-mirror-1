from zope.publisher.base import DebugFlags
from zope.component import getMultiAdapter

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.interface import implements
import re
from plone.app.gloworm.browser.interfaces import IInspectorView
from plone.app.gloworm.browser.utils import findTemplateViewRegistrationFromHash, getProvidedForViewlet, hashViewletInfo
from zope.viewlet.interfaces import IViewlet, IViewletManager
from zope.component import queryMultiAdapter
from BeautifulSoup import BeautifulSoup
from Globals import DevelopmentMode
from zope.component import getAdapters

import logging
logger = logging.getLogger('plone.app.gloworm')

class InspectorView(BrowserView):
    implements(IInspectorView)
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
            renderedTemplate = self.context()
            # xmldec = """<?xml version="1.0" encoding="UTF-8" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-us" lang="en-us"
            #       xmlns:metal="http://xml.zope.org/namespaces/metal"
            #       xmlns:tal="http://xml.zope.org/namespaces/tal" ?>
            # <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            # """
            # renderedTemplate = xmldec + renderedTemplate
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

class GlowormPanelNavTree(ViewletBase):
    render = ViewPageTemplateFile('glowormPanelNavTree.pt')
    def update(self):
        
        # Tell BeautifulSoup that viewlets and viewletmanagers can be nested.
        BeautifulSoup.NESTABLE_TAGS['tal:viewlet']=['tal:viewletmanager']
        BeautifulSoup.NESTABLE_TAGS['tal:viewletmanager']=['tal:viewlet']
        
        # Render the current page and strip out everything but the <tal:viewletmanager> and <tal:viewlet> tags.
        # TODO We probably don't need BeautifulSoup anymore since we've got such a simple parsetree.
        strippedHTML = ''.join((re.findall('(<\/?tal:viewlet/?[^\>]*>)', self.context())))
        
        # Soupify the simplified HTML
        soup = BeautifulSoup(strippedHTML)
        self.documentTree = []
        self.outstr = ""
        
        def getChildViewletManagers(node):
            """ Find all viewletmanagers within this node """
            all = node.findAll('tal:viewletmanager')
            stripped = []
            self.outstr += "<ul class='viewletmanager-tree'>"
            for v in all:
                if not(stripped and v.findParent('tal:viewletmanager') and stripped[-1] in v.findParents('tal:viewletmanager')):
                    rawname = v.attrs[0][1][27:] # 27 = len('kssattr-viewletmanagername-')
                    name = rawname.replace('-','.')
                    self.outstr += "<li><a href='#' class='inspectViewletManager kssattr-forviewletmanager-%s'>%s</a>" % (name.replace('.', '-'), name)
                    # Get the viewletmanager object
                    managerObj = queryMultiAdapter((self.context, self.request, self), IViewletManager, name)
                    # Look up the viewlets attached to this viewlet manager.
                    # We do it this way because calling viewletManager.viewlets won't see the hidden viewlets...
                    containedViewlets = getAdapters((self.context, self.request, managerObj.__parent__, managerObj),IViewlet)
                    containedViewlets = managerObj.sort([vl for vl in containedViewlets])
                    
                    stripped.append(v)
                    getChildViewlets(v, containedViewlets)
                    self.outstr += "</li>"
            self.outstr += "</ul>"
            return stripped
        
        def getChildViewlets(node, allViewlets=[]):
            """ Find all viewlets within this node """
            all = node.findAll('tal:viewlet')
            stripped = []
            self.outstr += "<ul class='viewlet-tree'>"
            
            def writeHiddenViewlet(viewlet):
                """ Create a list item HTML bit for a hidden viewlet """
                name = viewlet[0]
                managerObj = viewlet[1].manager
                viewletHash = hashViewletInfo(name, managerObj.__name__, getProvidedForViewlet(name, managerObj))
                return "<li><a href='#' class='viewletMoreInfo hiddenViewlet kssattr-forviewlet-%s'>%s</a></li>" % (viewletHash, name)
            
            for v in all:
                if not(stripped and v.findParent('tal:viewlet') and stripped[-1] in v.findParents('tal:viewlet')):
                    viewletHash = v.attrs[0][1][20:] # 20 = len('kssattr-viewlethash-')
                    reg = findTemplateViewRegistrationFromHash(viewletHash)
                    while allViewlets and reg.name != allViewlets[0][0]:
                        self.outstr += writeHiddenViewlet(allViewlets[0])
                        allViewlets.pop(0)
                    allViewlets.pop(0) # Remove the current viewlet from the allViewlets list
                    self.outstr += "<li><a href='#' class='viewletMoreInfo kssattr-forviewlet-%s'>%s</a>" % (viewletHash, reg.name)
                    stripped.append(v)
                    getChildViewletManagers(v)
                    self.outstr += "</li>"
            # Collect any remaining hidden viewletss
            if allViewlets:
                for vlt in allViewlets:
                    self.outstr += writeHiddenViewlet(vlt)
            self.outstr += "</ul>"
            return stripped
        
        getChildViewletManagers(soup)
