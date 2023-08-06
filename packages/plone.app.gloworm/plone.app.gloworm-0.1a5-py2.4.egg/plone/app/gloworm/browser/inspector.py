from zope.component import getAdapters
from zope.component import getSiteManager
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implements, providedBy
from five.customerize.interfaces import IViewTemplateContainer
from five.customerize.utils import findViewletTemplate
from five.customerize.browser import mangleAbsoluteFilename
from plone.app.customerize import registration
from plone.portlets.utils import unhashPortletInfo
from zope.viewlet.interfaces import IViewlet, IViewletManager
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView as base
from zope.contentprovider.interfaces import IContentProvider

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
                        # result = ksscore.nodeAttr(ksscore.getSameNodeSelector(), att)
                        result = ""
                        logger.debug("result: %s" % result)
                        out += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (att, expr, result)
                out += "</table></td></tr>"
            if talcondition:
                out += "<tr><td>tal-condition:</td><td>%s</td></tr>" % talcondition
            if portlethash:
                unhashedPortletInfo = unhashPortletInfo(portlethash) 
                out += "<tr><td>portlet:</td><td>portlet name: %s<br />portlet manager: %s</td></tr>" % (unhashedPortletInfo['name'], unhashedPortletInfo['manager'])
            if viewlethash:
                unhashedViewletInfo = self._unhashViewletInfo(viewlethash)
                out += "<tr><td>viewlet:</td><td><a href='#' class='viewletMoreInfo kssattr-forviewlet-%s'>%s</a></td></tr>" % (viewlethash, unhashedViewletInfo['view_name'])
            out += "</table>"
            
            # Dump the output to the inspector panel
            self.updatePanelBodyContent(out)
            
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
        reg = self._findTemplateViewRegistrationFromHash(viewlethash)
        viewRegistrationInfo = list(registration.templateViewRegistrationInfos([reg]))[0]
        template = viewRegistrationInfo['zptfile']
        cls = registration.getViewClassFromRegistration(reg)
        
        # Display it
        out = "<h4>Viewlet %s</h4><table>" % unhashedViewletInfo['view_name']
        out += "<tr><td>name:</td><td>%s</td></tr>" % unhashedViewletInfo['view_name']
        out += "<tr><td>manager:</td><td><a href='#' class='inspectViewletManager kssattr-forviewletmanager-%s'>%s</a></td></tr>" % (unhashedViewletInfo['manager_name'], unhashedViewletInfo['manager_name'])
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
        
        out += "<tr><td colspan='2'><form>"
        out += "<select id='toManagerName'>"
        
        managerNames = self._getAllViewletManagerNames()
        managerNames.sort()
        # Remove the viewlet's current viewlet manager and the gloworm panel from the choices.
        managerNames.remove(unhashedViewletInfo['manager_name'])
        managerNames.remove('gloworm.glowormPanel')
        
        for mgr in [name for name in managerNames if name is not unhashedViewletInfo['manager_name']]:
            out +="<option>%s</option>" % mgr
        out += "</select>"
        out += '<input type="submit" value="Move" class="moveToViewletManager kssattr-forviewlet-%s" />' % viewlethash
        out += "</form></td></tr>"
        out += "</table>"
        
        # Dump the output to the output panel
        self.updatePanelBodyContent(out)
        
        # Remove highlights from previously-clicked elements
        ksscore = self.getCommandSet('core')
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
        reg = self._findTemplateViewRegistrationFromHash(viewlethash)
        regInfo = list(registration.templateViewRegistrationInfos([reg]))[0]
        
        # TODO We should be looking at regInfo['customized'] to determine whether or not a customization exists. 
        # It never seems to have a value though... check on this.
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
        # TODO: move this to a viewlet
        out += """
            <form>
                <textarea name="text:text" id="editableTemplateContent" rows="10">%s</textarea>
                <div style="text-align:right; margin: 1em;">
                    <input type="submit" value="&laquo; Back" name="pt_editAction:method" class="viewletMoreInfo kssattr-forviewlet-%s" />
                    <input type="submit" value="Discard Customizations" name="pt_editAction:method" class="discardTemplateEdits kssattr-forviewlet-%s" />
                    <input type="submit" value="Save" name="pt_editAction:method" class="saveTemplateEdits kssattr-forviewlet-%s" />
                </div>
            </form>
        """ % (templateCode, viewlethash, viewlethash, viewlethash)
        self.updatePanelBodyContent(out)
        
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
        managerName = unhashedInfo['manager_name']
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
        reg = self._findTemplateViewRegistrationFromHash(viewlethash)
        templateName = registration.generateIdFromRegistration(reg)
        
        container.manage_delObjects([templateName])
        self._renderCustomizedViewlet(viewlethash, templateName)
        return self.inspectViewlet(viewlethash)
    
    def moveViewletToViewletManager(self, viewlethash, toManagerName):
        """ Register the viewlet as belonging to the specified viewlet manager """
        # Unhash the viewlet info. Pull out what we need.
        unhashedInfo = self._unhashViewletInfo(viewlethash)
        fromManagerName = unhashedInfo['manager_name']
        viewletName = unhashedInfo['view_name']
        
        reg = self._findTemplateViewRegistrationFromHash(viewlethash)

        fromViewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, fromManagerName)         
        fromManagerInterface = list(providedBy(fromViewletManager).flattened())[0] 
        toViewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, toManagerName)        
        toManagerInterface = list(providedBy(toViewletManager).flattened())[0]
        
        # Create a new tuple of the "required" interfaces.
        reqList = list(reg.required)
        pos = reqList.index(fromManagerInterface) 
        reqList[pos] = toManagerInterface 
        reqs = tuple(reqList)
        
        registration.createTTWViewTemplate(reg)
        attr, pt = findViewletTemplate(reg.factory)
        reg.factory.template = mangleAbsoluteFilename(pt.filename)
        
        # Register the new adapter
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(name=viewletName, required=reqs, provided=reg.provided, factory=reg.factory)
        
        # "Customize" it to force persistence
        reqstr = ','.join([a.__identifier__ for a in reqs])
        toreg = registration.findTemplateViewRegistration(reqstr, viewletName)
        viewzpt = registration.customizeTemplate(toreg)
        sm = getSiteManager(self.context)
        sm.registerAdapter(viewzpt, required=toreg.required, provided=toreg.provided, name=toreg.name)
        
        # Hide the original
        self.hide_viewlet(viewlethash)
        
        # Rerender the new one
        toViewletManager.update()
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('.kssattr-viewletmanagername-' + toManagerName.replace('.', '-'))
        ksscore.replaceInnerHTML(selector, toViewletManager.render())
        
        return self.render()
    
    def inspectViewletManager(self, managerName):
        """ Display information about a particular viewlet manager """
        logger.debug("in inspectViewletManager")
        
        # Get the viewletmanager object
        viewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, managerName)
        
        # Gather information for the viewlet hashes
        managerInterface = list(providedBy(viewletManager).flattened())[0]
        
        # Look up the viewlets attached to this viewlet manager.
        # We do it this way because calling viewletManager.viewlets won't see the hidden viewlets...
        viewlets = getAdapters((viewletManager.context, viewletManager.request, viewletManager.__parent__, viewletManager),IViewlet)
        
        # Get the names of the hidden viewlets
        storage = getUtility(IViewletSettingsStorage)
        hidden = frozenset(storage.getHidden(managerName, self.context.getCurrentSkinName()))
        
        # Generate the output
        out = "<h4>Viewlet Manager %s</h4><table>" % managerName
        sortedViewlets = viewletManager.sort(viewlets)
        for viewletTuple in sortedViewlets:
            viewletname = viewletTuple[0]
            
            # generate viewlet hashes...
            # TODO factor this up.

            # Get the "provided" interfaces for this viewlet manager.
            # TODO: Do this lookup properly.
            regs = [regs for regs in getGlobalSiteManager().registeredAdapters() if regs.name == viewletname and regs.required[-1].isOrExtends(managerInterface)]
            if regs:
                reg = regs[0]
                provided = ','.join([a.__identifier__ for a in reg.required])
                # logger.debug("%s - provided: %s" % (view_name, provided))
                hashedInfo = binascii.b2a_hex("%s\n%s\n%s" % (viewletname, managerName, provided))
            else:
                hashedInfo = ""
                logger.debug("Unable to create hash for %s" % viewletname)
            
            # Give the viewlet a class name depending on the visibility
            classname = viewletname in hidden and 'hiddenViewlet' or 'visibleViewlet'
            logger.debug(classname)
            
            out += "<tr class='%s kssattr-viewlethash-%s'>" % (classname, hashedInfo)
            
            out += "<td>"
            if viewletTuple != sortedViewlets[0]:
                out += "<a href='#' class='viewletMoveUp kssattr-forviewlet-%s'>&#9650;</a>" % hashedInfo
            out += "</td>"
            out += "<td>"
            if viewletTuple != sortedViewlets[-1]:
                out += "<a href='#' class='viewletMoveDown kssattr-forviewlet-%s'>&#9660;</a>" % hashedInfo
            out += "</td>"
            
            out += """<td>
                        <a href='#' class='hideViewlet'><img src='portal_skins/GloWorm/lightbulb.png' /></a>
                        <a href='#' class='showViewlet'><img src='portal_skins/GloWorm/lightbulb_off.png' /></a>
                      </td>"""
            out += "<td><a href='#' class='viewletMoreInfo kssattr-forviewlet-%s'>%s</a></td>" % (hashedInfo, viewletname)
            
            out += "</tr>"
        out += "</table>"
        
        # Update the output panel
        self.updatePanelBodyContent(out)
        
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
    
    def moveViewletByDelta(self, viewlethash, delta):
        """ Move the viewlet within its viewlet manager """
        logger.debug("in moveViewletByDelta")
        
        # Grab the information we need from the viewlet hash
        unhashedInfo = self._unhashViewletInfo(viewlethash)
        managerName = unhashedInfo['manager_name']
        viewletName = unhashedInfo['view_name']
        
        # Make sure delta is an integer, KSS apparently passes it in as a string.
        logger.debug("Converting %s to an integer" % delta)
        delta = int(delta)
        logger.debug("Moving viewlet by %s" % delta)
        
        # Get the viewletmanager object
        viewletManager = queryMultiAdapter((self.context, self.request, self), IViewletManager, managerName)
        
        # Get the order of the viewlets managed by this viewlet manager
        viewletManager.update()
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.context.getCurrentSkinName()
        order = list(storage.getOrder(managerName, skinname))
        viewlet_index = order.index(viewletName)
        
        # Move the viewlet to its new position
        newpos = max(0, viewlet_index + delta) and min(viewlet_index + delta, len(order))
        del order[viewlet_index]
        order.insert(newpos, viewletName)
        storage = getUtility(IViewletSettingsStorage)
        storage.setOrder(managerName, skinname, order)
        
        # Find the viewletmangager instance, tell it to update its rendering, and replace the contents of the selected div with that new html
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('.kssattr-viewletmanagername-' + managerName.replace('.', '-'))
        
        viewletManager.update()
        ksscore.replaceInnerHTML(selector, viewletManager.render())
        
        # Update the viewlet listing in the GloWorm panel
        # TODO: This can probably be done without rerunning all of the viewlet manager inspection code...
        self.inspectViewletManager(managerName)
        
        return self.render()
    
    def updatePanelBodyContent(self, content):
        """ Overwrite the current text in the GloWorm panel body """
        logger.debug("updatePanelBodyContent")
        ksscore = self.getCommandSet('core')
        panel = ksscore.getCssSelector('#glowormPanelBody')
        ksscore.replaceInnerHTML(panel, content)
        kssglo = self.getCommandSet('gloWorm')
        kssglo.resizePanel()
    
    def _toggleVisibleState(self, viewlethash, updateHiddenList):
        """ Change the visible/hidden state of the viewlet """
        unhashedInfo = self._unhashViewletInfo(viewlethash)
        logger.debug("in _toggleVisibleState")
        logger.debug(unhashedInfo)
        skinname = self.context.getCurrentSkinName()
        manager = unhashedInfo['manager_name']
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
        view_name, manager_name, provided = concat_txt.splitlines()
        # Turn provided into the tuple of strings that plone.app.customerize is looking for.
        info = dict(view_name=view_name, manager_name=manager_name, provided=provided, hash=hash)
        return info
    
    def _findTemplateViewRegistrationFromHash(self, hash):
        """ Get the view registration information from plone.app.customerize """
        unhashedInfo = self._unhashViewletInfo(hash)
        return registration.findTemplateViewRegistration(unhashedInfo['provided'], unhashedInfo['view_name'])
        
    def _getAllViewletManagers(self):
        """ Get all defined viewlet managers
        """
        return [regs for regs in getGlobalSiteManager().registeredAdapters() if regs.provided.isOrExtends(IViewletManager)]
        
    def _getAllViewletManagerNames(self):
        """ Get the names of all defined viewlet managers """
        return [v.name for v in self._getAllViewletManagers()]

