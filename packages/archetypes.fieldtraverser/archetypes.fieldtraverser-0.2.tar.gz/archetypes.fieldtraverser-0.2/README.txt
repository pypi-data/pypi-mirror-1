=========================
archetypes.fieldtraverser
=========================

Overview
========

This product patches Products.Archetypes so that it uses the fieldtraverser
for access to fields.

From the docstring of fieldtraverser.FieldTraverser:
"""
Used to traverse to a Archetypes field and access its storage.

useful together with AnnotationStorage if you dont want to hack __bobo__

usage: in url this traverser can be used to access a fields data by use of
	   the fieldname and the storage variant if needed (such as image sizes)
	   
	   in url its: obj/++atfield++FIELDNAME
	   or:         obj/++atfield++FIELDNAME-STORAGENAME 
	   
example: to access an original site image from a field named 'photo':
		 obj/++atfield++photo
		 
		 to access its thumbnail with size name thumb:
		 obj/++atfield++photo-thumb
"""


Dependencies
============

Products.Archetypes


Copyright
=========

Copyright (c) 2008: BlueDynamics Alliance, Austria


Credits
=======

- Jens Klein <jens@bluedynamics.com>

- Johannes Raggam <johannes@bluedynamics.com>

- Robert Niederreiter <rnix@squarewave.at