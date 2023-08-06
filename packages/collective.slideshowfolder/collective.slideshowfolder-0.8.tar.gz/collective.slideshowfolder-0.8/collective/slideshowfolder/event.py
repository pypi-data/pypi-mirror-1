from zope import component
from zope.lifecycleevent import interfaces as lifecycle_ifaces

from Products.ATContentTypes import interface as atct_ifaces

@component.adapter(atct_ifaces.IATImage,
                   lifecycle_ifaces.IObjectModifiedEvent)
def reindexReferencer(ob, event):
    """Reindex SlideshowImages when their referenced ATImage
    changes"""
    brefs = ob.getBRefs(relationship='imageReference')
    if brefs:
        assert len(brefs) == 1, "More than one imageReference"
        brefs[0].reindexObject()
