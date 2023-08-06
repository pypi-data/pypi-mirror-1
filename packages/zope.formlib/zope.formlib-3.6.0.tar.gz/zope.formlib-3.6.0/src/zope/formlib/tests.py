##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: tests.py 100109 2009-05-18 20:01:53Z icemac $
"""
import unittest
import os
import re
import pytz

import zope.component.testing
import zope.i18n.testing
import zope.interface.common.idatetime
import zope.publisher.interfaces
import zope.publisher.interfaces.browser
import zope.schema.interfaces
import zope.testing.renormalizing
import zope.traversing.adapters

import zope.app.form.browser
import zope.app.form.browser.exception
import zope.app.form.browser.interfaces
import zope.app.form.interfaces

from zope.app.testing import functional

import zope.formlib.form
import zope.formlib.interfaces
import zope.app.pagetemplate.namedtemplate

FormlibLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'FormlibLayer', allow_teardown=True)



@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
@zope.component.adapter(zope.publisher.interfaces.IRequest)
def requestToTZInfo(request):
    return pytz.timezone('US/Hawaii')

def pageSetUp(test):
    zope.component.testing.setUp(test)
    zope.component.provideAdapter(
        zope.traversing.adapters.DefaultTraversable,
        [None],
        )

@zope.component.adapter(zope.formlib.interfaces.IForm)
@zope.app.pagetemplate.namedtemplate.NamedTemplateImplementation
def TestTemplate(self):
    status = self.status
    if status:
        status = zope.i18n.translate(status,
                                     context=self.request,
                                     default=self.status)
        if getattr(status, 'mapping', 0):
            status = zope.i18n.interpolate(status, status.mapping)
        print status

    result = []

    if self.errors:
        for error in self.errors:
            result.append("%s: %s" % (error.__class__.__name__, error))

    for w in self.widgets:
        result.append(w())
        error = w.error()
        if error:
            result.append(str(error))

    for action in self.availableActions():
        result.append(action.render())

    return '\n'.join(result)

def formSetUp(test):
    zope.component.testing.setUp(test)
    zope.i18n.testing.setUp(test)
    zope.component.provideAdapter(
        zope.app.form.browser.TextWidget,
        [zope.schema.interfaces.ITextLine,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IInputWidget,
        )
    zope.component.provideAdapter(
        zope.app.form.browser.FloatWidget,
        [zope.schema.interfaces.IFloat,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IInputWidget,
        )
    zope.component.provideAdapter(
        zope.app.form.browser.UnicodeDisplayWidget,
        [zope.schema.interfaces.IInt,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IDisplayWidget,
        )
    zope.component.provideAdapter(
        zope.app.form.browser.IntWidget,
        [zope.schema.interfaces.IInt,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IInputWidget,
        )
    zope.component.provideAdapter(
        zope.app.form.browser.UnicodeDisplayWidget,
        [zope.schema.interfaces.IFloat,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IDisplayWidget,
        )
    zope.component.provideAdapter(
        zope.app.form.browser.UnicodeDisplayWidget,
        [zope.schema.interfaces.ITextLine,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IDisplayWidget,
        )
    zope.component.provideAdapter(
        zope.app.form.browser.DatetimeDisplayWidget,
        [zope.schema.interfaces.IDatetime,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IDisplayWidget,
        )
    zope.component.provideAdapter(
        zope.app.form.browser.DatetimeWidget,
        [zope.schema.interfaces.IDatetime,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IInputWidget,
        )
    zope.component.provideAdapter(
        zope.app.form.browser.exception.WidgetInputErrorView,
        [zope.app.form.interfaces.IWidgetInputError,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.browser.interfaces.IWidgetInputErrorView,
        )
    zope.component.provideAdapter(TestTemplate, name='default')
    zope.component.provideAdapter(requestToTZInfo)
    zope.component.provideAdapter(
        zope.formlib.form.render_submit_button, name='render')

# Classes used in tests

class IOrder(zope.interface.Interface):
    identifier = zope.schema.Int(title=u"Identifier", readonly=True)
    name = zope.schema.TextLine(title=u"Name")
    min_size = zope.schema.Float(title=u"Minimum size")
    max_size = zope.schema.Float(title=u"Maximum size")
    now = zope.schema.Datetime(title=u"Now", readonly=True)

class IDescriptive(zope.interface.Interface):
    title = zope.schema.TextLine(title=u"Title")
    description = zope.schema.TextLine(title=u"Description")


class Order:
    zope.interface.implements(IOrder)
    identifier = 1
    name = 'unknown'
    min_size = 1.0
    max_size = 10.0


class Descriptive(object):
    zope.component.adapts(IOrder)
    zope.interface.implements(IDescriptive)
    def __init__(self, context):
        self.context = context

    def title():
        def get(self):
            try:
                return self.context.__title
            except AttributeError:
                return ''
        def set(self, v):
            self.context.__title = v
        return property(get, set)
    title = title()

    def description():
        def get(self):
            try:
                return self.context.__description
            except AttributeError:
                return ''
        def set(self, v):
            self.context.__description = v
        return property(get, set)
    description = description()


def makeSureRenderCanBeCalledWithoutCallingUpdate():
    """\

    >>> class MyForm(zope.formlib.form.EditForm):
    ...     form_fields = zope.formlib.form.fields(
    ...         IOrder, keep_readonly=['identifier'])

    >>> from zope.publisher.browser import TestRequest
    >>> myform = MyForm(Order(), TestRequest())
    >>> print myform.render() # doctest: +NORMALIZE_WHITESPACE
    1
    <input class="textType" id="form.name" name="form.name"
           size="20" type="text" value="unknown"  />
    <input class="textType" id="form.min_size" name="form.min_size"
           size="10" type="text" value="1.0"  />
    <input class="textType" id="form.max_size" name="form.max_size"
           size="10" type="text" value="10.0"  />
    <input type="submit" id="form.actions.apply" name="form.actions.apply"
           value="Apply" class="button" />

