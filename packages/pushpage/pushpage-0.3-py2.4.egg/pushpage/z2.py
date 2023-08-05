""" Zope2 support

$Id: z2.py,v 1.1 2006/09/22 19:28:54 tseaver Exp $
"""
from AccessControl.SecurityInfo import ClassSecurityInfo
from Acquisition import Implicit
from Globals import InitializeClass

from pushpage.browser import PushPage
from pushpage.browser import PushPageFactory

class Z2PushPage(Implicit, PushPage):
    """ Zope2 wrapper.
    """
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    index_html = None # use our __call__

InitializeClass(Z2PushPage)

class Z2PushPageFactory(PushPageFactory):
    page_class = Z2PushPage
