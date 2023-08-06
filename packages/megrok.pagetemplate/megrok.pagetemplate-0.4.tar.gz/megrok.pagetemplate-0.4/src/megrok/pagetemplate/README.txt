===================
megrok.pagetemplate
===================

Introduction
------------

`megrok.pagetemplate` is a thin Grok layer above zope.pagetemplate
package. It allows the developper to register IPageTemplate components
using grokked components. The syntax is meant to be very simple and
readable. `megrok.pagetemplate` only provides one component named
PageTemplate and uses the basic grokcore.view and grokcore.viewlet
directives : name, view, context, layer. To make it even simplier and
straightforward, it uses the grokcore.view template registry to
register the template files associated to the pagetemplate component.


Getting started
---------------

First, we import our dependencies::

  >>> import grokcore.view as view
  >>> import megrok.pagetemplate as pt
  >>> from grokcore.component.testing import grok, grok_component
  

A complete yet self-explanatory example
---------------------------------------

To get started with the code itself, let's explain the concept behind
the PageTemplate component. The display is usually handled by the a
dedicated component: the View. The View is a multi adapter, adapting
the context and the request. It provides a rendering method
(__call__, usually). If we want to customize a View, we need to
subclass it or override it. In both case, we end up with a new
View and some code might have to be duplicated.

The PageTemplate component allows you to interact at the rendering
level. This new component implements the zope.pagetemplate
IPageTemplate interface and is registered as a multi adapter, adapting
a View and a Layer (request type). This PageTemplate can be named, for
more customization possibilities.

Let's build a concrete example to get into the concept. First, we need a
context. Our usecase will be to provide different renderings for an
adorable animal : the Mammoth. First, let's create our mammoth and a
simple view that displays it::


  >>> from zope.component import getMultiAdapter
  >>> from zope.pagetemplate.interfaces import IPageTemplate

  >>> class Mammoth(view.Context):
  ...     """A furry pachyderm
  ...     """
  ...     nickname = u"Grokky" 


  >>> class MammothView(view.View):
  ...     """A view that display a mammoth
  ...     """
  ...	  view.context(Mammoth)
  ...
  ...	  def update(self):
  ...	      self.mammoth_name = u"My name is %s." % self.context.nickname
  ...
  ...	  def render(self):
  ...	      template = getMultiAdapter((self, self.request), IPageTemplate)
  ...	      return template()

  >>> grok_component('my_mammoth_view', MammothView)
  True

As we can see here, the View render method is a call to the
PageTemplate component. It will render the template found by the
registry lookup.


To be complete, here, we'll provide a IPageTemplate component::

  >>> class NakedMammoth(pt.PageTemplate):
  ...     """A mammoth shown in its simpliest apparel
  ...     """
  ...     pt.view(MammothView)
  ...     template = view.PageTemplate(
  ...        '<span tal:replace="view/mammoth_name" /> I am naked !'
  ...        )

  >>> grok_component('NakedMammoth', NakedMammoth)
  True

Now that our template is registered, we can try to summon the view and
to render it::

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> mammoth = Mammoth()

  >>> mnv = getMultiAdapter((mammoth, request), name="mammothview")
  >>> print mnv()
  My name is Grokky. I am naked !
  <BLANKLINE>
  
Our Mammoth is rendered as expected. Though, we cannot decently leave
this creature naked. It needs some fur to face the harsh temperature
of the Siberian winter.

In order to customize our Mammoth rendering, to change it from Naked to
Furry, we'll create a skin on which we'll register our new 'furry'
template component::

  >>> from zope.publisher.interfaces import browser
  >>> class IFurryLayer(browser.IDefaultBrowserLayer):
  ...     """A layer for furry animals.
  ...     """
  >>> furry_request = TestRequest(skin=IFurryLayer)


  >>> class FurryMammoth(pt.PageTemplate):
  ...     """A mammoth shown in its simpliest apparel
  ...     """
  ...     pt.view(MammothView)
  ...     pt.layer(IFurryLayer)
  ...     template = view.PageTemplate(
  ...        '<span tal:replace="view/mammoth_name" /> I am all furry !'
  ...        )

  >>> grok_component('FurryMammoth', FurryMammoth)
  True

Our new template registered, we are now able to test if everything worked
as intended. Using the new skin, our Mammoth should now be furry::

  >>> mfv = getMultiAdapter((mammoth, furry_request), name="mammothview")
  >>> print mfv()
  My name is Grokky. I am all furry !
  <BLANKLINE>

Note - we can query our component with a very convenient function::

  >>> print pt.getPageTemplate(mfv, furry_request)
  <megrok.pagetemplate.components.ViewPageTemplate object at ...>

Awesome. Our Mammoth is now fully prepared to face the cold. Though,
let's make sure the simpliest request strip the animal from its warm
hairs::

  >>> mnv = getMultiAdapter((mammoth, request), name="mammothview")
  >>> print mnv()
  My name is Grokky. I am naked !
  <BLANKLINE>

That works. Enjoy !
