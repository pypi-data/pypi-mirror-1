=====================
iw.recipe.cmd package
=====================

This recipe is used to run one or more command lines

We need some buildout vars::

  >>> import os
  >>> join = os.path.join
  >>> data_dir = join(test_dir, 'data')
  >>> parts_dir = join(data_dir, 'parts')
  >>> buildout = {'instance': {'location': test_dir},
  ...             'buildout': {'directory': test_dir,
  ...             'parts-directory': test_dir}}
  >>> name = 'cmds'

Ok, so now we can touch a file in data_dir::

  >>> test_file = join(data_dir, 'test.txt')

  >>> options = {'cmds': 'touch %s' % test_file,
  ...            'on_install':'true'}

  >>> from iw.recipe.cmd import Recipe
  >>> recipe = Recipe(buildout, name, options)
  >>> path = recipe.install()
  >>> 'test.txt' in os.listdir(data_dir)
  True

And remove it::

  >>> options = {'cmds': 'rm -f %s' % test_file,
  ...            'on_install':'true'}
  >>> recipe = Recipe(buildout, name, options)
  >>> path = recipe.install()
  >>> 'test.txt' in os.listdir(data_dir)
  False

We can run more than one commands::

  >>> cmds = '''
  ... touch %s
  ... rm -f %s
  ... ''' % (test_file, test_file)

  >>> options = {'cmds': cmds,
  ...            'on_install':'true'}
  >>> recipe = Recipe(buildout, name, options)
  >>> path = recipe.install()
  >>> 'test.txt' in os.listdir(data_dir)
  False


