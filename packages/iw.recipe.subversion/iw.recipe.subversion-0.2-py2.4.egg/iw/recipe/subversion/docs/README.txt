====================
iw.recipe.subversion
====================

This product is used to download packages from svn and tar them in a directory.

We need some buildout vars::

  >>> data_dir = join(test_dir, 'data')
  >>> parts_dir = join(data_dir, 'parts')
  >>> buildout = {'instance': {'location': test_dir},
  ...             'buildout': {'directory': test_dir,
  ...             'install-from-cache': False,
  ...             'download-cache':False,
  ...             'parts-directory': parts_dir}}
  >>> name = 'svn-packages'

The recipe will checkout the package from his repository and put it in the
section.  For testing, we need a local repository::

  >>> repository = join(test_dir, 'test_repos')
  >>> if isdir(repository): rmtree(repository)
  >>> copytree(join(test_dir, 'repos'), repository)
  >>> if isdir(os.path.join(parts_dir, 'svn-packages')):
  ...     rmtree(os.path.join(parts_dir, 'svn-packages'))

Then, the recipe should work::

  >>> options = {
  ...   'urls':'file:///%s/my_package/trunk my_package' % repository}
  >>> from iw.recipe.subversion import Recipe
  >>> recipe = Recipe(buildout, name, options)
  >>> os.path.join(parts_dir, 'svn-packages') == recipe.install()
  True

Ok, we got it::

  >>> ls(parts_dir, 'svn-packages')
  my_package

If a download-cache directory is given, then an archive is created in the
specified path::

  >>> cache = join(data_dir, 'cache')
  >>> buildout['buildout']['download-cache'] = cache
  >>> recipe = Recipe(buildout, name, options)

  >>> if isdir(cache): rmtree(cache)

  >>> files = recipe.install()

  >>> ls(cache)
  my_package-r4.tar.gz

Ok, now we can work offline. The package will be installed from the cache
directory::

  >>> rmtree(repository)
  >>> rmtree(parts_dir)
  >>> buildout['buildout']['install-from-cache'] = 'true'
  >>> buildout['buildout']['download-cache'] = cache
  >>> recipe = Recipe(buildout, name, options)
  >>> files = recipe.install()

  >>> ls(parts_dir, 'svn-packages')
  my_package

  >>> ls(parts_dir, 'svn-packages', 'my_package')
  README.txt 
  __init__.py
  sub

Well, it's ok for a trunk url. But when working with tagged version, we don't want to use subversion if we already have an archive::

  >>> copytree(join(test_dir, 'repos'), repository)
  >>> rmtree(parts_dir)
  >>> options = {
  ...   'urls':'file:///%s/my_package/tags/v1_0_0 my_package' % repository}
  >>> buildout['buildout']['install-from-cache'] = 'false'
  >>> buildout['buildout']['download-cache'] = cache
  >>> recipe = Recipe(buildout, name, options)


At the first time, we need to update and built the archive::

  >>> recipe.need_update
  True

  >>> files = recipe.install()

But when we have an archive, we don't need to::

  >>> recipe.need_update
  False

Then we work offline in an online mode::

  >>> rmtree(repository)
  >>> files = recipe.install()

Test update::

  >>> recipe.update() is not None
  True

