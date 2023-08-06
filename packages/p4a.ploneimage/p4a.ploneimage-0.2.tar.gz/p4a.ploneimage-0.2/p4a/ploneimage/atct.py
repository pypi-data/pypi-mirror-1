import os
from OFS import Image as ofsimage

from zope import component
from zope import interface
from zope.app.event import objectevent

from p4a.image import imageanno
from p4a.image import interfaces
from p4a.image import utils

from p4a.fileimage import utils as fileutils

from Products.ATContentTypes import interface as atctifaces  
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

from zope.component import queryAdapter

DEFAULT_CHARSET = 'utf-8'

class ATCTFolderImageProvider(object):
    interface.implements(interfaces.IImageProvider)
    component.adapts(atctifaces.IATFolder)
    
    def __init__(self, context):
        self.context = context

    @property
    def image_items(self):
        files = []
        for x in self.context.getFolderContents(full_objects=True):
            adapted = component.queryAdapter(x, interfaces.IImage)
            if adapted is not None:
                files.append(adapted)

        return files

class ATCTBTreeFolderImageProvider(ATCTFolderImageProvider):
    interface.implements(interfaces.IImageProvider)
    component.adapts(atctifaces.IATBTreeFolder)
    
    def __init__(self, context):
        self.context = context

class ATCTTopicImageProvider(object):
    interface.implements(interfaces.IImageProvider)
    component.adapts(atctifaces.IATTopic)
    
    def __init__(self, context):
        self.context = context

    @property
    def image_items(self):
        files = []
        for x in self.context.queryCatalog(full_objects=True):
            adapted = component.queryAdapter(x, interfaces.IImage)
            if adapted is not None:
                files.append(adapted)

        return files

# XXX Need to make changes here to handle both File and Image uploads
# XXX For starters, let's just hande Image
@interface.implementer(interfaces.IImage)
#@component.adapter(atctifaces.IATFile)
@component.adapter(atctifaces.IATImage)
def ATCTImageEnhanced(context):
    if not interfaces.IImageEnhanced.providedBy(context):
        return None
    return _ATCTImageEnhanced(context)

