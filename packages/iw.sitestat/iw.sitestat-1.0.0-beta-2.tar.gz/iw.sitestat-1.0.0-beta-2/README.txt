===========
iw.sitestat
===========

By Ingeniweb_.

`iw.sitestat` makes the glue between a Plone site and a Sitestat
professional analytics service. The Sitestat product is a commercial
application from `Nedstat <http://www.nedstat.com>`_.

We assume at that point that your Sitestat service is correctly
installed and configured.

Note that the authors of `iw.sitestat` have no connection with the
Nedstat company.

Requirements
============

* `iw.sitestat` requires Plone 3.1 or newer.
* `simplejson` is added automatically by easy_install/zc.buildout.

Copyright and license
=====================

Copyright (c) 2008 Ingeniweb_ SAS

This software is subject to the provisions of the GNU General Public
License, Version 2.0 (GPL).  A copy of the GPL should accompany this
distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

See the `docs/LICENSE` file that comes with this component.

Installation
============

We assume that you created your Zope instance with **paster create -t
plone3_buildout <your-instance>** or something similar. And of course
you're supposed to know how to set up a Plone site using zc.buildout.


With zc.buildout
----------------

Recommended practice for integration or production instances.

Open `buildout.cfg` with your favorite text editor and change it like
indicated below::

  [instance]
  ...
  eggs =
    ...
    iw.sitestat
    ...
  zcml =
    ...
    iw.sitestat

Run your buildout, you're done.

From Subversion repository
--------------------------

Recommended practice for developers.

Install as indicated in `With zc.buildout`_ above.

Checkout your preferred trunk/branch of `iw.sitestat` in $BUILDOUT/src
(You should have $BUILDOUT/src/iw.sitestat/... after this). See the
`Project home pages`_ section for the repository URL.

Then::

  $ cd $BUILDOUT/src/iw.sitestat
  $ python setup.py develop

Open `buildout.cfg` with your favorite text editor and change it like
indicated below::

  [buildout]
  ...
  develop =
    src/iw.sitestat

Run your buildout, you're done. Your Subversion working copy of
`iw.sitestat` should take over the egg.

Configuration
=============

Site wide configuration
-----------------------

Go to the `Sitestat` configuration panel. This configuration panel is
self explanative for people who have basic skills in Sitestat
settings. Please refer to your Sitestat sevice documentation for terms
in use in this control panel.

Content item options
--------------------

Each content item has a `Sitestat` thumbnail available to anybody who
has item modification permission, even if Sitestat connection is
desactivated in the above mentioned control panel. As for the global
config, the various option widgets are self explanative for people
familiar with Sitestat features.

Limitations
===========

At this stage of development, we do not yet honour the following
Sitestat features:

* Adobe Flash decoration support.
* Forms decoration support.

These features are not essential in the context of a Plone site since
Plone is not suited for Flash oriented sites, and Plone has its own
tools for forms support.

Project home pages
==================

* At plone.org: http://plone.org/products/iw.sitestat
* At pypi: http://pypi.python.org/pypi/iw.sitestat
* Subversion repository: https://svn.plone.org/svn/collective/iw.sitestat

Upgrades
========

Visit in ZMI the `portal_setup` object of your site, click `Upgrades`
and select `iw.sitestat:default`. All is obvious from there.

Support
=======

As stated above, we will *never* provide support on Sitestat services,
or whatever that's covered by Nedstat commercial support. We only
support `iw.sitestat` itself.

Tracker
-------

You may report bugs or ask for features in our tracker. See the
"tracker" link from the project home page at plone.org.

Please read the rules written in the home page of the tracker before
reporting in the tracker. More specifically, please check that there
is no answer to your issue before filing anything.

Others
------

You may ask for further support (training, commercial support, ...) at
`Ingeniweb support <support@ingeniweb.com>`_ if you don't find answers
to your questions in the tracker.

Further documentation
=====================

See the other files in docs/\*. In addition this component may have
other more specific `README.txt` files in its directory tree.

More technical documentation may be found in docs/DESIGN.txt and
iw/sitestat/tests/\*.txt

Misc
====

About LinguaPlone
-----------------

We do not know if `iw.sitestat` is LinguaPlone compliant. At this time
we **do not** synch automatically content item options in the various
translations of a content item. As LinguaPlone is supposed to override
standard Plone and Archetypes APIs, we do not consider the issues
raised when mixing LinguaPlone and `iw.sitestat` in the same site as
`iw.sitestat` bugs. Anyway, sponsorship and contributions are welcome
to get all this working fine.

Credits
=======

* Main sponsor: `EDF <http://www.edf.fr>`_
* Main developer: `Gilles Lenfant <gilles.lenfant@ingeniweb.com>`_

Translations
============

* French (fr): `Gilles Lenfant <gilles.lenfant@ingeniweb.com>`_

.. _Ingeniweb: http://www.ingeniweb.com
.. $Id: README.txt 45 2008-09-30 16:23:05Z glenfant $
