five.grok
=========

.. contents::

Introduction
------------

`five.grok` is a development layer for Zope 2, based on Grok framework concepts.

The development techniques are similar to the ones used with Grok framework. 

It is based on `grokcore` namespace packages that were factored out of Grok
framework.



Implemented features
--------------------

Coming from Grok, the following components are available to Zope 2
developers:

- Zope 3 Component (Adapter, Utility, Subscribers),

- Permissions,

- Views,

- Page Templates (using the Zope 2 Page Templates),

- Formlib forms.

All those components are available with exactly the same syntax than
in grok. You just have to do::

  from five import grok

Instead of::

  import grok


More information
----------------

You can refer to the Grok website: http://grok.zope.org/, and the Grok
documentation: http://grok.zope.org/documentation/.

You can check the doctest included in sources as well.
