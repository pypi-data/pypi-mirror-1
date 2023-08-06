# external imports
from grokcore.viewlet import view
from grokcore.view import name, template, templatedir, layer
from zope.pagetemplate.interfaces import IPageTemplate

# exposed `megrok.pagetemplate` API
from megrok.pagetemplate.utils import getPageTemplate
from megrok.pagetemplate.components import PageTemplate
