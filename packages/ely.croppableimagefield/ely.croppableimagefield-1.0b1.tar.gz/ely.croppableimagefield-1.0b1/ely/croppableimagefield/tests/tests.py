import unittest
from zope.testing import doctest
from Testing import ZopeTestCase
from os.path import join, dirname
from Products.PloneTestCase import PloneTestCase


optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


class ImageUpload:
    """Utility object that supplies parts of the interface of
    FileUpload used by plonephotoupload.
    """

    def __init__(self, filename):
        self.file = open(join(dirname(__file__), 'input', filename))
        self.filename = filename
        self.headers = {'content_type': 'application/octet-stream'}

    def read(self, *args):
        return self.file.read(*args)

    def seek(self, *args):
        return self.file.seek(*args)

    def tell(self, *args):
        return self.file.tell(*args)


PloneTestCase.setupPloneSite()


def test_suite():
    return unittest.TestSuite([
        ZopeTestCase.ZopeDocFileSuite(
            'README.txt',
            package='ely.croppableimagefield',
            optionflags=optionflags,
            test_class=PloneTestCase.FunctionalTestCase,
            ),
        ])
