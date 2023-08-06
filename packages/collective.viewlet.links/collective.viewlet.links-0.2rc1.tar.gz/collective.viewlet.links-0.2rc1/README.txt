Overview
========

This package provides a viewlet that lets you enter in a list of local and external links on plonesite level
and on subfolders. Usually these links get displayed in the footer, but the viewlet can be placed anywhere.


After installation the viewlet displays a `Manage links` button for users with the corresponding permission
(granted to managers by default).
Users can set the links for a context that implements `ICanDefineLinks` (plonesite or folders by default)
by inserting them in a textfield like this::

  Plone;http://plone.org
  Internal;/relative/to/plone-site
  Webmeisterei;http://webmeisterei.com

Links defined on the portal get displayed in subfolders too, as long as they do not define their own links.


See the `package README <http://dev.plone.org/collective/browser/collective.viewlet.links/trunk/collective/viewlet/links/README.txt>`_
for a test describing this package's functionality in detail.

A screenshot_ of how links can be added and how they are displayed
can be found on the `product page` on plone.org.

.. _screenshot: http://plone.org/products/collective.vielet.links/screenshot
.. _`product page`: http://plone.org/products/collective.vielet.links


Installation
------------

To use this package in a plone buildout add `plone.app.z3cform` to the eggs section and to the
zcml slug for the zope instance::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  eggs =
      ...
      collective.viewlet.links
      ...
  zcml =
      collective.viewlet.links


Since collective.viewlet.links requires `plone.app.z3cform` the buildout is a little more complicating.
See the `developer buildout`_ for an example.

* use plone.recipe.zope2install >= 3.0 (default fake-eggs)
* use same skip-fake-eggs



Contribute
----------

Please submit bugs or feature requests to the `issue tracker`_  on the `product page`.

.. _`issue tracker`: http://plone.org/products/collective.vielet.links/issues


If you want to contribute to collective.viewlet.links, you can use the `developer buildout`_.

See the README there for instructions on how to setup an instance and run the tests.

.. _`developer buildout`: https://svn.plone.org/svn/collective/collective.viewlet.links/buildout/trunk


Authors
-------

Liz Dahlstrom (lizz-y)
  Initial idea and implementation

Harald Friessnegger (fRiSi)
  added support for custom links for content objects,
  unittests, devbuildout and made links be stored in an annotation
