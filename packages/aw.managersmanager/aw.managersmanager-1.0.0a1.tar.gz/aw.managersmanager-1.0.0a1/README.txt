==================
aw.managersmanager
==================

This component provides a console utility ``plonemanagers`` and a Plone
component that adds or removes managers on all Plone sites in a set of Zope
clusters.

Note that ``aw.managersmanager`` has a client command line utility and a Zope
component server side counterpart.

Installation
============

Either (typically on a client, you don't need Zope or anything else) ::

  $ easy_install aw.managersmanager

Or in a buildout (with Zope / Plone installation) ::

  [buildout]
  ...
  parts = 
    ...
    managersmanager
  ...
  eggs =
    ...
    aw.managersmanager
    ...
  [managersmanager]
  recipe = zc.recipe.egg
  eggs =
    ...
    aw.managersmanager
    ...
  [instance]
  recipe = plone.recipe.zope2instance
  ...
  zcml = 
    ...
    aw.managersmanager

Add a config file in your home directory named ``.managersmanager``. Or run once
the ``plonemanagers`` console tool that will create a skeleton if this file does
not exist. See `Config file`_ below.

Usage
=====

Common usages, respectively for adding a manager, listing Plone sites,
removing a manager and asking for help::

  $ plonemanagers adduser <login> <password>

  $ plonemanagers list

  $ plonemanagers deluser <login>

  $ plonemanagers --help


Config file
===========

The configuration file is named ``.managersmanager`` and is located in your user
default directory.

If you don't have such (mandatory) config file, a default one will becreated the
first time you invoke ``plonemanagers``. This default config file is fully
commented out, such it's pretty easy to tweak your client installation to fit
all the Zope / Plone clusters under your control.

Its content must match these rules ::

  # Main section (required)
  [main]

  # All Zope clusters
  clusters =
    somecluster
    anothercluster
    ...

  # HTTP connection timeout (in seconds)
  timeout = 10

  # Each item in above "clusters" must have its sections
  [somecluster]

  # One or more root URL (the ZEO clients of this cluster)
  root-urls = 
    http://somehost:8080
    http://otherhost:8080

  # A *Zope root* manager login
  login = admin
  password = mysecret

  # Same thing for all clusters
  [anothercluster]
  ...


License
=======

GPL

Support
=======

Tracker: http://plone.org/products/aw-managersmanager/issues

Mail support: `Ingeniweb support <support@ingeniweb.com>`_

Subversion repository
=====================

http://svn.plone.org/svn/collective/aw.managersmanager
