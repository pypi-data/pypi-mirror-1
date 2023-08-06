collective.plone.gsxml
======================

An XML import/export add-on for Plone_.

.. _Plone: http://www.plone.org

Installation
============

**collective.plone.gsxml** is a egg, so installation is easy
if you use buildout.  You just need to add **collective.plone.gsxml**
to your plone part's *eggs* AND *zcml* option.

A example buildout is available here:

https://svn.plone.org/svn/collective/gsxml/buildout/trunk

This package needs lxml_, see the buildout example.

.. _lxml: http://www.codespeak.net/lxml


Usage
=====

After installation, you'll get two new items in Plone's **action**
menu, one for *import*, and one for *export*.  For additional stuff,
please see the detailled documentation below.

Features
========

- Exports virtually all Archetypes-based documents
- exports and keeps references
- exports binary data as separate file
- works with ZOPE blobs
- sends custom events which you can subscribe to prior and after
  import/export
- uses the ZCA to fetch a serializer for a content type -- the default
  adapter uses the Plone Marshaller

Caveats
=======

This package relies pretty much on the **Marshall** product for plone
(which is shipped with Plone).  This product, is, while offering great
functionality, a bit convoluted and does not allow to hook in using
the ZCA.

Also, this package tries to export **references**, and this is
currently done using pickles, which is not safe.  References should be
exported by using adapters defined by those who actually use the
references and know how to export them (it's impossible to do this in
a generic way IMHO).

Bugs
----

- exports references using pickles
- messes with the internals of the Marshal product due to lack of
  hooks
- uses pickles, this is not secure
- manifest XML is not yet parsed

Annoyances
----------

- convoluted code. The code of this package needs cleanup. This will
  be done in due course.

Caveats
-------

- This package out-of-the-box export AT based content only, but you
  can provide your own serializer as adapter
- This package does NOT export dynamically marked interfaces
- This package does NOT export annotations on content

Products.Poi
------------

You need the branch version of Products.Marshall to handle the DataGridFields

https://svn.plone.org/svn/archetypes/Products.Marshall/branches/use-zca-in-atns

Products.eXtremeManagement
--------------------------

change line 44 of Products.eXtremeManagement.content.PoiTask to::

   def getAssignees(self):
        managers = set()
        try:
            for issue in self.getRefs('task_issues'):
                managers.add(issue.getResponsibleManager())
        except:
            pass
        return sorted(list(managers))

because the references to the POI issues are fixed on the end of import and are
*not* available when the object is recreated

::
 vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
