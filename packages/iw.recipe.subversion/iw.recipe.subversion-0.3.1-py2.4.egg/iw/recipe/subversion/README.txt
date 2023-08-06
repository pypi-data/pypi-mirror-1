====================
iw.recipe.subversion
====================

This product is used to download packages from svn and tar them in a directory.

We need some buildout vars::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts=svn-package
    ...
    ... [svn-package]
    ... recipe=iw.recipe.subversion
    ... urls=
    ...   file:///%s/my_package/trunk my_package
    ... """ % repository)

We need a repository::

    >>> create_repository()

Then, the recipe should work::

    >>> print system(buildout)
    Installing svn-package.
    A    /sample-buildout/parts/svn-package/my_package/__init__.py
    A    /sample-buildout/parts/svn-package/my_package/sub
    A    /sample-buildout/parts/svn-package/my_package/sub/__init__.py
    A    /sample-buildout/parts/svn-package/my_package/README.txt
    ...
    <BLANKLINE>

Ok, we got it::

    >>> ls('parts', 'svn-package')
    d my_package

If a download-cache directory is given, then an archive is created in the
specified path::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... download-cache=cache
    ... parts=svn-package
    ...
    ... [svn-package]
    ... recipe=iw.recipe.subversion
    ... urls=
    ...   file:///%s/my_package/trunk my_package
    ... """ % repository)

    >>> rmtree('parts')
    >>> cache = join(os.getcwd(), 'cache')
    >>> mkdir(cache)

    >>> print system(buildout)
    Creating directory '/sample-buildout/parts'.
    Uninstalling svn-package.
    Installing svn-package.
    A    /sample-buildout/parts/svn-package/my_package/__init__.py
    A    /sample-buildout/parts/svn-package/my_package/sub
    A    /sample-buildout/parts/svn-package/my_package/sub/__init__.py
    A    /sample-buildout/parts/svn-package/my_package/README.txt
    ...
    Creating archive: my_package-dev.tar.gz

    >>> ls(cache)
    d  dist
    -  my_package-dev.tar.gz

Ok, now we can work offline. The package will be installed from the cache
directory::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... install-from-cache=true
    ... download-cache=cache
    ... parts=svn-package
    ...
    ... [svn-package]
    ... recipe=iw.recipe.subversion
    ... urls=
    ...   file:///%s/my_package/trunk my_package
    ... """ % repository)

    >>> rmtree(repository)
    >>> rmtree('parts')
    >>> print system(buildout)
    Creating directory '/sample-buildout/parts'.
    Uninstalling svn-package.
    Installing svn-package.
    <BLANKLINE>


    >>> ls('parts', 'svn-package')
    d  my_package

    >>> ls('parts', 'svn-package', 'my_package')
    -  README.txt
    -  __init__.py
    d  sub

Well, it's ok for a trunk url. But when working with tagged version, we don't want to use subversion if we already have an archive::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... download-cache=cache
    ... parts=svn-package
    ...
    ... [svn-package]
    ... recipe=iw.recipe.subversion
    ... urls=
    ...   file:///%s/my_package/tags/v1_0_0 my_package
    ... """ % repository)


At the first time, we need to update and built the archive::

    >>> create_repository()
    >>> print system(buildout)
    Uninstalling svn-package.
    Installing svn-package.
    A    /sample-buildout/parts/svn-package/my_package/__init__.py
    A    /sample-buildout/parts/svn-package/my_package/sub
    A    /sample-buildout/parts/svn-package/my_package/sub/__init__.py
    A    /sample-buildout/parts/svn-package/my_package/README.txt
    ...
    Creating archive: my_package-v1_0_0.tar.gz
    <BLANKLINE>

    >>> ls('parts', 'svn-package', 'my_package')
    d  .svn
    -  README.txt
    -  __init__.py
    d  sub

    >>> ls(cache)
    d  dist
    -  my_package-v1_0_0.tar.gz

Then we work can work offline::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... offline=true
    ... download-cache=cache
    ... parts=svn-package
    ...
    ... [svn-package]
    ... recipe=iw.recipe.subversion
    ... urls=
    ...   file:///%s/my_package/tags/v1_0_0 my_package
    ... """ % repository)

    >>> rmtree(repository)
    >>> rmtree('parts')
    >>> print system(buildout)
    Creating directory '/sample-buildout/parts'.
    Uninstalling svn-package.
    Installing svn-package.
    <BLANKLINE>

    >>> ls('parts', 'svn-package', 'my_package')
    -  README.txt
    -  __init__.py
    d  sub

