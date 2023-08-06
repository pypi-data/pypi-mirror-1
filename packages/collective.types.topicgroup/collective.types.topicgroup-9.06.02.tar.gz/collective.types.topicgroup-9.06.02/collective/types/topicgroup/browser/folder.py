from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile \
     import ViewPageTemplateFile
from plone.memoize.instance import memoize
from util import extractInnerView as getView

#Patch for a bug that causes these views not to work
from Products.Five.browser.pagetemplatefile import \
     ZopeTwoPageTemplateFile
        
def _getContext(self):
    while 1:
        self = self.aq_parent
        if not getattr(self, '_is_wrapperish', None):
            return self

class DetailView(BrowserView):
    """View mode for a Topic Group 
    """
    __call__ = ViewPageTemplateFile('folder_detail.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

        #Monkey patch for the strange error shown here
        #https://bugs.launchpad.net/zope2/+bug/176566
        ZopeTwoPageTemplateFile._getContext = _getContext

    def displayLayout(self, item_object):
        return getView(item_object)

    @memoize
    def if_then_else(self, test, iftrue, iffalse):
        """Return iftrue if 'test' evaluates to true, otherwise return iffalse
        """
        if test:
            return iftrue
        return iffalse
