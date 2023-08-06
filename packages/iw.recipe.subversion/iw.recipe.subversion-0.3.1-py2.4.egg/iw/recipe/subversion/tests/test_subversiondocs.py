# -*- coding: utf-8 -*-
"""
Doctest runner for 'iw.recipe.subversion'.
"""
__docformat__ = 'restructuredtext'

import unittest
import zc.buildout.tests
import zc.buildout.testing
from shutil import copytree, rmtree
import os
from os.path import join

from zope.testing import doctest, renormalizing

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

test_dir = os.path.split(__file__)[0]

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('iw.recipe.subversion', test)
    repository = os.path.join(test_dir, 'test_repos')
    def create_repository():
        try:
            rmtree(repository)
        except:
            pass
        copytree(os.path.join(test_dir, 'repos'), repository)
    test.globs['create_repository'] = create_repository
    test.globs['repository'] = repository


def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                '../README.txt',
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
                globs=globals(),
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        zc.buildout.testing.normalize_path,
                        ]),
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
