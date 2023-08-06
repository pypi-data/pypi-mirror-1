"""
  >>> from megrok.pagetemplate import testing
  >>> testing.grok(__name__)
  Traceback (most recent call last):
  ...
  ConfigurationConflictError: Conflicting configuration actions
      For: ('adapter', (<class 'megrok.pagetemplate.tests.test_samename_failure.View'>, <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>), <InterfaceClass zope.pagetemplate.interfaces.IPageTemplate>, 'judith')...
"""

import megrok.pagetemplate
import grokcore.view
import grokcore.viewlet 

from zope.component import getMultiAdapter
from zope.pagetemplate.interfaces import IPageTemplate

grokcore.view.templatedir("templates")


class Context(grokcore.view.Context):
    """A context.
    """


class View(grokcore.view.View):
    """A very simple view.
    """
    def render(self):
        return u'nothing here to be seen !'


class JudithTemplate(megrok.pagetemplate.PageTemplate):
    grokcore.viewlet.view(View)
    grokcore.viewlet.name('judith')
    grokcore.view.template('judith')


class EmmaTemplate(megrok.pagetemplate.PageTemplate):
    grokcore.viewlet.view(View)
    grokcore.viewlet.name('judith')
    grokcore.view.template('emma')


def test_suite():
    from zope.testing import doctest
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    return suite
