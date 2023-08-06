Supported options
=================

The recipe supports the following options:

.. Note to recipe author!
   ----------------------
   For each option the recipe uses you shoud include a description
   about the purpose of the option, the format and semantics of the
   values it accepts, whether it is mandatory or optional and what the
   default value is if it is omitted.

venv
    Virtualenv id. The virtualenv is build in `parts/venv` (Default to pip)

indexes
    Extra indexes url.

install
    A list of string passed to pip directly. A sub process is run per line.
    This allow to use `--install-option`.

editables
    A list of svn url. (`svn+http://myrepo/svn/MyApp#egg=MyApp`)

This recipe is based on `zc.recipe.egg#scripts
<http://pypi.python.org/pypi/zc.recipe.egg#id23>`_ so options used by this
recipe should also works.

Example usage
=============

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = test1
    ...
    ... [test1]
    ... recipe = gp.recipe.pip
    ... eggs = PasteScript
    ... interpreter = python
    ... scripts =
    ...     paster = paster
    ... """)

Running the buildout gives us::

    >>> print 'start', system(buildout) 
    start...
    Installing test1.
    Creating new virtualenv environment ...
    ...
    Successfully installed PasteScript
    ...
    Generated script '/sample-buildout/bin/paster'.
    Generated interpreter '/sample-buildout/bin/python'.
    <BLANKLINE>

Scripts are generated::

    >>> ls('bin')
    -  buildout
    -  paster
    -  python

Here is a config file used to install Deliverance::

  [buildout]
  parts = deliverance
  download-cache = download

  [deliverance]
  recipe = gp.recipe.pip
  install =
      Cython
      --install-option=--static-deps lxml==2.2alpha1
      http://deliverance.openplans.org/dist/Deliverance-snapshot-latest.pybundle

