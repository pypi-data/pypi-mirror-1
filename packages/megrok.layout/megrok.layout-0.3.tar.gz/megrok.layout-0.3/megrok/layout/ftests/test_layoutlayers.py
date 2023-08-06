"""
  >>> from zope.app.testing.functional import getRootFolder
  >>> getRootFolder()["a"] = A()
  >>> getRootFolder()["b"] = B()
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  
  >>> browser.open("http://localhost/++skin++Basic/a/@@myview") 
  >>> print browser.contents
  <div> A Layout </div>

  >>> browser.open("http://localhost/++skin++myskin/a/@@myview") 
  >>> print browser.contents
  <div> A2 Layout </div>
  
  >>> browser.open("http://localhost/++skin++myskin/b/@@myviewb")
  >>> print browser.contents
  <div> B Layout </div>
"""

import grok

from zope import interface
from megrok.layout import Layout, Page 
from zope.app.basicskin import IBasicSkin

grok.layer(IBasicSkin)

class MySkinLayer(IBasicSkin):
    pass

class MySkin(MySkinLayer):
    grok.skin('myskin')

class A(grok.Context):
    pass

class B(grok.Context):
    pass

class ALayout(Layout):
    grok.context(A)

    def render(self):
	return "<div> A Layout </div>"

class A2Layout(Layout):
    grok.context(A)
    grok.layer(MySkinLayer)

    def render(self):
	return "<div> A2 Layout </div>"

class BLayout(Layout):
    grok.context(B)
    grok.layer(MySkinLayer)

    def render(self):
	return "<div> B Layout </div>"


class MyView(Page):
    grok.context(interface.Interface)

    def render(self):
        return "MYVIEW"

class MyViewB(Page):
    grok.context(interface.Interface)
    grok.layer(MySkinLayer)

    def render(self):
        return "MYVIEW"

def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite  
