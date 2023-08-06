Introduction
============

Extra extension of the collective.blogging which integrates 3rd-party
package Products.Maps for blogging events.

Installing
============

This package requires Plone 3.x or later (tested on 3.3.x).

Installing without buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install this package in either your system path packages or in the lib/python
directory of your Zope instance. You can do this using either easy_install or
via the setup.py script.

Installing with buildout
~~~~~~~~~~~~~~~~~~~~~~~~

If you are using `buildout`_ to manage your instance installing
collective.bloggingmaps is even simpler. You can install
collective.bloggingmaps by adding it to the eggs line for your instance::

    [instance]
    eggs = collective.bloggingmaps

After updating the configuration you need to run the ''bin/buildout'', which
will take care of updating your system.

.. _buildout: http://pypi.python.org/pypi/zc.buildout

Usage
=====

- install collective.bloggingmaps via Quick Installer

- configure Maps package by following instructions at http://pypi.python.org/pypi/Products.Maps

- set geo location when posting event based blog entries

For more information about how to use blogging maps go to [your-site]/blogging-help.

Copyright and Credits
=====================

collective.bloggingmaps is licensed under the GPL. See LICENSE.txt for details.

Author: `Lukas Zdych (lzdych)`__.

.. _lzdych: mailto:lukas.zdych@gmail.com

__ lzdych_

Homepage: collective.bloggingmaps_.

.. _collective.bloggingmaps: http://plone.org/products/collective.bloggingmaps
