""" PushPage events

$Id: interfaces.py,v 1.1 2006/10/05 20:04:27 tseaver Exp $
"""
from zope.interface import Interface
from zope.interface import Attribute

class IPushPageEvent(Interface):
    """ Base for events related to publishing pushpage objects.
    """
    page = Attribute(u"""Pushpage

        The page about whom the event is published.""")

class IPushPageNamespaceInit(IPushPageEvent):
    """ Event published after extracting the namespace from the callable.
    """
    namespace = Attribute(u"""Namespace

        A dict containing names returned from the callable.  Subscribers
        may mutate at will.""")

class IPushPageRendered(IPushPageEvent):
    """ Event published after rendering a pushpage.
    """
    rendered = Attribute(u"""Rendered Text

        The text rendered by the pushpage.""")
