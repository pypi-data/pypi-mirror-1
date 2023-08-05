=========================
iw.recipe.fetcher package
=========================

.. contents::

What is iw.recipe.fetcher ?
===========================

Download an url to a local directory.

How to use iw.recipe.fetcher ?
==============================

The recipe download from an http server::

  >>> server_data = tmpdir('server_data')
  >>> write(server_data, 'file1.txt', 'test1')
  >>> write(server_data, 'file2.txt', 'test1')
  >>> write(server_data, 'file3.txt', 'test1')

  >>> server_url = start_server(server_data)

We need some buildout vars::

  >>> write('buildout.cfg', '''
  ... [buildout]
  ... parts=test1
  ...
  ... [test1]
  ... recipe=iw.recipe.fetcher
  ... urls=
  ...       %(server_url)s/file1.txt
  ... base_url=%(server_url)s
  ... files=
  ...       file2.txt
  ...       file3.txt
  ... ''' % dict(server_url=server_url))


Now we can fetch some urls::
  
  >>> print system(buildout)
  Installing test1.
  <BLANKLINE>



It works::

  >>> ls(sample_buildout, 'test1')
  - file1.txt
  - file2.txt
  - file3.txt


  >>> write('buildout.cfg', '''
  ... [buildout]
  ... parts=test2
  ...
  ... [test2]
  ... recipe=iw.recipe.fetcher
  ... urls=
  ...   http://www.example.com/file1.txt
  ... find-links=%(server_url)s
  ... ''' % dict(server_url=server_url))


Now we can fetch some urls::
  
  >>> print system(buildout)
  Uninstalling test1.
  Installing test2.
  <BLANKLINE>


