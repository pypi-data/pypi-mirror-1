Introduction
============

This product provides an event subscriber for BaseContent Archetypes objects that will
clean up the HTML of all the RichText fields for each object.

This is especially a problem when users copy and paste from MSWord into
FCKEditor.

The operation runs automatically every time an object is created or edited and
can be disabled/enabled in the Settings fieldset of the object's normal 'edit'
view.

The cleaning and sanitizing of the HTML code is mainly done by using the lxml library:
http://codespeak.net/lxml/lxmlhtml.html 


This Product does not have to be installed via quick_installer or the plone
control panel.


