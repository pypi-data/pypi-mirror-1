from zope.cachedescriptors import property

from Products.Five.browser import pagetemplatefile

from plone.app.portlets.portlets import base

from collective.slideshowfolder.portlets import browser

class Renderer(base.Renderer, browser.SlideShowPortletView):

    _template = pagetemplatefile.ViewPageTemplateFile('slideshow.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(
            self, context, request, view, manager, data)
        browser.SlideShowPortletView.__init__(self, context, request)
        self.settings = data

    def render(self):
        return self._template()

    available = browser.SlideShowPortletView.available

    @property.Lazy
    def image_data(self):
        return '{ ' + ','.join([
            "'%s': { caption: '%s' }" % (
                image['name'], image['caption']) for image in
            self.getSlideshowImages()]) + ' }'

    @property.Lazy
    def options(self):
        return ', '.join([
            '%s: %s' % item for item in
            self.getSlideshowSettings().iteritems()])

    @property.Lazy
    def script(self):
        return (
            "registerPloneFunction( function() { "
            "var data = %s; "
            "new Slideshow('myShow', data, "
            "{hu: '', classes: ['slideshowfolder'], loader: "
            " {'animate': ['loader-#.png', 12]}, "
            "%s }); });") % (self.image_data, self.options)
    
