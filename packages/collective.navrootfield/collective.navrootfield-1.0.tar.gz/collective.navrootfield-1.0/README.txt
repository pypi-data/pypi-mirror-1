collective.navrootfield
=======================

This is a simple package which uses archetypes.schemaextender to add a field
to folders which allows one to make them navigation roots. This will affect
several things in Plone, like the destination of the link on the logo, the
global tabs, the navigation tree etc.

Usage
=====

Install the collective.navrootfield egg and load it's zcml. Folders will have
a "Navigation root" checkbox in the settings fieldset of the edit tab.
