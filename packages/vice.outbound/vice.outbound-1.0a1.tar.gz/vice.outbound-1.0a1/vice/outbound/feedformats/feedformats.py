from zope.interface import implements, alsoProvides
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from vice.outbound.feedformats.interfaces import IFeedFormats

class DefaultFeedFormats(object):
    """Utility for storing feed formats.
    
    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.feedformats.interfaces import IFeedFormats
    >>> from vice.outbound.feedformats.feedformats import DefaultFeedFormats
    >>> verifyClass(IFeedFormats, DefaultFeedFormats)
    True

    """
    implements(IFeedFormats)

    # Format is:
    # Display name of feed format,
    # Name of view to render feed format,
    # Name of adapter to used by the view to convert the context to the
    #     desired interface,
    # MIME type of the resulting feed,
    # character encoding for the resulting feed
    # the type to be used in the autodiscover link
    # whether the feed is a visible choice in the per-container config screen
    format_tuples = [
                     ('Atom', 'atom', 'vice-default', 'vice-default', 
                      'text/xml', 'utf-8', 'application/atom+xml', True),
                     ('RSS 2.0', 'rss-2', 'vice-default', 'vice-default', 
                      'text/xml', 'utf-8', 'application/rss+xml', True),
                     ('RSS 1.0', 'rss-1', 'vice-default', 'vice-default', 
                      'text/xml', 'utf-8', 'application/rss+xml', True),
                    ]


    @property
    def feed_formats(self):
        return [{
                 'name' : t[0],
                 'view' : t[1],
                 'feed_adapter_name' : t[2],
                 'item_adapter_name' : t[3],
                 'MIME_type' : t[4],
                 'encoding' : t[5],
                 'autodiscover_type' : t[6],
                 'visible' : t[7],
                } for t in self.format_tuples]

    def getFormatInfo(self, view):
        return [f for f in self.feed_formats 
                if f['view'] == view][0]

    def viewForDisplayName(self, display_name):
        return [f['view'] for f in self.feed_formats 
                if f['name'] == display_name][0]

def feedFormatVocabulary(context):
    utility = getUtility(IFeedFormats)
    return SimpleVocabulary.fromItems([(f['name'], f['view']) for f 
                                      in utility.feed_formats
                                      if f['visible']])
alsoProvides(feedFormatVocabulary, IVocabularyFactory)