"""

def make_sure_i18n_is_called_correctly_for_actions():
    """\

We want to make sure that i18n is called correctly.  This is in
response to a bug that occurred because actions called i18n.translate
with incorrect positional arguments.

We'll start by setting up an action:

    >>> import zope.i18nmessageid
    >>> _ = zope.i18nmessageid.MessageFactory('my.domain')
    >>> action = zope.formlib.form.Action(_("MyAction"))

Actions get bound to forms.  We'll set up a test request, create a
form for it and bind the action to the form:

    >>> myform = zope.formlib.form.FormBase(None, 42)
    >>> action = action.__get__(myform)

Button labels are rendered by form.render_submit_button, passing the
bound action.  Before we call this however, we need to set up a dummy
translation domain.  We'll create one for our needs:

    >>> import zope.i18n.interfaces
    >>> class MyDomain:
    ...     zope.interface.implements(zope.i18n.interfaces.ITranslationDomain)
    ...
    ...     def translate(self, msgid, mapping=None, context=None,
    ...                   target_language=None, default=None):
    ...         print msgid
    ...         print mapping
    ...         print context
    ...         print target_language
    ...         print default
    ...         return msgid

    >>> zope.component.provideUtility(MyDomain(), name='my.domain')

Now, if we call render_submit_button, we should be able to verify the
data passed to translate:

    >>> zope.formlib.form.render_submit_button(action)() # doctest: +NORMALIZE_WHITESPACE
    MyAction
    None
    42
    None
    MyAction
    u'<input type="submit" id="form.actions.myaction"
       name="form.actions.myaction" value="MyAction" class="button" />'


"""

def test_error_handling():
    """\

Let's test the getWidgetsData method which is responsible for handling widget
erros raised by the widgets getInputValue method.

    >>> import zope.app.form.interfaces
    >>> class Widget(object):
    ...     zope.interface.implements(zope.app.form.interfaces.IInputWidget)
    ...     def __init__(self):
    ...         self.name = 'form.summary'
    ...         self.label = 'Summary'
    ...     def hasInput(self):
    ...         return True
    ...     def getInputValue(self):
    ...         raise zope.app.form.interfaces.WidgetInputError(
    ...         field_name='summary',
    ...         widget_title=u'Summary')
    >>> widget = Widget()
    >>> inputs = [(True, widget)]
    >>> widgets = zope.formlib.form.Widgets(inputs, 5)
    >>> errors = zope.formlib.form.getWidgetsData(widgets, 'form', {'summary':'value'})
    >>> errors #doctest: +ELLIPSIS
    [<zope.app.form.interfaces.WidgetInputError instance at ...>]

