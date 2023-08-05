from types import TupleType

from zope import interface
from zope import component
from zope.filerepresentation.interfaces import IFileFactory

from Products.CMFPlone import utils as ploneutils
from Products.PloneFlashUpload import interfaces
from Products.CMFCore import utils as cmfutils

from interfaces import IUploadingCapable


class UploadingCapableFileFactory(object):
    interface.implements(IFileFactory)
    component.adapts(IUploadingCapable)

    DEFAULT_TYPE = 'File'

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        ctr = cmfutils.getToolByName(self.context, 'content_type_registry')
        type_ = ctr.findTypeName(name, '', '') or self.DEFAULT_TYPE
        settings = PortalFlashUploadSettings(self.context)
        if type_ not in settings.valid_types:
            type_ = self.DEFAULT_TYPE

        plone_tool = cmfutils.getToolByName(self.context, 'plone_utils')
        newid = plone_tool.normalizeString(name)

        obj = ploneutils._createObjectByType(type_, self.context, newid)
        obj.update_data(data, content_type)
        obj.update(title=name)
        return obj


class PortalFlashUploadSettings(object):
    interface.implements(interfaces.IFlashUploadSettings)
    component.adapts(interface.Interface)

    COMPLETION_PROPERTY = 'flashupload_completion_url'
    VALID_TYPES_PROPERTY = 'flashupload_valid_types'

    def __init__(self, context):
        pt = cmfutils.getToolByName(context, 'portal_url')
        portal = pt.getPortalObject()
        self.site_props = portal.portal_properties.site_properties

    def _get_completion_url(self):
        default = interfaces.IFlashUploadSettings['completion_url'].default
        return self.site_props.getProperty(self.COMPLETION_PROPERTY, default)
    def _set_completion_url(self, v):
        if not self.site_props.hasProperty(self.COMPLETION_PROPERTY):
            self.site_props.manage_addProperty(self.COMPLETION_PROPERTY,
                                               v, 'string')
        else:
            kwargs = {self.COMPLETION_PROPERTY: v}
            self.site_props.manage_changeProperties(**kwargs)
    completion_url = property(_get_completion_url, _set_completion_url)

    def _get_valid_types(self):
        """Return the valid types as a tuple.

        Whether the property is a string or a tuple, it ought to be returned
        as a string.

        >>> class MockSomething:
        ...     _dict = {}
        ...     def getProperty(self, id, default):
        ...         return self._dict.get(id, default)
        ...     def hasProperty(self, id):
        ...         return id in self._dict.keys()
        ...     def manage_addProperty(self, id, value, type_):
        ...         self._dict[id] = tuple(value.split('\\n'))
        >>> portal = MockSomething()
        >>> class MockPortalTool:
        ...     def getPortalObject(self):
        ...         return portal
        >>> portal.portal_url = MockPortalTool()
        >>> portal.portal_properties = MockSomething()
        >>> portal.portal_properties.site_properties = MockSomething()
        >>> settings = PortalFlashUploadSettings(portal)

        When we set it, it should be stored as a string.
        >>> settings.valid_types = u"Reinout\\nvan\\nRees"
        >>> settings.valid_types
        u'Reinout\\nvan\\nRees'

        The default as passed by the interface is a string with \n,
        though. Ought to stay a string.

        >>> portal.portal_properties.site_properties._dict = {}
        >>> settings.valid_types
        u'Image\\nFile'

        """
        default = interfaces.IFlashUploadSettings['valid_types'].default
        value = self.site_props.getProperty(self.VALID_TYPES_PROPERTY,
                                            default)
        if isinstance(value, TupleType):
            value = '\n'.join(value)
        return value
    def _set_valid_types(self, v):
        #v = v.split('\n')
        if not self.site_props.hasProperty(self.VALID_TYPES_PROPERTY):
            self.site_props.manage_addProperty(self.VALID_TYPES_PROPERTY,
                                               v, 'lines')
        else:
            kwargs = {self.VALID_TYPES_PROPERTY: v}
            self.site_props.manage_changeProperties(**kwargs)
    valid_types = property(_get_valid_types, _set_valid_types)
