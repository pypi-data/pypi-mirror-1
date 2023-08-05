pushpage Overview
=================

CVS: $Id: README.txt,v 1.7 2006/10/05 20:04:27 tseaver Exp $

"Push"-mode is jargon used in a number of templating systems to describe
templates which have their data "pushed" to them as a mapping, supplied by
the application.

Zope Page Templates don't qualify, as they frequently traverse the top-level
names (e.g., 'context', 'view', etc.) to "pull" data into the template.

Adopting this model has a couple of advantages, particularly for Zope
applications:

- The template code stays simpler, and therefore easier to maintain.

- The view code which does the work has an easily testable API.

- All the "heavy lifting" must be done by "trusted" code, and therefore
  without doing security checks.

- Assuming that the values in the mapping are primitive types, the
  actual work of rendering the template can be done *after* closing
  the database connection, and could therefore be done "lazily" (e.g.,
  by an IStreamITerator).


Using pushpage
==============

A push page is a view which combines a ZPT template and a callable returning
a mapping::

  >>> from pushpage.browser import PushPageFactory
  >>> TEMPLATE = """\
  ... <tal:block tal:repeat="row rows">
  ... <tal:span tal:replace="row/title">TITLE</tal:span>
  ... </tal:block>"""
  >>> def getRows(context, request):
  ...     return {'rows': [{'title': 'First Title'},
  ...                      {'title': 'Second Title'},
  ...                      {'title': 'Third Title'},
  ...                     ]}
  >>> factory = PushPageFactory(TEMPLATE, getRows)
  >>> page = factory(None, None)
  >>> print page()
  <BLANKLINE>
  First Title
  <BLANKLINE>
  Second Title
  <BLANKLINE>
  Third Title
  <BLANKLINE>

Push pages can also be made from file-like objects::

  >>> from StringIO import StringIO
  >>> filelike = StringIO(TEMPLATE)
  >>> page = PushPageFactory(filelike, getRows)(None, None)
  >>> print page()
  <BLANKLINE>
  First Title
  <BLANKLINE>
  Second Title
  <BLANKLINE>
  Third Title
  <BLANKLINE>

Push pages do *not* have access to the "standard" top-level names used
in most ZPT::

  >>> factory = PushPageFactory('<tal:x tal:replace="context/title" />',
  ...                           lambda context, request: {})
  >>> page = factory(None, None)
  >>> page()
  Traceback (most recent call last):
  ...
  KeyError: 'context'
  >>> factory = PushPageFactory('<tal:x tal:replace="template/title" />',
  ...                           lambda context, request: {})
  >>> page = factory(None, None)
  >>> page()
  Traceback (most recent call last):
  ...
  KeyError: 'template'
  >>> factory = PushPageFactory('<tal:x tal:replace="view/title" />',
  ...                           lambda context, request: {})
  >>> page = factory(None, None)
  >>> page()
  Traceback (most recent call last):
  ...
  KeyError: 'view'

We can pass along a security checker when instantiating a factory, which
will then be annotated onto the pages it produces under the special
'__Security_checker__' name (used by the security proxy machinery)::

  >>> checker = object()
  >>> factory = PushPageFactory('<tal:x tal:replace="context/title" />',
  ...                           lambda context, request: {}, checker=checker)
  >>> page = factory(None, None)
  >>> page.__Security_checker__ is checker
  True


Event Publication
=================

Pushpages publish events at two key points during the rendering process:
after retrieving the namespace from the callables, and after rendering the
template::

  >>> from zope.event import subscribers
  >>> events = []
  >>> subscribers.append(events.append)
  >>> page = PushPageFactory(TEMPLATE, getRows)(None, None)
  >>> result = page()
  >>> len(events)
  2
  >>> from pushpage.interfaces import IPushPageNamespaceInit
  >>> IPushPageNamespaceInit.providedBy(events[0])
  True
  >>> events[0].page is page
  True
  >>> events[0].namespace.keys()
  ['rows']
  >>> from pushpage.interfaces import IPushPageRendered
  >>> IPushPageRendered.providedBy(events[1])
  True
  >>> events[1].page is page
  True
  >>> print events[1].rendered
  <BLANKLINE>
  First Title
  <BLANKLINE>
  Second Title
  <BLANKLINE>
  Third Title
  <BLANKLINE>

Now clean up:

  >>> subscribers.remove(events.append)
