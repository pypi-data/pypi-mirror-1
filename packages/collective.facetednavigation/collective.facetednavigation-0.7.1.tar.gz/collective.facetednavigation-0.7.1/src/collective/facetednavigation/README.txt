=============================
Collective Faceted Navigation
=============================

What is faceted navigation (the concept)
========================================

First, what is faceted classification::

    A faceted classification system allows the assignment of multiple
    classifications to an object, enabling the classifications to be
    ordered in multiple ways, rather than in a single, pre-determined,
    taxonomic order.

    -- Wikipedia (Faceted classification)

Once we know what faceted classification is, we can infer what is a
faceted browser::

    A faceted browser or faceted semantic browser is a user interface
    which makes use of faceted classification to allow the user to
    explore by filtering available information. Each facet typically
    corresponds to the possible values of a property common to a set
    of digital objects.

    -- Wikipedia (Faceted browser)

An example would help, I guess::

    A traditional restaurant guide might group restaurants first by
    location, then by type, price, rating, awards, ambiance, and
    amenities. In a faceted system, a user might decide first to
    divide the restaurants by price, and then by location and then by
    type, while another user could first sort the restaurants by type
    and then by awards. Thus, faceted navigation, like taxonomic
    navigation, guides users by showing them available categories (or
    facets), but does not require them to browse through a hierarchy
    that may not precisely suit their needs or way of thinking.

    -- Wikipedia (Faceted classification)

Sources:

- `Faceted classification`_ in Wikipedia;

- `Faceted browser`_ in Wikipedia.

Various examples of faceted navigation are also available on the
home page of the MIT `Exhibit`_ project.

.. _Faceted classification: http://en.wikipedia.org/wiki/Faceted_classification

.. _Faceted browser: http://en.wikipedia.org/wiki/Faceted_browser

.. _Exhibit: http://simile.mit.edu/exhibit


What is Faceted Navigation (the Plone product)
==============================================

This concept sounds cool, but what does Faceted Navigation (the
product) exactly do?

Once we have installed the product, we will have to configure facets
(i.e. criteria), which are actually linked to default or custom
catalog indexes. Then the user will see a new link in the portal
actions bar (along "site map" and other links), called "Faceted
navigation". This link leads to an user interface that lets the user
browse portal items via... a faceted navigation.

**Warning:** I do not pretend to be an expert on this subject, nor do
I think that this is the definitive implementation of this concept in
Plone. I also have other user interfaces in mind; they could probably
be implemented using the current code. Anyway, there are a lot of
ideas floating around: a good start would be the `Plone
classification`_ workspace on OpenPlans.

.. _Plone classification: http://www.openplans.org/projects/ploneclassification


Examples
========

Example applications have been set up:

- `Burgers`_;

- PyPi - Python packages (in development).

Feel free to try them and provide feedback.

.. _Burgers: http://burgers.pilotsystems.net


Dependencies
============

Server-side
-----------

This version has the following dependencies:

- Plone 3.0.x or Plone 3.1.x

This product might also work with Plone 2.5 (probably with a
backported version of KSS, though).


Browser-side
------------

The user interface makes use of KSS. Therefore, Javascript must be
activated. There is no plan to provide a non-Javascript version.

The user interface should work on all modern browsers. It has been
successfully tested on the following ones:

- Firefox 2;

- Firefox 3;

- Opera 9;

- Microsoft Internet Explorer 6;

- Microsoft Internet Explorer 7.

Support for earlier versions and other browsers is not planned.


Installation and configuration
==============================

See ``doc/install.txt``.


Documentation
=============

The most up to date documentation of this product lives in `the "doc"
folder`_ of the sources. It is mirrored in the `Documentation
section`_ of `Faceted Navigation`_ on `plone.org`_.

.. _the "doc" folder: http://dev.plone.org/collective/browser/collective.facetednavigation/trunk/src/collective/facetednavigation/doc

.. _Documentation section: http://plone.org/products/faceted-navigation/documentation

.. _Faceted navigation: http://plone.org/products/faceted-navigation

.. _plone.org: http://plone.org


Credits
=======

The development of this product has been initially sponsored by `ENA`_
(Ecole Nationale d'Administration) and conducted by `Pilot Systems`_.

The following people have developed, given help or tested this
product:

- Damien Baty (damien DOT baty AT gmail DOT com): original author,
  tests, documentation, maintenance.
- Leonardo Caballero (leonardocaballero AT gmail DOT com>): Spanish localization.

.. _ENA: http://www.ena.fr

.. _Pilot Systems: http://www.pilotsystems.net


License
=======

Collective Faceted Navigation is copyright 2008 by ENA (Ecole
Nationale d'Administration).

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see the `section about licenses`_ of
the `GNU web site`_.

.. _section about licenses: http://www.gnu.org/licenses
.. _GNU web site: http://www.gnu.org
