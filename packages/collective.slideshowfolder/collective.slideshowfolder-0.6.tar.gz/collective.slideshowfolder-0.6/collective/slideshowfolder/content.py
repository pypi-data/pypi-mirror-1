from Products.Archetypes import atapi
from Products.ATContentTypes.content import image
from Products.ATReferenceBrowserWidget import ATReferenceBrowserWidget

from collective.slideshowfolder import field

class SlideshowImage(image.ATImage):
    """Uses a reference to an existing ATImage for most field
    values."""

    meta_type = portal_type = 'SlideshowImage'
    archetype_name = 'Slideshow Image'

    schema = image.ATImage.schema.copy() + atapi.Schema(
        [field.ReferencedField(orig_field=orig_field,
                               reference_field='imageReference')
         for orig_field in image.ATImage.schema.fields()
         if orig_field.getName() != 'id'])
    schema.addField(
        atapi.ReferenceField(
            'imageReference',
            relationship = 'imageReference',
            allowed_types=('Image',),
            widget = ATReferenceBrowserWidget.ReferenceBrowserWidget(
                allow_search=True,
                allow_browse=True,
                show_indexes=False,
                force_close_on_insert=True,
                label=u'Image Reference',
                description=u'The real image',
                visible={'edit': 'visible', 'view': 'invisible'})))
    schema.moveField('imageReference', after='id')

atapi.registerType(SlideshowImage, 'collective.slideshowfolder')
