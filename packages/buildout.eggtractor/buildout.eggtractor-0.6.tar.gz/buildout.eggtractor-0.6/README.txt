buildout.eggtractor
===================

Q: What is a buildout extension ?

A: http://pypi.python.org/pypi/zc.buildout#extensions

The problem
-----------

When developing zope/plone eggs with buildout I have to edit the buildout
configuration file ( in 3 places ) each time I create/delete/rename a
development egg in the ``src`` directory or in other development directories
(sometime I have more than one).

I have to add/delete/rename the egg in the ``eggs`` option of the 
``[buildout]`` and then add/delete/rename the egg path in the ``develop`` option
of the ``[buildout]`` and in the end add/delete/rename the ``zcml`` option of
the zope ``[instance]`` or in the ``configure.zcml`` file of my policy package.
This is too much specially when the speed is set to development mode. I need a
less boring way to develop.

Solution
--------

``buildout.eggtractor`` is a buildout extension that scans the ``src`` 
directory or a list of directories I give for eggs and picks them up
automatically. So no more editing of the buildout's configuration file.

When ``buildout.eggtractor`` finds an egg in the scanned directory it::

  1. adds the egg to the ``eggs`` option of all zope instance parts or
     to a set of given parts

  2. adds the egg's path in the ``develop`` option of the ``[buildout]``
  
  3. If ``tractor-autoload-zcml`` is not given or set to other thing than
     false, scans the egg folder for ``configure.zcml``, ``meta.zcml`` and
     ``overrides.zcml`` and adds the appropriate zcml entries to the ``zcml``
     option of the zope instance parts or to a set of given parts.

This steps are done on the fly when running buildout. So I can add/delete/rename
an egg and it will be picked up.

NOTE: The extension does not write to the buildout's configuration file.

buildout.eggtractor options
---------------------------

tractor-src-directory:
  A set of directories to scan for development eggs. Defaults to the ``src``
  directory of the buildout.

tractor-target-parts:
  A set of parts to update their ``eggs`` option with eggs found in the 
  ``tractor-src-directory``. Defaults to zope instance parts if any.

tractor-autoload-zcml(boolean):
  Update the ``zcml`` option of ``tractor-target-parts`` with the eggs found
  in ``tractor-src-directory``. Defaults to true

tractor-zcml-top:
  A set of eggs to load their zcml files first. Defaults to an empty set.


How to use it
-------------

Using ``buildout.eggtractor`` is very simple. As said, it is a buildout
extension. All I have to do is to declare it in the ``extensions`` option::

  [buildout]
  parts =
  
  extensions = buildout.eggtractor

That's all. ``buildout.eggtractor`` will scan the ``src`` directory and do its
job every time I run the buildout command.

When I have other directories I want to scan I just add an
``tractor-src-directory`` option in the ``[buildout]`` and add my directories
there::

  [buildout]
  parts =
  
  extensions = buildout.eggtractor
  
  tractor-src-directory = 
                        dev-src1 
                        dev-src2
                        src

In a few cases when the priority of loading zcml files matters. I add the egg to
be loaded first in the ``tractor-zcml-top`` option in the ``[buildout]``::

  [buildout]
  parts =
  
  extensions = buildout.eggtractor
  
  tractor-src-directory = 
            dev-src1 
            dev-src2
            src
            
  tractor-zcml-top = 
            plone.app.mypackage1


If I want to add the eggs found in the development directories to the eggs
option of a given set of parts, I add a ``tractor-target-parts`` option 
and add the parts there::

  [buildout]
  parts = instance1 instance2 instance3
  
  extensions = buildout.eggtractor
  
  tractor-target-parts = instance1 instance3

This way only instance1 and instance3 will be updated.

If I have already other way to include the zcml files (ie: z3c.autoinclude)
and don't want ``eggtractor`` to generate the zcml slugs, I add an
``tractor-autoload-zcml`` option and set it to ``false``


In most cases you will only need to add ``buildout.eggtractor`` to the
``extensions`` option of the ``[buildout]`` without any extra configuration
options.


LIMITATION:
-----------

The extension assumes that the egg name reflects its file system structure

example: if the egg name is com.mustap.www the extension assumes that the file
system structure is one of the following::

  1. com.mustap.www/src/com/mustap/www
  
  2. com.mustap.www/com/mustap/www

This is where the extension looks for configure.zcml, meta.zcml and
overrides.zcml files.

If the egg name has nothing to do with how it is structured on the system,
the extension will ignore it.

XXX: I guess walking through the directory is better than this assumption.

In my case this is not a limitation as I choose my egg names that way.



Mustapha

email: mustap_at_gmail_com

web: http://www.mustap.com
