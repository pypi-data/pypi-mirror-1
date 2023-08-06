==========
IngeniSkel
==========

A collection of skeletons for quickstarting projects based on Ingeniweb
products. This package is an extension of ZopeSkel.

Current templates:

- `iw_plone2.5_buildout`_: installs a Zope Instance with a Plone 2.5;
- `iw_python`_: creates a Python namespace package;
- `iw_recipe`_: creates a recipe package for zc.buildout (nested namespace).

Prerequests
===========

If you have installed IngeniSkel throught `easy_install`, you can skip
this section and head to `Installing a Zope Instance`_.

IngeniSkel uses `setuptools` to install all dependencies. To install
it, download `ez_setup.py` and run it with the appropriate Python::

    $ cd /tmp
    $ wget http://peak.telecommunity.com/dist/ez_setup.py
    $ sudo python2.4 ez_setup.py

Once `setuptools` is installed, you can run IngeniSkel setup::

    $ sudo python2.4 setup.py install

iw_plone2.5_buildout
====================

To create a Zope instance, simply run paster, which was installed by
IngeniSkel, with the `iw_plone2.5_buildout` template, and the path where you
want the instance to be created::

    $ paster create -t iw_plone2.5_buildout /tmp/my_project

A script called `bootstrap.py` has to be run in the folder created by the
paster::

    $ cd /tmp/my_project
    $ python2.4 bootstrap.py

Once the bootstrap is done, you can run the `buildout` script, and answer
to all questions (default answer will fit a generic usage)::

    $ bin/buildout

That's all ! Zope can then be launched with the `instance` script::

    $ ./bin/instance fg

iw_python
=========

To create a new namespaced package for your Zope application, you can use the
provided template: `iw_python`. For example, if you want to create the 
`iw.package`, go into your `src` subfolder, and call paster::

    $ cd /tmp/my_project/src
    $ paster create -t iw_plone iw.package

An egg-compatible structure is created, that can be used in the Zope instance.
To add it to the project, insert it into `buildout.cfg`::

    [buildout]
    ...
    eggs =
    ...
        iw.package

	develop =
	    src/iw.package
	    
And run buildout again::

    $ cd /tmp/my_project
    $ bin/buildout

This will develop your new package.

iw_recipe
=========

To create a new recipe, use this template, with a nested namespace that starts
with `iw.recipe`::

    $ cd /tmp/my_project/src
    $ paster create -t iw_recipe iw.recipe.package

This will create a nested namespace with an entry point for you recipe.
The next step is to write the recipe in the __init__.py file of the package::

    $ cd /tmp/my_project/src/iw.recipe.package/iw/recipe/package
    $ vi __init__.py

-> code ! ;)

IngeniSkel is an Ingeniweb_ product.

.. _Ingeniweb: http://www.ingeniweb.com

