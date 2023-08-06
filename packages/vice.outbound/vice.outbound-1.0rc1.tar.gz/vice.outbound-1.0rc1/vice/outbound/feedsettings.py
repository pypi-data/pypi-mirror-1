from zope.interface import implements
from vice.outbound.interfaces import IFeedSettings
from persistent import Persistent

class FeedSettings(Persistent):
    """See IFeedSettings.

    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.interfaces import IFeedSettings
    >>> from vice.outbound.feedsettings import FeedSettings
    >>> verifyClass(IFeedSettings, FeedSettings)
    True
    
    """

    implements(IFeedSettings)

    enabled = False
    max_items = -1
    published_url_enabled = True
    recursion_enabled = True
