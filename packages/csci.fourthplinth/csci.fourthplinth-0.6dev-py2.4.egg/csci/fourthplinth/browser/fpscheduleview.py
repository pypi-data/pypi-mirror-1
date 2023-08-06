from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from csci.fourthplinth import fourthplinthMessageFactory as _


class IFPscheduleView(Interface):
    """
    FPschedule view interface
    """

    def test():
        """ test method"""


class FPscheduleView(BrowserView):
    """
    FPschedule browser view
    """
    implements(IFPscheduleView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        if not hasattr(self.context, 'schedule_html'):
            self.context.schedule_html = ''
        
        
    def get_html(self):
        if not hasattr(self.context, 'schedule_html'):
            self.context.schedule_html = 'Awaiting update!'
            
        return self.context.schedule_html
        
        

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
