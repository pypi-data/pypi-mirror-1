from zope.component import getSiteManager
from plone.app.gloworm.browser.viewlets import OverridingViewletManager
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.app.gloworm.browser.interfaces import IInspectorView
from plone.app.layout.viewlets.interfaces import IPortalTop
from zope.viewlet.interfaces import IViewletManager
from zope.component import getGlobalSiteManager
from zope.publisher.interfaces.browser import IBrowserView

import logging
logger = logging.getLogger('plone.app.viewletmanageradaptation')

def install(self):
    """ """
    logger.info("Installing")
    sm = getSiteManager()
    vms = getAllViewletManagers(self)
    print vms
    for vm in vms:
        required = tuple([req for req in vm.required if req is not IBrowserView]) + (IInspectorView,)
        sm.registerAdapter(name=vm.name,
                           factory=OverridingViewletManager,
                           required=required,
                           provided=vm.provided,
                           )
    return "Ran install for viewletmanageradaptation"

def uninstall(self):
    """ """
    logger.info("Uninstalling")
    sm = getSiteManager()
    vms = getAllViewletManagers(self)
    print vms
    for vm in vms:
        required = tuple([req for req in vm.required if req is not IBrowserView]) + (IInspectorView,)
        sm.unregisterAdapter(name=vm.name,
                           factory=OverridingViewletManager,
                           required=required,
                           provided=vm.provided,
                           )
    return "Ran uninstall for viewletmanageradaptation"


def getAllViewletManagers(self):
    """
    """
    return [regs for regs in getGlobalSiteManager().registeredAdapters() if regs.provided.isOrExtends(IViewletManager)]
    
"""
<adapter name="plone.portaltop"
     factory="plone.app.viewletmanageradaptation.browser.viewletmanagertest.OverridingViewletManager"
     for_="zope.interface.Interface
           zope.publisher.interfaces.browser.IBrowserRequest
           plone.app.viewletmanageradaptation.browser.viewletmanagertest.IViewletManagerTestView"
     provides="plone.app.layout.viewlets.interfaces.IPortalTop"/>

sm.registerAdapter(
required=(Interface, IBrowserRequest, IBrowserView,),
provided=IContentProvider, name='plone.leftcolumn',
factory=site['.portlets']['left'])

"""     