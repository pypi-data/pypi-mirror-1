================
iw.memberreplace
================

By Ingeniweb_

A missing feature from the members control panel. A contributor of your Plone
site is replaced by someone else. This happens sometimes. If your site has
thousands of items, dozens of contributors and groups, this utility will save
your managers hours of digging in your site and changing settings on hundreds of
content items.

Features and options:

* Replace member in ownership
* Replace member in DC Creators
* Replace member in sharings
* Replace member in groups
* Remove former member
* Dry run
* Logging all this

Copyright and license
=====================

Copyright (c) 2008-2009 Ingeniweb_ SAS

This software is subject to the provisions of the GNU General Public License,
Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.  THIS
SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE
DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE,
MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

See the `docs/LICENSE` file that comes with this component.

Requirements
============

Plone 3.x

Installation
============

We assume that you created your Zope instance with **paster create -t
plone3_buildout <your-instance>** or something similar. And of course you're
supposed to know how to set up a Plone site using zc.buildout.

With zc.buildout
----------------

Recommended practice for integration or production instances.

Open `buildout.cfg` with your favorite text editor and change it like indicated
below::

  [instance]
  ...
  eggs =
    ...
    iw.memberreplace
    ...
  zcml =
    ...
    iw.memberreplace

Run your buildout, you're done.

From Subversion repository
--------------------------

Recommended practice for developers.

Install as indicated in `With zc.buildout`_ above.

Checkout your preferred trunk/branch of `iw.memberreplace` in $BUILDOUT/src (You
should have $BUILDOUT/src/iw.memberreplace/... after this). See the `Project
home pages`_ section for the repository URL.

Then::

  $ cd $BUILDOUT/src/iw.memberreplace
  $ python setup.py develop

Open `buildout.cfg` with your favorite text editor and change it like indicated
below::

  [buildout]
  ...
  develop =
    src/iw.memberreplace

Run your buildout, you're done. Your Subversion working copy of
`iw.memberreplace` should take over the egg.

Project home pages
==================

* At plone.org: http://plone.org/products/iw.memberreplace
* At pypi: http://pypi.python.org/pypi/iw.memberreplace
* Subversion repository:
  https://svn.plone.org/svn/collective/iw.memberreplace

Upgrades
========

Visit in ZMI the `portal_setup` object of your site, click `Upgrades` and select
`iw.memberreplace:default`. All is obvious from there.

Support
=======

You may ask for further support (training, commercial support, ...) at
`Ingeniweb support <support@ingeniweb.com>`_ if you don't find answers to your
questions in the tracker.

Further documentation
=====================

See the other files in docs/. In addition this component may have other more
specific `README.txt` files in its directory tree.

More technical documentation may be found in
thisdir/iw/memberreplace/tests/README.txt.

Credits
=======

* Main developer: `Gilles Lenfant <gilles.lenfant@ingeniweb.com>`_

Translations
============

* French (fr): `Gilles Lenfant <gilles.lenfant@ingeniweb.com>`_

.. _Ingeniweb: http://www.ingeniweb.com/
.. $Id: README.txt 81891 2009-03-07 23:29:53Z glenfant $
