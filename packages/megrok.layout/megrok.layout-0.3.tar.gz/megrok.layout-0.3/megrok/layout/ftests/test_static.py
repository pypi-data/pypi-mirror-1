"""
  >>> from megrok.layout import ILayout
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> mongo = Dummy()
  >>> mylayout = getMultiAdapter((mongo, request), ILayout)
  >>> mylayout.static
  <grokcore.view.components.DirectoryResource object at ...>
  >>> mylayout.static['empty.js']
  <zope.app.publisher.browser.fileresource.FileResource object at ...>
"""

import grok
from megrok.layout import Layout


class Dummy(grok.Context):
    pass

class LayoutWithResources(Layout):
    pass

def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite  
