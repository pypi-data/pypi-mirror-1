""" PushPage events

$Id: events.py,v 1.1 2006/10/05 20:04:27 tseaver Exp $
"""
from zope.interface import implements

from pushpage.interfaces import IPushPageEvent
from pushpage.interfaces import IPushPageNamespaceInit
from pushpage.interfaces import IPushPageRendered

class PushPageNamespaceInit(object):
    implements(IPushPageNamespaceInit)
    
    def __init__(self, page, namespace):
        self.page = page
        self.namespace = namespace

class PushPageRendered(object):
    implements(IPushPageRendered)
    
    def __init__(self, page, rendered):
        self.page = page
        self.rendered = rendered
