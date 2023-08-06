from logging import getLogger
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.event import notify

from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from ZODB.POSException import ConflictError
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ATFieldProperty
from Products.Archetypes.atapi import registerType
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.MimetypesRegistry.common import MimeTypeException

from plone.app.blob.interfaces import IATBlob, IATBlobImage
from plone.app.blob.config import packageName
from plone.app.blob.field import BlobMarshaller
from plone.app.blob.mixins import ImageMixin
from plone.app.blob.markings import markAs


ATBlobSchema = ATContentTypeSchema.copy()
ATBlobSchema['title'].storage = AnnotationStorage()

finalizeATCTSchema(ATBlobSchema, folderish=False, moveDiscussion=False)
ATBlobSchema.registerLayer('marshall', BlobMarshaller())


def addATBlob(container, id, subtype='Blob', **kwargs):
    """ extended at-constructor copied from ClassGen.py """
    obj = ATBlob(id)
    if subtype is not None:
        markAs(obj, subtype)    # mark with interfaces needed for subtype
    notify(ObjectCreatedEvent(obj))
    container._setObject(id, obj)
    obj = container._getOb(id)
    obj.initializeArchetype(**kwargs)
    notify(ObjectModifiedEvent(obj))
    return obj.getId()

def addATBlobFile(container, id, **kwargs):
    return addATBlob(container, id, subtype='File', **kwargs)

def addATBlobImage(container, id, **kwargs):
    return addATBlob(container, id, subtype='Image', **kwargs)


class ATBlob(ATCTFileContent, ImageMixin):
    """ a chunk of binary data """
    implements(IATBlob)

    __implements__ = ATCTFileContent.__implements__, IATFile

    portal_type = 'Blob'
    _at_rename_after_creation = True
    schema = ATBlobSchema

    title = ATFieldProperty('title')
    summary = ATFieldProperty('description')

    security  = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline or as an attachment """
        field = self.getPrimaryField()
        if IATBlobImage.providedBy(self):
            return field.index_html(self, REQUEST, RESPONSE)
        else:
            return field.download(self, REQUEST, RESPONSE)

    # helper & explicit accessor and mutator methods

    security.declarePrivate('getBlobWrapper')
    def getBlobWrapper(self):
        """ return wrapper class containing the actual blob """
        accessor = self.getPrimaryField().getAccessor(self)
        return accessor()

    security.declareProtected(View, 'getFile')
    def getFile(self, **kwargs):
        """ archetypes.schemaextender (wisely) doesn't mess with classes,
            so we have to provide our own accessor """
        return self.getBlobWrapper()

    security.declareProtected(ModifyPortalContent, 'setFile')
    def setFile(self, value, **kwargs):
        """ set the file contents and possibly also the id """
        mutator = self.getField('file').getMutator(self)
        mutator(value, **kwargs)

    # index accessor using portal transforms to provide index data

    security.declarePrivate('getIndexValue')
    def getIndexValue(self, mimetype='text/plain'):
        """ an accessor method used for indexing the field's value
            XXX: the implementation is mostly based on archetype's
            `FileField.getIndexable` and rather naive as all data gets
            loaded into memory if a suitable transform was found.
            this should probably use `plone.transforms` in the future """
        field = self.getPrimaryField()
        source = field.getContentType(self)
        transforms = getToolByName(self, 'portal_transforms')
        if transforms._findPath(source, mimetype) is None:
            return ''
        value = str(field.get(self))
        filename = field.getFilename(self)
        try:
            return str(transforms.convertTo(mimetype, value,
                mimetype=source, filename=filename))
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            getLogger(__name__).exception('exception while trying to convert '
               'blob contents to "text/plain" for %r', self)

    # compatibility methods when used as ATFile replacement

    security.declareProtected(View, 'get_data')
    def get_data(self):
        """ return data as a string;  this is highly inefficient as it
            loads the complete blob content into memory, but the method
            is unfortunately still used here and there... """
        return str(self.getBlobWrapper())

    data = ComputedAttribute(get_data, 1)

    def __str__(self):
        """ return data as a string;  this is highly inefficient as it
            loads the complete blob content into memory, but the method
            is unfortunately still used here and there... """
        if IATBlobImage.providedBy(self):
            return self.getPrimaryField().tag(self)
        else:
            return self.get_data()

    security.declareProtected(ModifyPortalContent, 'setFilename')
    def setFilename(self, value, key=None):
        """ convenience method to set the file name on the field """
        self.getBlobWrapper().setFilename(value)

    security.declareProtected(ModifyPortalContent, 'setFormat')
    def setFormat(self, value):
        """ convenience method to set the mime-type """
        self.getBlobWrapper().setContentType(value)

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=False):
        """ calculate an icon based on mime-type """
        contenttype = self.getBlobWrapper().getContentType()
        mtr = getToolByName(self, 'mimetypes_registry', None)
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            mimetypeitem = None
        if mimetypeitem is None or mimetypeitem == ():
            return super(ATBlob, self).getIcon(relative_to_portal)
        icon = mimetypeitem[0].icon_path
        if not relative_to_portal:
            utool = getToolByName( self, 'portal_url' )
            icon = utool(relative=1) + '/' + icon
            while icon[:1] == '/':
                icon = icon[1:]
        return icon


registerType(ATBlob, packageName)

