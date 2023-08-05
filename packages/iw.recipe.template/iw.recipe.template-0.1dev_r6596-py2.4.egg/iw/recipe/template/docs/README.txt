==========================
iw.recipe.template package
==========================

.. contents::

What is iw.recipe.template ?
============================

iw.recipe.template is a zc.buildout recipe to build template based
file/scripts

It also provide some recipe to build Zope2, Zope3 and Squid vhosts config
file for apache.

How to use iw.recipe.template ?
=====================

We need a buildout config file::

  >>> server = start_server(test_dir)

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = template.txt
  ...
  ... [template.txt]
  ... recipe = iw.recipe.template
  ... source = %s/template.txt_impl
  ... destination = %s/
  ... """ % (sample_buildout, sample_buildout))

And a template::

  >>> template = join(sample_buildout, 'template.txt_impl')
  >>> open(template, 'w').write('''My template is named "$name"''')


Then, the recipe should work::

  >>> print system(buildout)
  Installing template.txt.
  template.txt: Generated file 'template.txt'.



Here is the result::

  >>> print open(join(sample_buildout, 'template.txt')).read()
  My template is named "template.txt"


Now we can generate an executable::  

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = script
  ...
  ... [script]
  ... recipe = iw.recipe.template:script
  ... source = %s/template.py_impl
  ... destination = %s/
  ... """ % (sample_buildout, sample_buildout))


And a template::

  >>> template = join(sample_buildout, 'template.py_impl')
  >>> open(template, 'w').write('''
  ... import sys
  ... print 'this is the script named "$name"'
  ... ''')


  >>> print system(buildout)
  Uninstalling template.txt.
  Installing script.
  script: Generated script 'script'.

Here is the result::

  >>> print open(join(sample_buildout, 'script')).read()
  #!/.../bin/python
  <BLANKLINE>
  import sys
  print 'this is the script named "script"'
  <BLANKLINE>

  >>> print system(join(sample_buildout, 'script'))
  this is the script named "script"
