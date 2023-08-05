=========================
iw.recipe.fetcher package
=========================

.. contents::

What is iw.recipe.fetcher ?
===========================

Download an url to a local directory.

How to use iw.recipe.fetcher ?
==============================

We need some buildout vars::

  >>> data_dir = join(test_dir, 'data')
  >>> parts_dir = join(data_dir, 'parts')
  >>> buildout = {'instance': {'location': test_dir},
  ...             'buildout': {'directory': test_dir,
  ...             'install-from-cache': 'false',
  ...             'download-cache':'false',
  ...             'parts-directory': parts_dir}}
  >>> name = 'utilities'


Now we can fetch some urls::

  >>> options = {
  ...   'urls':'http://garr.dl.sourceforge.net/sourceforge/mingw/MinGW-5.1.3.exe'}
  >>> from iw.recipe.fetcher import Recipe
  >>> recipe = Recipe(buildout, name, options)
  >>> recipe.install()

It works::

  >>> ls(os.path.join(parts_dir, name))
  MinGW-...exe