Let's see what happens if a widget doesn't convert a ValidationError
raised by a field to a WidgetInputError. This should not happen if a widget
converts ValidationErrors to WidgetInputErrors. But since I just fixed
yesterday the sequence input widget, I decided to catch ValidationError also
in the formlib as a fallback if some widget doen't handle errors correct. (ri)

    >>> class Widget(object):
    ...     zope.interface.implements(zope.app.form.interfaces.IInputWidget)
    ...     def __init__(self):
    ...         self.name = 'form.summary'
    ...         self.label = 'summary'
    ...     def hasInput(self):
    ...         return True
    ...     def getInputValue(self):
    ...         raise zope.schema.interfaces.ValidationError('A error message')
    >>> widget = Widget()
    >>> inputs = [(True, widget)]
    >>> widgets = zope.formlib.form.Widgets(inputs, 5)
    >>> errors = zope.formlib.form.getWidgetsData(widgets, 'form', {'summary':'value'})
    >>> errors #doctest: +ELLIPSIS
    [<zope.app.form.interfaces.WidgetInputError instance at ...>]

"""

def test_form_template_i18n():
    """\
Let's try to check that the formlib templates handle i18n correctly.
We'll define a simple form:

    >>> from zope.app.pagetemplate import ViewPageTemplateFile
    >>> import zope.i18nmessageid
    >>> _ = zope.i18nmessageid.MessageFactory('my.domain')

    >>> class MyForm(zope.formlib.form.Form):
    ...     label = _('The label')
    ...     status = _('Success!')
    ...     form_fields = zope.formlib.form.Fields(
    ...         zope.schema.TextLine(__name__='name',
    ...                              title=_("Name"),
    ...                              description=_("Enter your name"),
    ...                             ),
    ...         )
    ...     @zope.formlib.form.action(_('Ok'))
    ...     def ok(self, action, data):
    ...         pass
    ...     page = ViewPageTemplateFile("pageform.pt")
    ...     subpage = ViewPageTemplateFile("subpageform.pt")

Now, we should be able to create a form instance:

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> form = MyForm(object(), request)

Unfortunately, the "page" template uses a page macro. We need to
provide a template that it can get one from.  Here, we'll set up a
view that provides the necessary macros:

    >>> from zope.pagetemplate.pagetemplate import PageTemplate
    >>> macro_template = PageTemplate()
    >>> macro_template.write('''\
    ... <html metal:define-macro="view">
    ... <body metal:define-slot="body" />
    ... </html>
    ... ''')

We also need to provide a traversal adapter for the view namespace
that lets us look up the macros.

    >>> import zope.traversing.interfaces
    >>> class view:
    ...     zope.component.adapts(None, None)
    ...     zope.interface.implements(zope.traversing.interfaces.ITraversable)
    ...     def __init__(self, ob, r=None):
    ...         pass
    ...     def traverse(*args):
    ...         return macro_template.macros

    >>> zope.component.provideAdapter(view, name='view')

And we have to register the default traversable adapter (I wish we had
push templates):

    >>> from zope.traversing.adapters import DefaultTraversable
    >>> zope.component.provideAdapter(DefaultTraversable, [None])

We need to set up the translation framework. We'll just provide a
negotiator that always decides to use the test language:

    >>> import zope.i18n.interfaces
    >>> class Negotiator:
    ...     zope.interface.implements(zope.i18n.interfaces.INegotiator)
    ...     def getLanguage(*ignored):
    ...         return 'test'

    >>> zope.component.provideUtility(Negotiator())

And we'll set up the fallback-domain factory, which provides the test
language for all domains:

    >>> from zope.i18n.testmessagecatalog import TestMessageFallbackDomain
    >>> zope.component.provideUtility(TestMessageFallbackDomain)

OK, so let's see what the page form looks like. First, we'll compute
the page:

    >>> form.update()
    >>> page = form.page()

