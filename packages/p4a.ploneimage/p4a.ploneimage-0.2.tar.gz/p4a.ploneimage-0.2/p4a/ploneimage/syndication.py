from zope import component
from zope import interface
from zope.schema import vocabulary 
from p4a.image import interfaces
from Products.CMFCore import utils as cmfutils
from Products.fatsyndication import adapters as fatadapters
from Products.basesyndication import interfaces as baseinterfaces

# XXX don't know about genre
#from p4a.image import genre

# XXX It would be cool to have a feed that included thumbnails in a feed
# XXX - will have to rewrite - does flickr do something like this? 
class ImageContainerFeed(fatadapters.BaseFeed):
    interface.implements(baseinterfaces.IFeed)
    component.adapts(interfaces.IImageContainerEnhanced)

class ImageContainerFeedSource(fatadapters.BaseFeedSource):
    interface.implements(baseinterfaces.IFeedSource)
    component.adapts(interfaces.IImageContainerEnhanced)

    def getFeedEntries(self):
        """See IFeedSoure
        """
        image_items = interfaces.IImageProvider(self.context).image_items
        return [baseinterfaces.IFeedEntry(x.context) 
                for x in image_items]

class ImageFeed(fatadapters.BaseFeed):
    interface.implements(baseinterfaces.IFeed)
    component.adapts(interfaces.IImageEnhanced)

class ImageFeedSource(fatadapters.BaseFeedSource):
    interface.implements(baseinterfaces.IFeedSource)
    component.adapts(interfaces.IImageEnhanced)

    def getFeedEntries(self):
        """See IFeedSoure
        """
        return [baseinterfaces.IFeedEntry(self.context)]

class ImageFeedEntry(fatadapters.BaseFeedEntry):
    interface.implements(baseinterfaces.IFeedEntry)
    component.adapts(interfaces.IImageEnhanced)
    
    def __init__(self, *args, **kwargs):
        fatadapters.BaseFeedEntry.__init__(self, *args, **kwargs)
        
        self.image = interfaces.IImage(self.context)
    
    def getBody(self):
        """See IFeedEntry.
        """
        return ''
    
    def getEnclosure(self):
        return baseinterfaces.IEnclosure(self.context)
    
    def getTitle(self):
        return self.image.title
    
    def getPhotographer(self):
        """
        """
        return self.image.photographer
    
    def getDescription(self):
        """
        """
        return self.image.description
    
    def getCategory(self):
        """
        """
        # XXX don't know about genre...
        #g = self.image.genre
        #if g in genre.GENRE_VOCABULARY:
        #    return genre.GENRE_VOCABULARY.getTerm(g).title
        return u''
    
    
class ATFileEnclosure(object):
    interface.implements(baseinterfaces.IEnclosure)
    component.adapts(interfaces.IImageEnhanced)
    
    def __init__(self, context):
        self.context = context
    
    def getURL(self):
        return self.context.absolute_url()

    def _getFile(self):
        from Products.ATContentTypes.interface.image import IATImage
        from Products.ATContentTypes.interface.file import IATFile
        if IATImage.providedBy(self.context):
            return self.context.getImage()
        elif IATFile.providedBy(self.context):
            return self.context.getFile()
        else:
            # XXX this will fail on later point   
            return None

    def getLength(self):
       return self._getFile().get_size()

    def __len__(self):
        return self.getLength()

    def getMajorType(self):
        return self._getFile().getContentType().split('/')[0]

    def getMinorType(self):
        return self._getFile().getContentType().split('/')[1]

    def getType(self):
        return self._getFile().getContentType()
