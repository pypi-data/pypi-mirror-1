import unittest, doctest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from lovely.gae.testing import DBLayer

# use the lovely.gae test layer which sets up an in-memory database
# stub, which is cleaned after each test.
dbLayer = DBLayer('DBLayer')

def test_suite():
    views = DocFileSuite(
        'views.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        )
    s = unittest.TestSuite((views,),)
    s.layer = dbLayer
    return s