We want to make sure that the page has the translations we expect and
that it doesn't double translate anything.  We'll write a generator
that extracts the translations, complaining if any are nested:

    >>> def find_translations(text):
    ...     l = 0
    ...     while 1:
    ...         lopen = text.find('[[', l)
    ...         lclose = text.find(']]', l)
    ...         if lclose >= 0 and lclose < lopen:
    ...             raise ValueError(lopen, lclose, text)
    ...         if lopen < 0:
    ...             break
    ...         l = lopen + 2
    ...         lopen = text.find('[[', l)
    ...         lclose = text.find(']]', l)
    ...         if lopen >= 0 and lopen < lclose:
    ...             raise ValueError(lopen, lclose, text)
    ...         if lclose < 0:
    ...             raise ValueError(l, text)
    ...         yield text[l-2:lclose+2]
    ...         l = lclose + 2

    >>> for t in find_translations(page):
    ...     print t
    [[my.domain][The label]]
    [[my.domain][Success!]]
    [[my.domain][Name]]
    [[my.domain][Enter your name]]
    [[my.domain][Ok]]

Now, let's try the same thing with the sub-page form:

    >>> for t in find_translations(form.subpage()):
    ...     print t
    [[my.domain][The label]]
    [[my.domain][Success!]]
    [[my.domain][Name]]
    [[my.domain][Enter your name]]
    [[my.domain][Ok]]

"""


def test_setUpWidgets_prefix():
    """This is a regression test for field prefix handling in setUp*Widgets.

    Let's set up fields with some interface and a prefix on fields:

        >>> from zope.formlib import form
        >>> from zope import interface, schema

        >>> class ITrivial(interface.Interface):
        ...     name = schema.TextLine(title=u"Name")

        >>> form_fields = form.Fields(ITrivial, prefix='one')
        >>> form_fields += form.Fields(ITrivial, prefix='two')
        >>> form_fields += form.Fields(ITrivial, prefix='three')

    Let's call setUpDataWidgets and see their names:

        >>> class Trivial(object):
        ...     interface.implements(ITrivial)
        ...     name = 'foo'
        >>> context = Trivial()

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest()

        >>> widgets = form.setUpDataWidgets(form_fields, 'form', context,
        ...                                 request, {})
        >>> [w.name for w in widgets]
        ['form.one.name', 'form.two.name', 'form.three.name']

    Let's try the same with setUpEditWidgets:

        >>> widgets = form.setUpEditWidgets(form_fields, 'form', context,
        ...                                  request)
        >>> [w.name for w in widgets]
        ['form.one.name', 'form.two.name', 'form.three.name']

    And setUpInputWidgets:

        >>> widgets = form.setUpInputWidgets(form_fields, 'form', context,
        ...                                  request)
        >>> [w.name for w in widgets]
        ['form.one.name', 'form.two.name', 'form.three.name']

    And setUpWidgets:

        >>> widgets = form.setUpWidgets(form_fields, 'form', context, request)
        >>> [w.name for w in widgets]
        ['form.one.name', 'form.two.name', 'form.three.name']

    """

def test_Action_interface():
    """
    >>> action = zope.formlib.form.Action('foo')
    >>> import zope.interface.verify
    >>> zope.interface.verify.verifyObject(zope.formlib.interfaces.IAction,
    ...                                    action)
    True
    """


def test_suite():
    from zope.testing import doctest
    checker = zope.testing.renormalizing.RENormalizing([
      (re.compile(r"\[WidgetInputError\('form.summary', 'summary', ValidationError\('A error message'\)\)\]"),
                  r"[<zope.app.form.interfaces.WidgetInputError instance at ...>]"),
      (re.compile(r"\[WidgetInputError\('summary', u'Summary', None\)\]"),
                  r"[<zope.app.form.interfaces.WidgetInputError instance at ...>]"),
      (re.compile(r" ValueError\('invalid literal for float\(\): (bob'|10,0'),\)"),
                  r"\n <exceptions.ValueError instance at ...>"),
    ])
    errors = functional.FunctionalDocFileSuite("errors.txt")
    errors.layer = FormlibLayer
    bugs = functional.FunctionalDocFileSuite(
        "bugs.txt",
        optionflags=doctest.INTERPRET_FOOTNOTES | doctest.ELLIPSIS)
    bugs.layer = FormlibLayer
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'form.txt',
            setUp=formSetUp, tearDown=zope.component.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker
            ),
        doctest.DocTestSuite(
            setUp=formSetUp, tearDown=zope.component.testing.tearDown,
            checker=checker
            ),
        doctest.DocTestSuite(
            'zope.formlib.errors'),
        errors,
        bugs,
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

