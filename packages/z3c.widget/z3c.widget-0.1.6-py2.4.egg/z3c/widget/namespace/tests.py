import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup
from zope import component
from zope.app.form.interfaces import IInputWidget
from zope.schema.interfaces import ITextLine
from zope.app.form.browser import TextWidget
from zope.publisher.interfaces.browser import IBrowserRequest

def setUp(test):
    setup.placefulSetUp()
    #factory, adapts=None, provides=None, name=''
    component.provideAdapter(TextWidget,(ITextLine,IBrowserRequest),
                             IInputWidget)
    

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    
    return unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
