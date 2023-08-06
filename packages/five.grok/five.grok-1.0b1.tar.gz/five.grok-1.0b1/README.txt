five.grok
=========

.. contents::

Introduction
------------

`five.grok` is a development layer for Zope 2, based on Grok framework
concepts.

The development techniques are similar to the ones used with Grok
framework.

It is based on `grokcore` namespace packages that were factored out of Grok
framework.

Implemented features
--------------------

Coming from Grok, the following components are available to Zope 2
developers:

- Zope 3 Component (Adapter, Global utilities, Subscribers),

- Permissions,

- Views and Viewlets,

- Skins and resources directories,

- Page Templates (using the Zope 2 Page Templates),

- Formlib forms,

- Local sites and local utilities,

- Annotations.

All those components are available with exactly the same syntax than
in grok. You just have to do::

  from five import grok

Instead of::

  import grok

Installation
------------

After adding the dependency to ``five.grok`` in your project, you have
to load the following ZCML::

  <include package="five.grok" />

Note
~~~~

``five.grok`` have some dependencies on Zope 3 eggs. With Zope 2, you
can fake those dependencies in buildout with the help of
``plone.recipe.zope2instance``.

The minium required configuration to install Zope would be::

  [zope2]
  recipe = plone.recipe.zope2install
  url = Please complete here correctly
  fake-zope-eggs = true
  additional-fake-eggs =
     ZODB3
  skip-fake-eggs =
     zope.app.publisher
     zope.component
     zope.i18n
     zope.interface
     zope.testing


And for this release we recommand to pin down the following version in
your buildout::

  grokcore.annotation = 1.0.1
  grokcore.component = 1.6
  grokcore.formlib = 1.1
  grokcore.security = 1.0
  grokcore.site = 1.0.1
  grokcore.view = 1.7
  grokcore.viewlet = 1.0
  five.localsitemanager = 1.1
  martian = 0.11
  zope.app.publisher = 3.5.1
  zope.component = 3.4
  zope.i18n = 3.6.0
  zope.interface = 3.5.0
  zope.testing = 3.7.1

Zope 2.10 is required as bare minimum.


More information
----------------

You can refer to the Grok website: http://grok.zope.org/, and the Grok
documentation: http://grok.zope.org/documentation/.

You can check the doctest included in sources as well.
