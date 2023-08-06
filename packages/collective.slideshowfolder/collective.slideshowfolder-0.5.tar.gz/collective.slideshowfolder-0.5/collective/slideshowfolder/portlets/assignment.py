from zope import interface
from zope import schema
from zope.schema import interfaces as schema_ifaces
from zope.schema import fieldproperty
from zope.formlib import form

from plone.portlets import interfaces as portlets_ifaces
from plone.app.portlets.portlets import base

from Products.slideshowfolder import interfaces

class IAssignment(portlets_ifaces.IPortletDataProvider,
                                  interfaces.ISlideShowSettings):
    """A portlet displaying a slideshow"""
    
    showWidth = schema.Int(
        title=u'Slideshow Width',
        description=(
            u'Width of the slideshow in pixels.  Images '
            u'will be shrunk to fit within the dimensions '
            u'of the slideshow.'),
        default=120,
        )

    showHeight = schema.Int(
        title=u'Slideshow Height',
        description=(
            u'Height of the slideshow in pixels.  Images '
            u'will be shrunk to fit within the dimensions '
            u'of the slideshow.'),
        default=90,
        )

class Assignment(base.Assignment):
    interface.implements(IAssignment)

    title = u'Slideshow'

    showWidth = fieldproperty.FieldProperty(IAssignment['showWidth'])
    showHeight = fieldproperty.FieldProperty(
        IAssignment['showHeight'])
    slideDuration = fieldproperty.FieldProperty(
        IAssignment['slideDuration'])
    transitionTime = fieldproperty.FieldProperty(
        IAssignment['transitionTime'])
    thumbnails = fieldproperty.FieldProperty(
        IAssignment['thumbnails'])
    fast = fieldproperty.FieldProperty(IAssignment['fast'])
    captions = fieldproperty.FieldProperty(IAssignment['captions'])
    arrows = fieldproperty.FieldProperty(IAssignment['arrows'])
    random = fieldproperty.FieldProperty(IAssignment['random'])
    loop = fieldproperty.FieldProperty(IAssignment['loop'])
    linked = fieldproperty.FieldProperty(IAssignment['linked'])

    def __init__(self, **kw):
        for name, value in kw.iteritems():
            if not (
                name in interfaces.ISlideShowSettings[name] and
                schema_ifaces.IField.providedBy(
                    interfaces.ISlideShowSettings[name])):
                raise TypeError(
                    'Field %s not in ISlideShowSettings' % name)
            setattr(self, name, value)

class AddForm(base.AddForm):
    form_fields = form.Fields(interfaces.ISlideShowSettings)
    label = u'Add Slideshow Portlet'
    description = u'This portlet displays a slideshow.'

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(interfaces.ISlideShowSettings)
    label = u'Edit Slideshow Portlet'
    description = u'This portlet displays a slideshow.'
