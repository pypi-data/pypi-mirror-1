from zope import interface
from zope.cachedescriptors import property

from Products.Archetypes import interfaces as at_ifaces

from Products.slideshowfolder import interfaces
from Products.slideshowfolder import browser as base_browser
from collective.slideshowfolder import browser

class ISlideShowPortletView(interfaces.ISlideShowView):
    """View for inspecting slideshow data"""

    available = interface.Attribute('Is Available')

class SlideShowPortletView(browser.SlideShowFolderView):
    interface.implements(ISlideShowPortletView)
    
    def __init__(self, context, request):
        self.portlet_context = context
        context = self.slideshowfolder
        super(base_browser.SlideShowFolderView, self).__init__(
            context, request)

    @property.Lazy
    def available(self):
        if self.context is not None:
            return self.getSlideshowImages()

    @property.Lazy
    def slideshowfolder(self):
        if at_ifaces.IReferenceable.providedBy(self.portlet_context):
            refs = self.portlet_context.getRefs('slideshow')
            if refs:
                return refs[0]
