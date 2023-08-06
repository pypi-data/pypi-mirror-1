# removed 2008-04-25: this code was written for z3, not z2, and doesn't
# work right in z2. We'll try to provide adapters in a future release,
# but we're not doing it now. XXX TODO: Provide zope2 stock content type 
# adapters

#import rfc822, pytz, time
#from vice.zope2.outbound.utils import DT2dt, dt2DT
#from datetime import datetime
#from zope.annotation import factory
#from zope.interface import implements
#from zope.component import adapts, getMultiAdapter
#from zope.dublincore.interfaces import IZopeDublinCore
#from zope.annotation.interfaces import IAnnotations
#from zope.app.folder.interfaces import IFolder
#from zope.app.file.interfaces import IFile
#from zope.traversing.browser.interfaces import IAbsoluteURL
#from zope.traversing.browser.absoluteurl import absoluteURL
#from zope.filerepresentation.interfaces import IReadFile
#from uuid import uuid1
#from collective.uuid import UUIDs
#from vice.outbound.interfaces import IFeed, IFeedItem, \
#    IFeedConfigs, \
#    IFeedConfig, IItemUUID, IItemUUIDs, IItemUUIDable, IFeedUUID, \
#    IFeedUUIDable
#
#class FolderFeed(object):
#    """Adapter from IFolder to IFeed.
#
#    Make sure that FolderFeed implements the IFeed
#    interface
#    >>> from zope.interface.verify import verifyClass
#    >>> verifyClass(IFeed, FolderFeed)
#    True
#    """
#    implements(IFeed)
#    adapts(IFolder, IAbsoluteURL)
#
#    __name__ = __parent__ = None
#
#    def __init__(self, context, absolute_url):
#        self.context = context
#        self.absolute_url = absolute_url
#
#    def __iter__(self):
#        """Iterator for all syndicated items in this feed.
#        """
#        for item in self.context.objectValues():
#            yield getMultiAdapter((item, self), IFeedItem)
#
#    @property
#    def description(self):
#        """See IFeed.
#        """
#        return IZopeDublinCore(self.context).description
#
#    @property
#    def modified(self):
#        """See IFeed.
#        """
#        mod =  IZopeDublinCore(self.context).modified
#        if mod == None:
#            mod = IZopeDublinCore(self.context).created
#        return mod
#
#    @property
#    def modifiedString(self):
#        return RFC3339(self.modified)
#
#    @property
#    def name(self):
#        """See IFeed.
#        """
#        return self.context.__name__
#
#    @property
#    def title(self):
#        """See IFeed.
#        """
#        return IZopeDublinCore(self.context).Title
#
#    @property
#    def UID(self):
#        """See IFeed.
#        """
#        u = IFeedUUID(self)
#        return u.UUID
#
#    @property
#    def syndication(self):
#        s = IFeedConfigs(self.context)
#        # XXX TODO: use ID, not URL
#        return s.findConfigByID(self.absolute_url())
#
#class FileFeedItem(object):
#    """Adapts IFile to IFeedItem
#
#    Make sure that FileFeedItem implements the IFeedItem
#    interface
#    >>> from zope.interface.verify import verifyClass
#    >>> verifyClass(IFeedItem, FileFeedItem)
#    True
#    """
#
#    implements(IFeedItem)
#    adapts(IFile, IFeed)
#
#    def __init__(self, context, feed):
#        self.context = context
#        self.feed = feed
#
#    @property
#    def title(self):
#        """See IFeedItem
#        """
#        return IZopeDublinCore(self.context).title
#
#    @property
#    def description(self):
#        """See IFeedItem
#        """
#        return IZopeDublinCore(self.context).description
#
#    @property
#    def body(self):
#        """See IFeedItem
#        """
#        # XXX TODO
#        return unicode(IReadFile(self.context).read())
#
#    @property
#    def XHTML(self):
#        """See IFeedItem
#        """
#        # XXX TODO
#        return ""
#
#    @property
#    def UID(self):
#        """See IFeedItem
#        """
#        u = getMultiAdapter((self.feed, self), IItemUUID)
#        return u.UUID
# 
#    @property
#    def author(self):
#        """See IFeedItem
#        """
#        return IZopeDublinCore(self.context).creators
#
#    @property
#    def effective(self):
#        """See IFeedItem
#        """
#        return IZopeDublinCore(self.context).created
#
#    @property
#    def effectiveString(self):
#        return RFC3339(self.effective)
#
#    @property
#    def modified(self):
#        """See IFeedItem
#        """
#        mod =  IZopeDublinCore(self.context).modified
#        if mod == None:
#            mod = IZopeDublinCore(self.context).created
#        return mod
#
#    @property
#    def modifiedString(self):
#        return RFC3339(self.modified)
#
#    @property
#    def tags(self):
#        """See IFeedItem
#        """
#        # XXX TODO
#
#    @property
#    def rights(self):
#        """See IFeedItem
#        """
#        return IZopeDublinCore(self.context).rights
#
#    @property
#    def enclosure(self):
#        """See IFeedItem
#        """
#        # XXX TODO
#        return None
#
#