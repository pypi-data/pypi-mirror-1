from zope.interface import implements
from plone.memoize.view import memoize, memoize_contextless

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from interfaces import IPTGUtility

class PTGUtility(BrowserView):
    """Information about the state of the portal
    """
    implements(IPTGUtility)

    @memoize
    def should_include(self, display_type):
        context = aq_inner(self.context)
        return context.portal_type == 'Gallery' and context.getDisplayType() == display_type