class _ATCTImageEnhanced(imageanno.AnnotationImage):
    """An IImage adapter designed to handle ATCT based Image content.
    """
    
    interface.implements(interfaces.IImage)
    #component.adapts(atctifaces.IATFile)
    component.adapts(atctifaces.IATImage)

    ANNO_KEY = 'p4a.ploneimage.atct.ATCTImageEnhanced'

    def _load_image_metadata(self):
        """Retrieve image metadata from the raw file data and update
        this object's appropriate metadata fields.
        """
        
        mime_type = self.context.get_content_type()
        accessor = component.queryAdapter(self.context, 
                                          interfaces.IImageDataAccessor,
                                          unicode(mime_type))
        if accessor is not None:
            # aaagh, there is no getRawFile on ATImage like on ATFile...
            #filename = fileutils.write_ofsfile_to_tempfile(self.context.getRawFile())
            filename = fileutils.write_ofsfile_to_tempfile(self.context.getPrimaryField().getAccessor(self.context)( ))
            accessor.load(filename)
            os.remove(filename)

    def _save_image_metadata(self):
        """Write the image metadata fields of this object as metadata
        on the raw file data.
        """
        
        mime_type = self.context.get_content_type()
        accessor = component.queryAdapter(self.context, 
                                          interfaces.IImageDataAccessor,
                                          unicode(mime_type))
        if accessor is not None:
            #filename = fileutils.write_ofsfile_to_tempfile(self.context.getRawFile())
            filename = fileutils.write_ofsfile_to_tempfile(self.context.getPrimaryField().getAccessor(self.context)( ))
            accessor.store(filename)

            #zodb_file = self.context.getRawFile()
            zodb_file = self.context.getPrimaryField().getAccessor(self.context)( )
            fin = open(filename, 'rb')
            # very inefficient, loading whole file in memory upon upload
            # TODO: fix in-memory loading
            data, size = zodb_file._read_data(fin)
            zodb_file.update_data(data, mime_type, size)
            fin.close()
            
            os.remove(filename)

    @property
    def _default_charset(self):
        """The charset determined by the active Plone site to be the
        default.
        """
        
        charset = getattr(self, '__cached_default_charset', None)
        if charset is not None:
            return charset
        try:
            props = cmfutils.getToolByName(self.context, 'portal_properties')
            self.__cached_default_charset = props.site_properties.default_charset
        except:
            self.__cached_default_charset = DEFAULT_CHARSET
        return self.__cached_default_charset
        
    def _u(self, v):
        """Return the unicode object representing the value passed in an
        as error-immune manner as possible.
        """
        
        return utils.unicodestr(v, self._default_charset)

    def _get_file(self):
        #return self.context.getRawFile()
        return self.context.getPrimaryField().getAccessor(self.context)( )
    def _set_file(self, v):
        if v != interfaces.IImage['file'].missing_value:
            #self.context.getRawFile().manage_upload(file=v)
            self.context.getPrimaryField().getAccessor(self.context)( ).manage_upload(file=v)
    file = property(_get_file, _set_file)

    def _get_image_thumbnail(self):
        v = self.image_data.get('image_thumbnail', None)
        if v == None or v.get_size() == 0:
            return None
        return v
    def _set_image_thumbnail(self, v):
        if v == interfaces.IImage['image_thumbnail'].missing_value:
            return
        upload = v
        if isinstance(upload, ofsimage.Image):
            image = upload
        else:
            image = ofsimage.Image(id=upload.filename, 
                                   title=upload.filename, 
                                   file=upload)
        self.image_data['image_thumbnail'] = image
    image_thumbnail = property(_get_image_thumbnail, _set_image_thumbnail)

    @property
    def image_type(self):
        mime_type = self.context.get_content_type()
        accessor = component.getAdapter(self.context, 
                                        interfaces.IImageDataAccessor,
                                        unicode(mime_type))
        return accessor.image_type

    def __str__(self):
        return '<p4a.image ATCTImageEnhanced title=%s>' % self.title
    __repr__ = __str__

class _ATCTFolderishImageContainer(imageanno.AnnotationImageContainer):
    """An IImageContainer adapter designed to handle ATCT based file content.
    """

    interface.implements(interfaces.IImageContainer)
    component.adapts(atctifaces.IATFolder)

    ANNO_KEY = 'p4a.ploneimage.atct.ATCTFolderImageContainer'


    @property
    def _default_charset(self):
        """The charset determined by the active Plone site to be the
        default.
        """

        charset = getattr(self, '__cached_default_charset', None)
        if charset is not None:
            return charset
        try:
            props = cmfutils.getToolByName(self.context, 'portal_properties')
            self.__cached_default_charset = props.site_properties.default_charset
        except:
            self.__cached_default_charset = DEFAULT_CHARSET
        return self.__cached_default_charset

    def _u(self, v):
        """Return the unicode object representing the value passed in an
        as error-immune manner as possible.
        """

        return utils.unicodestr(v, self._default_charset)

    def _get_folder_image(self):
        v = self.image_data.get('folder_image', None)
        if v == None or v.get_size() == 0:
            return None
        return v
    def _set_folder_image(self, v):
        if v == interfaces.IImageContainer['folder_image'].missing_value:
            return
        upload = v
        if isinstance(upload, ofsimage.Image):
            image = upload
        else:
            image = ofsimage.Image(id=upload.filename, 
                                   title=upload.filename, 
                                   file=upload)
        self.image_data['folder_image'] = image
    folder_image = property(_get_folder_image, _set_folder_image)

    def __str__(self):
        return '<p4a.image ATCTFolderishImage title=%s>' % self.title
    __repr__ = __str__

