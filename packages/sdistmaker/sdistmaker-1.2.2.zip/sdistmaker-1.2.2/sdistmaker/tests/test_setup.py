import os
import re
import tempfile

from zope.testing import renormalizing
import z3c.testsetup


checker = renormalizing.RENormalizing([
    (re.compile(r'\S+/pypi'), 'PYPI'),
    (re.compile(r'\S+/bin/python'), 'python'),
    ])


def setup(test):
    test.tempdir = tempfile.mkdtemp()
    test.pypidir = os.path.join(test.tempdir, 'pypi')
    os.mkdir(test.pypidir)
    test.globs.update({'pypidir': test.pypidir,
                       })


def teardown(test):
    pass


test_suite = z3c.testsetup.register_all_tests(
    'sdistmaker',
    checker=checker)
