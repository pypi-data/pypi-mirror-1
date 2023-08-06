from zope.interface import Interface
from zope.schema import Iterable
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('vice')

class IFeedFormats(Interface):

    feed_formats = Iterable(
        title = _(u'Feed Formats'),
        description = _(u'Available formats for syndication feeds'),
        )

    def viewForDisplayName(display_name):
        """Use a display name for a feed format to look up the name of the
        view that renders that format.
        """