@interface.implementer(interfaces.IImageContainer)
@component.adapter(atctifaces.IATFolder)
def ATCTFolderImageContainer(context):
    if not interfaces.IImageContainerEnhanced.providedBy(context):
        return None
    return _ATCTFolderishImageContainer(context)

@interface.implementer(interfaces.IImageContainer)
@component.adapter(atctifaces.IATTopic)
def ATCTTopicImageContainer(context):
    if not interfaces.IImageContainerEnhanced.providedBy(context):
        return None
    return _ATCTFolderishImageContainer(context)

@interface.implementer(interfaces.IImageContainer)
@component.adapter(atctifaces.IATBTreeFolder)
def ATCTBTreeFolderImageContainer(context):
    if not interfaces.IImageContainerEnhanced.providedBy(context):
        return None
    return _ATCTFolderishImageContainer(context)

def load_metadata(obj, evt):
    """An event handler for loading metadata.
    """

    obj._load_image_metadata()

def sync_image_metadata(obj, evt):
    """An event handler for saving metadata information back onto the file.
    """

    image = interfaces.IImage(obj)
    for description in evt.descriptions:
        if isinstance(description, objectevent.Attributes):
            attrs = description.attributes
            # XXX attrs is the exposed IPTC fields plus file - why?
            #     ('title', 'description', 'file', 'photographer', 'copyright', 
            #     'keywords', 'location', 'city', 'state', 'country')
            orig = {}
            for key in attrs:
                if key != 'file':
                    # XXX this sets those fields to None in orig if they are blank
                    # XXX on the edit form
                    # XXX Then in the next stanza this is set on file, which breaks things
                    # XXX This probably needs _imagedata.py store to work to fix it
                    orig[key] = getattr(image, key)
            if 'file' in attrs:
                image._load_image_metadata()
                for key, value in orig.items():
                    setattr(image, key, value)
    image._save_image_metadata()

def attempt_media_activation(obj, evt):
    """Try to activiate the media capabilities of the given object.
    """

    activator = interfaces.IMediaActivator(obj)

    if activator.media_activated:
        return

    mime_type = obj.get_content_type()
    try:
        accessor = component.getAdapter(obj, 
                                        interfaces.IImageDataAccessor,
                                        unicode(mime_type))
    except Exception, e:
        accessor = None

    if accessor is not None:
        activator.media_activated = True
        update_dublincore(obj, evt)
        update_catalog(obj, evt)

def update_dublincore(obj, evt):
    """
    Update the dublincore properties.
    """

    image = interfaces.IImage(obj)
    # image metadata may include a title - if so, use it 
    if image.title and len(image.title) > 0:
        obj.setTitle(image.title)
    # similarly for description (called "caption" in the metadata)
    if image.description and len(image.description) > 0:
        obj.setDescription(image.description)
    # similarly for keywords
    if image.keywords is not None:
        obj.setSubject(image.keywords)

def update_catalog(obj, evt):
    """Reindex the object in the catalog.
    """

    obj.reindexObject()
    
def SearchableText(obj, portal, **kwargs):
    """ 
    Used by the catalog for basic full text indexing 
    XXX This needs more fields indexed (like location)
    """

    adapter = queryAdapter(obj, interfaces.IImage)

    if adapter:

        photographer = adapter.photographer
        keywords = adapter.keywords
        location = adapter.location
        city = adapter.city
        state = adapter.state
        country = adapter.country

        if photographer == None:
            # XXX workaround for a problem in sync_image_metadata above
            # XXX that may be due to not having a working store method...
            photographer = ''

        if keywords == None:
            keywords = []
        keywords = ' '.join(keywords)

        if location == None:
            location = ''
        
        if city == None:
            city = ''
        
        if state == None:
            state = ''
        
        if country == None:
            country = ''
        
        return_list = [obj.SearchableText(),
                       photographer,
                       keywords,
                       location,
                       city,
                       state,
                       country
                       ]
        return ' '.join(return_list)
    else:
        return obj.SearchableText()
    
registerIndexableAttribute('SearchableText', SearchableText)

    
