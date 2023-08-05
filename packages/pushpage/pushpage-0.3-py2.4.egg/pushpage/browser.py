""" Class:  PushPage

$Id: browser.py,v 1.7 2006/10/05 20:04:27 tseaver Exp $
"""

from zope.event import notify
from zope.interface import implements
from zope.pagetemplate.pagetemplate import PageTemplate
from zope.publisher.interfaces.browser import IBrowserPublisher

from pushpage.events import PushPageNamespaceInit
from pushpage.events import PushPageRendered

class PushPageTemplate(PageTemplate):

    def pt_getContext(self, args=(), options={}, **ignored):
        return options

class PushPage:
    implements(IBrowserPublisher)

    def __init__(self, context, request, template, mapper):
        self.context = context
        self.request = request
        self.template = template
        self.mapper = mapper

    def browserDefault(self, request):
        return self, ()

    def publishTraverse(self, request, name):
        if name == 'index.html':
            return self.index

        raise NotFound(self, name, request)

    def __call__(self):
        namespace = self.mapper(self.context, self.request)
        notify(PushPageNamespaceInit(self, namespace))
        rendered = self.template(**namespace)
        notify(PushPageRendered(self, rendered))
        return rendered

class PushPageFactory:

    page_class = PushPage

    def __init__(self, template, mapper, checker=None):
        if getattr(template, 'read', None) is not None:
            template = template.read()
        self.template = PushPageTemplate()
        self.template.write(template)
        self.mapper = mapper
        self.checker = checker

    def __call__(self, context, request):
        page = self.page_class(context, request, self.template, self.mapper)
        if self.checker is not None:
            page.__Security_checker__ = self.checker
        return page
