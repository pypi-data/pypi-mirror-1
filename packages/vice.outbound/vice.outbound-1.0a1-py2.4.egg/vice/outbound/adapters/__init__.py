from zope.annotation import factory
from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from zope.dublincore.interfaces import IZopeDublinCore
from zope.annotation.interfaces import IAnnotations
from uuid import uuid1
from collective.uuid import UUIDs
from vice.outbound.interfaces import IFeed, IFeedItem, \
    IFeedConfigs, \
    IFeedConfig, IItemUUID, IItemUUIDs, IItemUUIDable, IFeedUUID, \
    IFeedUUIDable

class FeedUUIDs(object):
    """Adapter from IFeedConfig to IFeedUUID. 

    Used to annotate a feed with a feed uuid field.
    
    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.interfaces import IFeedUUID
    >>> from vice.outbound.adapters import FeedUUIDs
    >>> verifyClass(IFeedUUID, FeedUUIDs)
    True
    
    """

    implements(IFeedUUID)
    adapts(IFeedUUIDable)

    UUID = str(uuid1())

feed_uuids_adapter = factory(FeedUUIDs)

class ItemUUIDs(UUIDs):
    """Adapter from IFeedConfig to IUUIDs. 

    Used to annotate a feed with a uuid utility.

    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.interfaces import IItemUUIDs
    >>> from vice.outbound.adapters import ItemUUIDs
    >>> verifyClass(IItemUUIDs, ItemUUIDs)
    True
    
    """

    implements(IItemUUIDs)
    adapts(IItemUUIDable)


item_uuids_adapter = factory(ItemUUIDs)

class ItemUUID(object):
    """Multiadapter from IFeed and IFeedItem to IItemUUID.

    Used to get the UUIDs for feed entries within a particular feed.
    
    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.interfaces import IItemUUID
    >>> from vice.outbound.adapters import ItemUUID
    >>> verifyClass(IItemUUID, ItemUUID)
    True
       
    """

    implements(IItemUUID)
    adapts(IFeed, IFeedItem)

    def __init__(self, feed, item):
        self.feed = feed
        self.item = item

    @property
    def UUID(self):
        u = IItemUUIDs(self.feed.config)
        uuid = u.queryId(self.item.context, None)
        if uuid is None:
            uuid = u.register(self.item.context)
        return str(uuid)

class FeedUUID(object):
    """Adapter from IFeed to IFeedUUID.
    
    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.interfaces import IFeedUUID
    >>> from vice.outbound.adapters import FeedUUID
    >>> verifyClass(IFeedUUID, FeedUUID)
    True
    
    """

    implements(IFeedUUID)
    adapts(IFeed)

    def __init__(self, context):
        self.context = context

    @property
    def UUID(self):
        return IFeedUUID(self.context.config).UUID
