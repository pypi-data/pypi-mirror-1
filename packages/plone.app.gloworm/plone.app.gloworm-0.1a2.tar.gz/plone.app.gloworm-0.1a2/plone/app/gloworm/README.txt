plone.app.gloworm Package Readme
=========================

Overview
--------

A Firebug-like inspector tool for Plone.

Credits
-------

Author: WebLion Group, Penn State University <support@weblion.psu.edu>.

Requirements-
------------

Requires Plone 3.1.x to operate.


Using GloWorm
-------------

Install the plone.app.gloworm package through the Add/Remove Products page. Once installed and when 
running in Zope debug mode, an "inspect this page" link will appear in the Object Actions section of
content objects on your site. Clicking this link will open up a new view of the page which includes
the GloWorm inspection panel. (You may also reach this view by appending '@@inspect' to the current 
page's URL).

In this view, clicking on any element of the current page will bring up a list of information about 
that object, including TAL commands and the viewlet or portlet is contained in.

Click the "close" icon in the upper-right corner of the GloWorm panel to return to normal browsing.

