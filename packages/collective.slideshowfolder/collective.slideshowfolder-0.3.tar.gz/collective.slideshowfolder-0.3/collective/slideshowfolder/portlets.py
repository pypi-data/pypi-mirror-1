from zope import interface
from zope.cachedescriptors import property

from Products.Five.browser import pagetemplatefile

from Products.Archetypes import interfaces as at_ifaces

from plone.portlets import interfaces
from plone.app.portlets.portlets import base

class ISlideshowView(interface.Interface):
    """View for inspecting slideshow data"""

    available = interface.Attribute('Is Available')

class ISlideshowPortlet(interfaces.IPortletDataProvider):
    """A portlet displaying a slideshow"""

class SlideshowAssignment(base.Assignment):
    interface.implements(ISlideshowPortlet)

    title = u'Slideshow'

class SlideshowView(object):
    interface.implements(ISlideshowView)
    
    @property.Lazy
    def available(self):
        slideshow_view = self.slideshow_view
        if slideshow_view is not None:
            return slideshow_view.getSlideshowImages()

    @property.Lazy
    def slideshowfolder(self):
        if at_ifaces.IReferenceable.providedBy(self.context):
            refs = self.context.getRefs('slideshow')
            if refs:
                return refs[0]

    @property.Lazy
    def slideshow_view(self):
        slideshowfolder = self.slideshowfolder
        if slideshowfolder is not None:
            return slideshowfolder.restrictedTraverse(
                '@@slideshow_view')

class SlideshowRenderer(SlideshowView, base.Renderer):

    _template = pagetemplatefile.ViewPageTemplateFile(
        'slideshow-portlet.pt')

    def render(self):
        return self._template()

class SlideshowAddForm(base.NullAddForm):

    def create(self):
        return SlideshowAssignment()

class SlideshowSettings(object):

    def __call__(self):
        return self.context.restrictedTraverse(
            '@@slideshow_portlet_view/slideshowfolder/'
            'slideshow_settings.js')()
