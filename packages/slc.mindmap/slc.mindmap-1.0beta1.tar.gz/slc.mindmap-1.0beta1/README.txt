Introduction
============

slc.mindmap enables you to embed the mindmap editor from www.mindmeister.com
into your Plone site.

By using this editor you can view, edit and export mindmaps from inside Plone.

Please take note that currently mindmeister.com can only save mindmaps in their
own format (.mind). Your file will therefore be replaced with a .mind type file 
whenever you save your mindmap through the embedded editor.

How to use
==========

slc.mindmap provides a configlet in the Plone control panel with which you can
configure some of the features of the Mindmeister editor, such as
enabling/disabling exporting and saving. 

You will be required to specify an API key in this configlet which will
receive once you have signed up at www.mindmeister.com

Initially the settings in the configure will disable editing and exporting and
enable POSTing of the mindmap file to the mindmeister servers.

The POST option is only for development purposes since offline Plone instances
will not be able to render the mindmaps otherwise (without POSTing,
mindmeister.com receives a callback URL on the plone server from which to get
the mindmap file).

After setting up the configlet, you can upload a mindmap and enable the
Mindmeister editor for it.

To enable the editor, click on the subtypes menu on the file view, and choose
'mindmap'. The page should reload and you should see the Mindmeister editor
loading inside an iframe in the context view.

Requirements
===========

slc.mindmap depends on p4a.subtyper, it should be fetched and installed
automatically.


