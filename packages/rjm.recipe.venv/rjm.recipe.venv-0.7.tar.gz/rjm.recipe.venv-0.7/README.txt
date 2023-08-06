rjm.recipe.venv
===============

This is a simple zc.buildout recipe that will use the virtualenv
package to turn the buildout root into a sandboxed virtual python
environment.  It is especially useful in conjunction with
gp.recipe.pip, which can then be used to install python packages into
the virtualenv that has been created.


Supported Options
=================

venv_options:

    Extra options that will be used when the virtualenv command is
    invoked.  These should match exactly what would be used on a
    command line.

distutils_urls:

    This option can be set to a list of URLs, each of which should
    point to an archive (tarball, zip, etc.) of a python package which
    supports simple distutils installation (i.e. 'python setup.py
    install').  Each of these packages will be installed into the
    virtualenv sandbox.  This is useful for installing certain older
    packages that do not work with pip, such as egenix-mx-base.


Example Usage
=============

This is a very simple buildout file that creates a virtualenv with no
site packages and using distribute.  It then installs egenix-mx-base
using distutils, and the latest version of Pylons and all of its
dependencies using pip::

  [buildout]
  parts =
      venv
      pip

  [venv]
  recipe = rjm.recipe.venv
  venv_options = --no-site-packages --with-distribute
  distutils_urls =
      http://downloads.egenix.com/python/egenix-mx-base-3.1.2.tar.gz

  [pip]
  recipe = gp.recipe.pip
  virtualenv = ${buildout:directory}
  install = pylons
