from p4a.image import interfaces
from p4a.ploneimage import content
from p4a.common import site

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName, SimpleRecord 

from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from zope.component.exceptions import ComponentLookupError
from p4a.image.interfaces import IImage

def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)
    setup_indexes(portal)
    setup_metadata(portal)
    addSmartFolderIndexAndMetadata(portal)
    
    qi = getToolByName(portal, 'portal_quickinstaller')
    qi.installProducts(['CMFonFive'])


def image_photographer(object, portal, **kwargs):
    """
    Return the name of the photographer in the image file for use in searching the catalog.
    """
    try:
        imagefile = IImage(object)
        return imagefile.photographer
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('image_photographer', image_photographer)

# XXX don't know about genre stuff
#def image_genre_id(object, portal, **kwargs):
#    """Return the genre id of the image file for use in searching the catalog."""
#    try:
#        imagefile = IImage(object)
#        return imagefile.genre
#    except (ComponentLookupError, TypeError, ValueError):
#        # The catalog expects AttributeErrors when a value can't be found
#        raise AttributeError

#registerIndexableAttribute('image_genre_id', image_genre_id)

def setup_site(site):
    """Install all necessary components and configuration into the
    given site.

      >>> from p4a.image import interfaces
      >>> from p4a.common.testing import MockSite

      >>> site = MockSite()
      >>> site.queryUtility(interfaces.IImageSupport) is None
      True

      >>> setup_site(site)
      >>> site.getUtility(interfaces.IImageSupport)
      <ImageSupport ...>

    """
    
    sm = site.getSiteManager()
    if not sm.queryUtility(interfaces.IImageSupport):
        sm.registerUtility(
            provided=interfaces.IImageSupport,
            component=content.ImageSupport('image_support'))

def setup_indexes(portal):
    """Install specific indexes for the image metadata fields
    so they are searchable."""
    
    out = StringIO()
    pc = getToolByName(portal, 'portal_catalog')

    # XXX don't know about genre
    #if not 'image_genre_id' in pc.indexes():
    #    pc.addIndex('image_genre_id', 'FieldIndex')
    #    pc.manage_reindexIndex('image_genre_id')
    #    print >>out, 'The FieldIndex "image_genre_id" was successfully created'

    if not 'image_photographer' in pc.indexes():

        extra = SimpleRecord(lexicon_id='plaintext_lexicon',
                             index_type='Okapi BM25 Rank')
        
        pc.addIndex('image_photographer', 'ZCTextIndex', extra)
        pc.manage_reindexIndex('image_photographer')
        print >>out, 'The ZCTextIndex "image_photographer" was successfully created'

    if not 'Format' in pc.indexes():
        pc.addIndex('Format', 'FieldIndex')
        pc.manage_reindexIndex('Format')
        print >>out, 'The FieldIndex "Format" was successfully created'
    
def setup_metadata(portal):
    """Adds the specified columns to the catalog specified,
       which must inherit from CMFPlone.CatalogTool.CatalogTool, or otherwise
       use the Plone ExtensibleIndexableObjectWrapper."""
       
    out = StringIO()
    pc = getToolByName(portal, 'portal_catalog', None)

    try:
        pc.delColumn('image_photographer')
    except:
        pass
        
    pc.manage_addColumn('image_photographer')
    # XXX this can be way too surprising for large sites
    # pc.refreshCatalog()
        
    print >>out, 'The metadata "image_photographer" was successfully added.'

            
index_mapping = {'image_photographer':
                    {'name': 'Photographer Name',
                     'description': 'The name of the photographer.',
                     'enabled': True,
                     'criteria': ('ATSimpleStringCriterion',)},
                 'Format':
                    {'name': 'MIME Types',
                     'description': 'The MIME type of the file. '
                                 'For a JPG file, this is image/jpeg and for a TIFF, image/tiff.',
                     'enabled': True,
                     'criteria': ('ATSimpleStringCriterion',)},
                 }
# XXX don't know about genre
#                 'image_genre_id':
#                    {'name': 'Genre',
#                     'description': 'The genre id of the song.'
#                                    'this is a number 0-147. '
#                                    'See genre.py for the genre names.',
#                     'enabled': True,
#                     'criteria': ('ATSimpleIntCriterion',)},

# XXX add 'image_genre_id' to list of indexes if you want this 
def addSmartFolderIndexAndMetadata(portal,
                                   indexes=('image_photographer',
                                            'Format')):
    """Adds the default indexes to be available from smartfolders"""
    atct_config = getToolByName(portal, 'portal_atct', None)
    if atct_config is not None:
        for index in indexes:
            index_info=index_mapping[index]
            atct_config.updateIndex(index, friendlyName=index_info['name'],
                                 description=index_info['description'],
                                 enabled=index_info['enabled'],
                                 criteria=index_info['criteria'])
            atct_config.updateMetadata(index, friendlyName=index_info['name'],
                                 description=index_info['description'],
                                 enabled=True)
                                     
def _cleanup_utilities(site):
    raise NotImplementedError('Current ISiteManager support does not '
                              'include ability to clean up')

def importVarious(context):
    """GenericSetup handler"""

    if context.readDataFile('p4a.ploneimage_various.txt') is None:
        return

    return setup_portal(context.getSite())
