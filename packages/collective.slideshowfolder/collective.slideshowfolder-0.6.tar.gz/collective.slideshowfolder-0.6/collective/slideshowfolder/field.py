import AccessControl

from Products.CMFCore import permissions

from Products.Archetypes import atapi
from Products.Archetypes import Registry

class ReferencedField(atapi.ComputedField):
    """A field which retrieves its value from a referenced object."""
    __implements__ = atapi.Field.__implements__

    _properties_override = {
        'type' : 'referenced',
        'reference_field': None,
        'orig_field': None,
        'mode' : 'r',
        'storage': atapi.ReadOnlyStorage(),
        }
    _properties = atapi.Field._properties.copy()
    _properties.update(_properties_override)

    security = AccessControl.ClassSecurityInfo()

    def __init__(self, name=None, orig_field=None, **kwargs):
        """Copy the properties from the original field that aren't
        updated by the kwargs."""

        assert orig_field is not None, (
            "Must pass in the field to pulled from the referenced "
            "object.")

        if name is None:
            name = orig_field.getName()

        kw = orig_field.__dict__.copy()
        kw.update(self._properties_override)
        kw.update(orig_field=orig_field, **kwargs)

        super(ReferencedField, self).__init__(name=name, **kw)

    def _getReferenced(self, instance):
        reference_field = instance.getField(self.reference_field)
        assert not reference_field.multiValued, (
            "The reference_field cannot be multiValued")
        return reference_field.getAccessor(instance)()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        """Return the referenced value."""
        referenced = self._getReferenced(instance)
        if referenced is not None:
            return referenced.getField(self.getName()).get(
                referenced, **kwargs)
        else:
            return self.orig_field.getDefault(instance)

    security.declarePrivate('get')
    def getRaw(self, instance, **kwargs):
        """Return the referenced value."""
        referenced = self._getReferenced(instance)
        if referenced is not None:
            return referenced.getField(self.getName()).getRaw(
                referenced, **kwargs)

    security.declareProtected(permissions.View, 'tag')
    def tag(self, instance, *args, **kwargs):
        referenced = self._getReferenced(instance)
        if referenced is not None:
            return referenced.getField(self.getName()).tag(
                referenced, **kwargs)
        else:
            return self.orig_field.tag(instance, *args, **kwargs)

    security.declarePrivate('getFilename')
    def getFilename(self, instance, *args, **kwargs):
        referenced = self._getReferenced(instance)
        if referenced is not None:
            return referenced.getField(self.getName()).getFilename(
                referenced, **kwargs)
        else:
            return self.orig_field.getFilename(
                instance, *args, **kwargs)

    security.declareProtected(permissions.View, 'getAvailableSizes')
    def getAvailableSizes(self, instance, *args, **kwargs):
        referenced = self._getReferenced(instance)
        if referenced is not None:
            return referenced.getField(
                self.getName()).getAvailableSizes(
                referenced, **kwargs)
        else:
            return self.orig_field.getAvailableSizes(
                instance, *args, **kwargs)

    security.declareProtected(permissions.View, 'getScale')
    def getScale(self, instance, **kwargs):
        referenced = self._getReferenced(instance)
        if referenced is not None:
            return referenced.getField(
                self.getName()).getScale(
                referenced, **kwargs)
        else:
            return self.orig_field.getScale(
                instance, *args, **kwargs)

Registry.registerField(ReferencedField,
                       title='Referenced',
                       description=ReferencedField.__doc__)
