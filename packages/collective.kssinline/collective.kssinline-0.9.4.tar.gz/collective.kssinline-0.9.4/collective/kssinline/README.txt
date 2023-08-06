Overview
--------
collective.kssinline allows you to edit and create content without navigating away from listings.

kss bindings are made on the add content menu items (the green drop-down). These bindings will intercept the object creation navigation.

The normal folder contents view is subclassed to provide editing links in the table. This view is specified in overrides.zcml with the name folder_contents, which means it overrides the normal Plone folder contents.

Requirements
------------
Plone>3.1 because it ships with jQuery

Installation
------------
A buildout is provided at
http://dev.plone.org/collective/browser/collective.kssinline/trunk/buildout.cfg

To enable collective.kssinline for an existing installation ensure that the following is present in your buildout.cfg

In the eggs section collective.kssinline

In the zcml section collective.kssinline and collective.kssinline-overrides

Run ./bin/buildout -Nv and restart your instance.

collective.kssinline must be installed as a product in a Plone site. This can be done through the quick installer or portal_setup.

There is a KssInline Tool configlet under Site Setup where you can choose which types are subject to inline editing.
