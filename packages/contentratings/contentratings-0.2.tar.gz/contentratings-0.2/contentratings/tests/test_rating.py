import unittest
from zope.testing.doctestunit import DocFileSuite
from zope.app.tests import ztapi, placelesssetup
try:
    from zope.app.annotation.interfaces import IAnnotations
    from zope.app.annotation.interfaces import IAttributeAnnotatable
    from zope.app.annotation.attribute import AttributeAnnotations
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation.interfaces import IAnnotations
    from zope.annotation.interfaces import IAttributeAnnotatable
    from zope.annotation.attribute import AttributeAnnotations

from contentratings.interfaces import IEditorRatable
from contentratings.interfaces import IUserRatable
from contentratings.interfaces import IEditorialRating
from contentratings.interfaces import IUserRating
from contentratings.rating import EditorialRating
from contentratings.rating import UserRating

def setUp(test):
    placelesssetup.setUp(test)
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)
    ztapi.provideAdapter(IEditorRatable, IEditorialRating, EditorialRating)
    ztapi.provideAdapter(IUserRatable, IUserRating, UserRating)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     package='contentratings',
                     setUp=setUp,
                     tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
