from zope.component import getAdapters
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implements, providedBy
from five.customerize.interfaces import IViewTemplateContainer
from plone.app.customerize import registration
from plone.portlets.utils import unhashPortletInfo
from zope.viewlet.interfaces import IViewlet, IViewletManager
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView as base
from Acquisition import aq_inner
import binascii

import logging
logger = logging.getLogger('plone.app.gloworm')


class InspectorKSS(base):
    implements(IPloneKSSView)

    def inspectElement(self,
                      insideglowormpanel=False,
                      talcontent=None,
                      talattributes=None,
                      talcondition=None,
                      metaldefmacro=None,
                      metalusemacro=None,
                      fieldname=None,
                      portlethash=None,
                      viewlethash=None):
        """ Get details about a particular html element. """
        # Make sure we're not clicking inside the inspector div since KSS doesn't seem to provide a 
        # way to block processing of other rules.
        if not insideglowormpanel:
            logger.debug("in inspectElement")
            ksscore = self.getCommandSet('core')
            
            out = "<table>"
            out += "<tr><td>skin name:</td><td>%s</td></tr>" % self.context.getCurrentSkinName()
            if metalusemacro:
                out += "<tr><td>in macro:</td><td>%s</td></tr>" % metalusemacro
            if metaldefmacro:
                out += "<tr><td>defines macro:</td><td>%s</td></tr>" % metaldefmacro
            if fieldname:
                out += "<tr><td>field name:</td><td>%s</td></tr>" % fieldname
            if talcontent:
                out += "<tr><td>tal-content:</td><td>%s</td></tr>" % talcontent
            if talattributes:
                out += "<tr><td>tal-attributes:</td>"
                out += "<td><table><tr><th>Attribute</th><th>Expression</th><th>Result</th></tr>"
                logger.debug("attr: %s" % talattributes)
                for a in talattributes.split(';'):
                    logger.debug("a: %s" % a)
                    if a:
                        att, expr = a.strip().split(' ', 1)
                        # TODO: How do we get at the html attrs from inside our KSS methods?
                        #result = ksscore.nodeAttr(ksscore.getSameNodeSelector(), att)
                        result = ""
                        logger.debug("result: %s" % result)
                        out += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (att, expr, result)                
                out += "</table></td></tr>"
            if talcondition:
                out += "<tr><td>tal-condition:</td><td>%s</td></tr>" % talcondition
            if portlethash:
                unhashedPortletInfo = unhashPortletInfo(portlethash) #manager, category, key, name
                out += "<tr><td>portlet:</td><td>portlet name: %s<br />portlet manager: %s</td></tr>" % (unhashedPortletInfo['name'], unhashedPortletInfo['manager'])
            if viewlethash:
                unhashedViewletInfo = self._unhashViewletInfo(viewlethash)
                out += "<tr><td>viewlet:</td><td><a href='#' class='viewletMoreInfo kssattr-forviewlet-%s'>%s</a></td></tr>" % (viewlethash, unhashedViewletInfo['view_name'])
            out += "</table>"
            
            # Dump the output to the inspector panel
            panel = ksscore.getCssSelector('#glowormPanelBody')
            ksscore.replaceInnerHTML(panel, out)
            
            # Remove highlights from previously-clicked elements
            ksscore.removeClass(ksscore.getCssSelector('.currentlySelectedElement'), 'currentlySelectedElement')
            # Highlight this element
            ksscore.addClass(ksscore.getSameNodeSelector(), 'currentlySelectedElement')
        
        return self.render()


    def inspectViewlet(self, viewlethash):
        """ Display detailed information about a particular viewlet. """
        logger.debug("in inspectViewlet")
        
        # Unhash the viewlet info
        unhashedViewletInfo = self._unhashViewletInfo(viewlethash)

        # Get the registration information for this viewlet
        reg = registration.findTemplateViewRegistration(unhashedViewletInfo['for_name'], unhashedViewletInfo['type_name'], unhashedViewletInfo['view_name'])
        viewRegistrationInfo = list(registration.templateViewRegistrationInfos([reg]))[0]
        template = viewRegistrationInfo['zptfile']
        cls = registration.getViewClassFromRegistration(reg)

        # Display it
        out = "<h4>Viewlet %s</h4><table>" % unhashedViewletInfo['view_name']
        out += "<tr><td>name:</td><td>%s</td></tr>" % unhashedViewletInfo['view_name']
        out += "<tr><td>manager:</td><td><a href='#' class='inspectViewletManager kssattr-forviewletmanager-%s'>%s</a></td></tr>" % (unhashedViewletInfo['manager'], unhashedViewletInfo['manager'])
        out += "<tr><td>class:</td><td>%s.%s</td></tr>" % (cls.__module__, cls.__name__)
        out += "<tr><td>template:</td><td>%s</td></tr>" % template
        
        out += "<tr><td colspan='2'><form>"
        
        container = queryUtility(IViewTemplateContainer)
        templateName = registration.generateIdFromRegistration(reg)
        if templateName in container:
            # customization exists
            out += '<input type="submit" value="Edit Customized Version" class="customizeViewlet kssattr-forviewlet-%s" />' % viewlethash
            out += '<input type="submit" value="Discard Customized Version" class="discardTemplateEdits kssattr-forviewlet-%s" />' % viewlethash
        else:
            out += '<input type="submit" value="Customize" class="customizeViewlet kssattr-forviewlet-%s" />' % viewlethash
        out += "</form></td></tr>"

        out += "</table>"

        # Dump the output to the output panel
        ksscore = self.getCommandSet('core')
        panel = ksscore.getCssSelector('#glowormPanelBody')
        ksscore.replaceInnerHTML(panel, out)

        # Remove highlights from previously-clicked elements
        ksscore.removeClass(ksscore.getCssSelector('.currentlySelectedElement'), 'currentlySelectedElement')
        # Highlight this element
        logger.debug('kssattr-viewlethash-%s' % viewlethash)
        ksscore.addClass(ksscore.getCssSelector('.kssattr-viewlethash-%s' % viewlethash), 'currentlySelectedElement')

        return self.render()

    def customizeViewlet(self, viewlethash):
        """ Display an edit form for modifiying a viewlet's template """
        logger.debug("in customizeViewlet")
        
        # Unhash the viewlet info
        unhashedViewletInfo = self._unhashViewletInfo(viewlethash)

        # Get the viewlet's registration information from portal_view_customizations
        container = queryUtility(IViewTemplateContainer)
        reg = registration.findTemplateViewRegistration(unhashedViewletInfo['for_name'], unhashedViewletInfo['type_name'], unhashedViewletInfo['view_name'])
        templateName = registration.generateIdFromRegistration(reg)

        # Check to see if the viewlet has already been customized. Get the template code accordingly.
        if templateName not in container.objectIds():
            viewzpt = registration.customizeTemplate(reg)
            sm = getSiteManager(self.context)
            sm.registerAdapter(viewzpt, required= reg.required, provided = reg.provided, name=reg.name)
        else:
            viewzpt = container[templateName]
        out = "<h4>Editing template at %s</h4>" % viewzpt.absolute_url()
        templateCode = viewzpt.read()
        # Display the edit form
        # TODO move this to a viewlet
        out += """
            <form>
                <textarea name="text:text" id="editableTemplateContent" rows="10">%s</textarea>
                <div style="text-align:right; margin: 1em;">
                    <input type="submit" value="Cancel" name="pt_editAction:method" class="cancelTemplateEdits kssattr-forviewlet-%s" />
                    <input type="submit" value="Discard Customizations" name="pt_editAction:method" class="discardTemplateEdits kssattr-forviewlet-%s" />
                    <input type="submit" value="Save" name="pt_editAction:method" class="saveTemplateEdits kssattr-forviewlet-%s" />
                </div>
            </form>
        """ % (templateCode, viewlethash, viewlethash, viewlethash)
        ksscore = self.getCommandSet('core')
        ksscore.replaceInnerHTML(ksscore.getCssSelector('#glowormPanelBody'), out)

        return self.render()
        
    def saveViewletTemplate(self, viewlethash, newContent):
        """ Update portal_view_customizations with the new version of the template. """
        logger.debug("in save_viewlet_template")

        # Unhash the viewlet info. Pull out what we need.
        unhashedInfo = self._unhashViewletInfo(viewlethash)
        viewletName = unhashedInfo['view_name']

        # FInd the template in portal_view_customizations, save the new version
        container = queryUtility(IViewTemplateContainer)
        templateName = 'zope.interface.interface-%s' % viewletName
        if templateName in container.objectIds():
            container[templateName].write(newContent)

        return self._renderCustomizedViewlet(viewlethash, templateName)

    def _renderCustomizedViewlet(self, viewlethash, templateName):
        """ Rerender the viewlet to show the new code """
        # Unhash the viewlet info. Pull out what we need.
        unhashedInfo = self._unhashViewletInfo(viewlethash)
        managerName = unhashedInfo['manager']
        viewletName = unhashedInfo['view_name']

        ksscore = self.getCommandSet('core')

        # Find the viewletmangager instance, tell it to update its rendering, and replace the contents of the selected div with that new html
        selector = ksscore.getCssSelector('.kssattr-viewletmanagername-' + managerName.replace('.', '-'))
        viewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, managerName)
        viewletManager.update()

        ksscore.replaceInnerHTML(selector, viewletManager.render())
        vlt = ksscore.getCssSelector('.kssattr-viewlethash-%s' % viewlethash)
        # Get the viewlet. 
        # TODO: Is there a better way to do this?
        for viewlet in viewletManager.viewlets:
            if hasattr(viewlet, 'template') and viewlet.template.__name__ == templateName:
                ksscore.replaceInnerHTML(vlt, viewlet.render())
                break
        return self.render()

    def discardViewletCustomizations(self, viewlethash):
        """ Remove the customized template for a particular viewlet """
        # Unhash the viewlet info
        unhashedViewletInfo = self._unhashViewletInfo(viewlethash)

        # Get the viewlet's registration information from portal_view_customizations
        container = queryUtility(IViewTemplateContainer)
        reg = registration.findTemplateViewRegistration(unhashedViewletInfo['for_name'], unhashedViewletInfo['type_name'], unhashedViewletInfo['view_name'])
        templateName = registration.generateIdFromRegistration(reg)
        
        container.manage_delObjects([templateName])
        self._renderCustomizedViewlet(viewlethash, templateName)
        return self.inspectViewlet(viewlethash)

    def inspectViewletManager(self, managerName):
        """ Display information about a particular viewlet manager """
        logger.debug("in inspectViewletManager")
        
        # Get the viewletmanager object 
        viewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, managerName)

        # Gather information for the viewlet hashes
        for_name="zope.interface.Interface" # TODO: hardcoded!
        managerInterface = list(providedBy(viewletManager).flattened())[0].__identifier__

        # Look up the viewlets attached to this viewlet manager. 
        # We do it this way because calling viewletManager.viewlets won't see the hidden viewlets...
        viewlets = getAdapters((viewletManager.context, viewletManager.request, viewletManager.__parent__, viewletManager),IViewlet)
        
        # Get the names of the hidden viewlets
        storage = getUtility(IViewletSettingsStorage)
        hidden = frozenset(storage.getHidden(managerName, self.context.getCurrentSkinName()))
        
        # Generate the output
        out = "<h4>Viewlet Manager %s</h4><table>" % managerName
        for viewletTuple in viewletManager.sort(viewlets):
            viewletname = viewletTuple[0]
            
            # generate viewlet hashes...
            # TODO factor this up.
            hashedInfo = binascii.b2a_hex("%s\n%s\n%s\n%s" % (for_name, managerInterface, viewletname, managerName))
            
            # Give the viewlet a class name depending on the visibility
            classname = viewletname in hidden and 'hiddenViewlet' or 'visibleViewlet'
            logger.debug(classname)
            
            out += "<tr class='%s kssattr-viewlethash-%s'>" % (classname, hashedInfo)
            out += """<td>
                        <a href='#' class='hideViewlet'><img src='portal_skins/GloWorm/lightbulb.png' /></a>
                        <a href='#' class='showViewlet'><img src='portal_skins/GloWorm/lightbulb_off.png' /></a>
                      </td>"""
            out += "<td><a href='#' class='viewletMoreInfo kssattr-forviewlet-%s'>%s</a></td>" % (hashedInfo, viewletname)
            out += "</tr>"
        out += "</table>"

        # Update the output panel
        ksscore = self.getCommandSet('core')
        panel = ksscore.getCssSelector('#glowormPanelBody')
        ksscore.replaceInnerHTML(panel, out)

        return self.render()

    def hide_viewlet(self, viewlethash):
        """ Hide the selected viewlet """
        logger.debug("in hide_viewlet")
        def updateHiddenList(hidden, view_name):
            return hidden + (view_name,)
        self._toggleVisibleState(viewlethash, updateHiddenList)
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('#glowormPanel .kssattr-viewlethash-%s' % viewlethash)
        ksscore.removeClass(selector, 'visibleViewlet')
        ksscore.addClass(selector, 'hiddenViewlet')
        return self.render()

    def show_viewlet(self, viewlethash):
        """ Show the selected viewlet """
        logger.debug("in hide_viewlet")
        def updateHiddenList(hidden, view_name):
            return tuple(x for x in hidden if x != view_name)
        self._toggleVisibleState(viewlethash, updateHiddenList)
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('#glowormPanel .kssattr-viewlethash-%s' % viewlethash)
        ksscore.removeClass(selector, 'hiddenViewlet')
        ksscore.addClass(selector, 'visibleViewlet')
        return self.render()

    def _toggleVisibleState(self, viewlethash, updateHiddenList):
        """ Change the visible/hidden state of the viewlet """
        unhashedInfo = self._unhashViewletInfo(viewlethash)
        logger.debug("in _toggleVisibleState")
        logger.debug(unhashedInfo)
        skinname = self.context.getCurrentSkinName()
        manager = unhashedInfo['manager']
        storage = getUtility(IViewletSettingsStorage)
        hidden = storage.getHidden(manager, skinname)
        logger.debug("hidden before...")
        logger.debug(hidden)
        storage.setHidden(manager, skinname, updateHiddenList(hidden, unhashedInfo['view_name']))
        logger.debug("hidden after...")
        logger.debug(storage.getHidden(manager, skinname))

        # Get the viewlet manager, update, and rerender it 
        viewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, manager)
        viewletManager.update()
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('.kssattr-viewletmanagername-' + manager.replace('.', '-'))
        ksscore.replaceInnerHTML(selector, viewletManager.render())
        return self.render()

    def _unhashViewletInfo(self, hash):
        """ Pull values out of the hashed "info" variable being passed in by KSS """
        concat_txt = binascii.a2b_hex(hash)
        for_name, type_name, view_name, manager = concat_txt.splitlines()
        info = dict(for_name=for_name, type_name=type_name, view_name=view_name, manager=manager, hash=hash)
        return info
        
