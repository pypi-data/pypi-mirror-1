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

After installation, you'll get two new
items in Plone's **action** menu, one for *import*, and
one for *export*.

Bugs, Annoyances, Caveats
=========================

This package relies pretty much on the **Marshal_** product
for plone (which is shipped with Plone).  This product, is, while offering
great functionality, a bit convoluted and does not allow to hook in
using the ZCA.

Also, this package tries to export **references**, and this is currently done
using pickles, which is not safe.  References should be exported by using adapters
defined by those who actually use the references and know how to export them (it's
impossible to do this in a generic way IMHO).

Bugs
----

- exports references using pickles
- messes with the internals of the Marshal product due to lack of
  hooks
- uses pickles, this is not secure
- manifest XML is not yet parsed

Annoyances
----------

- convoluted code. The code of this package needs cleanup. This will be done in due
  course.

Caveats
-------

- This package can export AT based content only.
- This package does NOT export dynamically marked interfaces
- This package does NOT export annotations on content

