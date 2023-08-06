Rotating Plone content
======================

Overview
--------
This package provides rotating of arbitrary content in Plone. 

It comes with a default portlet to display rotating content but you can easily
plug in your own one and/or viewlets, etc.

Installation
------------
To get started you will simply need to add the package to your "eggs" and
"zcml" sections, run buildout, restart your Plone instance and install the
"iqpp.plone.rotating" package using the quick-installer or via the "Add-on
Products" section in "Site Setup".

Create a Collection (Topic) to select the content which should be rotated. (For 
instance you can use the "aggregator" within the default news or events folder).

Adapt the options within the "Rotating Options" tab.

Add a "Rotating" portlet and enter the path to the Collection.

How it works
------------
First it asks the associated Collection for all objects, which match the 
criteria. If the requested items for rotating are less than the found ones it 
decides randomly which ones to return.

Options
-------
Return Already Selected:

    If checked, already selected items within "Path" can be displayed again. 
    Otherwise all items within "Path" are displayed only once.
    
Reset Selected:

    If checked already selected items within "Path" will be reset if all items
    has been displayed. Otherwise no item will be returned if all items has been
    displayed.
    
Update Intervall

    Within this intervall (in hours) the same objects are returned.

Set To Midnight

    If checked "Last Update" is always set to midnight. This only makes sense if 
    "Update Intervall" is set to an multiple of 24 hours. In this way you can 
    display one item per day for instance.
    
Status
------
The package is beta but it is in use within a few production sites.