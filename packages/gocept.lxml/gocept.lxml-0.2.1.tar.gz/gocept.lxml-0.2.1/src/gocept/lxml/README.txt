==============================
Interface Definitions For lxml
==============================

This package provides zope interfaces for lxml objects. Far from being
complete but a starting point.

Interfaces
==========

Interfaces are here:    

>>> import gocept.lxml.interfaces

There is an interface for lxml.etree elements:

>>> import lxml.etree
>>> xml = lxml.etree.fromstring('<a/>')
>>> gocept.lxml.interfaces.IElement.providedBy(xml)
True

And for objectifieds:

>>> import lxml.objectify
>>> obj = lxml.objectify.fromstring('<a><str>holla</str></a>')
>>> gocept.lxml.interfaces.IElement.providedBy(obj)
True
>>> gocept.lxml.interfaces.IObjectified.providedBy(obj)
True
>>> gocept.lxml.interfaces.IElement.providedBy(obj.str)
True
>>> gocept.lxml.interfaces.IObjectified.providedBy(obj.str)
True


Objectified parsers
===================

There is a helper for creating objectifieds from file handles in
`gocept.lxml.objectify`. Open a file:

>>> import os.path
>>> import gocept.lxml.objectify
>>> filename = os.path.join(
...     os.path.dirname(__file__),
...     'ftesting.zcml')
>>> xml_file = file(filename)

And parse it:

>>> xml = gocept.lxml.objectify.fromfile(xml_file)
>>> xml
<Element {http://namespaces.zope.org/zope}configure at ...>

This really is objectified:

>>> gocept.lxml.interfaces.IObjectified.providedBy(xml)
True
>>> xml.include.get('package')
'zope.app.component'


For convinience `fromstring` is also defined in `gocept.lxml.objectify`:

>>> xml = gocept.lxml.objectify.fromstring('<a><b/></a>')
>>> xml
<Element a at ...>
>>> gocept.lxml.interfaces.IObjectified.providedBy(xml)
True

Changes
=======

0.2.1 (2008-02-14)
++++++++++++++++++

- Lifted dependency on lxml<2.0dev so lxml 2 can be used now.
