================
iw.recipe.template package
================

.. contents::

What is iw.recipe.template ?
==================

Explain here what is the purpose of iw.recipe.template.

How to use iw.recipe.template ?
=====================

We need some buildout vars::

  >>> data_dir = join(test_dir, 'data')
  >>> parts_dir = join(data_dir, 'parts')
  >>> buildout = {'instance': {'location': test_dir},
  ...             'buildout': {'directory': test_dir,
  ...             'install-from-cache': False,
  ...             'download-cache':False,
  ...             'parts-directory': parts_dir}}
  >>> name = 'template'

And a template::

  >>> template = join(data_dir, 'template.py_impl')
  >>> open(template, 'w').write('''My template is named "$name"''')

Then, the recipe should work::

  >>> from iw.recipe.template import Recipe
  >>> options = {}
  >>> options['source'] = template
  >>> options['destination'] = join(data_dir, 'template.py')
  >>> recipe = Recipe(buildout, name, options)
  >>> filename = recipe.install()

Here is the result::

  >>> print open(options['destination']).read()
  My template is named "template"



