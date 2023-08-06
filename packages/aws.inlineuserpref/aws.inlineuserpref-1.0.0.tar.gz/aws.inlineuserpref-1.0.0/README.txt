==================
aws.inlineuserpref
==================


Introduction
============

Since Plone 3.1.5, a site manager can enable or disable globally inline editing
(KSS) to all users or nobody. Enabling inline editing is fair to users ho got a
fast computer and a modern browser.

Content authors in lots of organizations who have Plone powered intranets have
old computers and/or cannot install a modern browser, mostly stuck with IE6,
thus cannot use inline editing unless it bloats their computer.

``aws.inlineuserpref`` provides a user control panel that let members choose if
they prefer or not using inline editing, such users with decent computers and
recent browser can carry on enjoying inline editing, while others with old
computers and browsers cans disable inline editing.

Copyright and license
=====================

Copyright (c) 2009 - Alter Way Solutions

This software is subject to the provisions of the GNU General Public License,
Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE

See the ``docs/LICENSE.txt`` file that comes with this product.

Requirements
============

Plone 3.1.5 or later.

Installation
============

With zc.buildout
----------------

Recommanded installation for production sites. Add these lines to your
``buildout.cfg`` ::

  [buildout]
  ...
  eggs =
      ...
      aws.inlineuserpref
      ...

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  zcml =
      ...
      aw.inlineuserpref
      aw.inlineuserpref-overrides

Development
-----------

Developers of this package should use the ``buildout.cfg`` that comes in the
subversion bundle. See `Subversion repository`_ below.

In the Plone site
-----------------

Install ``aws.inlineuserpref`` as usually either with the quick installer or the
setup tool.

Upgrading
---------

If you upgraded ``aws.inlineuserpref`` from a previous version, upgrades may be
available. Open in ZMI the "Upgrades" tab of the "portal_setup" tool and look if
upgrades are available for ``aws.inlineuserpref:default`` profile.

Usage for content authors
=========================

The control panel is available from the user's preferences panel. Its usage is
obvious and self explanative.

How to
======

Default KSS preference should be "off" for any new user
-------------------------------------------------------

I didn't make a control panel for this. Just open the **Properties** tab of the
**portal_memberdata** object of your Plone site, and uncheck the
**enable_inline_editing** property.

Subversion repository
=====================

https://svn.plone.org/svn/collective/aws.inlineuserpref

Support
=======

Ask for support to `Alter Way Solutions support <support@ingeniweb.com>`_.

Credits
=======

* Developer : `Gilles Lenfant <mailto:gilles.lenfant@ingeniweb.com>`_
* Sponsor : `EDF <http://www.edf.fr>`_

To do
=====

* Plone 4 compatiblity.
