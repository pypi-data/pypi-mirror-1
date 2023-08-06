## -*- coding: utf-8 -*-
import unittest
import doctest
import os, sys
import os.path

import gocept.cvs
import cvsrep
import zc.buildout.testing


FLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('gocept.cvs', test)


def tearDown(test):
    zc.buildout.testing.buildoutTearDown(test)


def test_suite():
    return unittest.TestSuite([doctest.DocFileSuite(
        os.path.join(os.path.dirname(__file__), 'README.txt'),
        optionflags=FLAGS,
        globs=globals(),
        setUp=setUp,
        tearDown=tearDown,
        module_relative=False)])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
