from zope.interface import Interface, Attribute
from BTrees.OOBTree import OOBTree
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.schema import Bool, Choice, Datetime, Dict, Field, Iterable, Int, \
    List, Object, Text, TextLine, Tuple, URI
from zope.i18nmessageid import MessageFactory
from collective.uuid import IUUIDs
from zope.interface import invariant

_ = MessageFactory('vice')


class IEnclosure(Interface):
    """Represents an 'enclosed' file that is explicitly linked to within
    an IFeedEntry.

    This is here to support podcasting.
    """

    def mimeType():
        """MIME content-type of the enclosed file.
        """

    def URL():
        """URL of the enclosed file.
        """

    def size():
       """Return the size/length of the enclosed file.
       """


class IFeedItem(Interface):
    """A single syndication feed item.
    """

    title = Attribute( \
        """Title of this item.
        """)

    description = Attribute( \
        """Description of this item.
        """)
    

    url = Attribute( \
        """Main URL to include in the feed.
        """)

    relatedUrls = Attribute( \
        """Related URLs
        """)

    # TODO: Body needs some thinkwork. RSS accepts all sorts of
    # stuff, but Atom is capable of including xhtml without needing
    # to resort to CDATA sections and escaping of tags.
    # 
    # See also xhtml, which should solve this.

    body = Attribute( "The raw body content of this item.")
       
    XHTML = Attribute( \
        """The (X)HTML body content of this item, or None.
        """)

    UID = Attribute( \
        """Universally unique ID for this item.

        Especially for the Atom format: this UID should never
        change. Never. This way tools can prevent display of double
        items (like items that are also aggregated into a "planet"
        that you read).
        """)

    author = Attribute( \
        """Author(s) of this item.
        """)

    effective = Attribute( \
        """The datetime this entry was first published.

        The date must be a datetime.datetime instance
        (standard python library datetime format).
        """)

    effectiveString = Attribute( \
        """The effective date in RFC3339 format.
        """)

    modified = Attribute( \
        """The datetime this entry was last modified.

        The date must be a datetime.datetime instance 
        (standard python library datetime format).
        """)

    modifiedString = Attribute( \
        """The modified date in RFC3339 format.
        """)

    tags = Attribute( \
        """The tags/keywords/subjects associated with this item.

        Return the tags as an iterable element. It is up to the 
        actual feed to handle the display.
        """)

    rights = Attribute( \
        """The dublin core "rights" associated with this item.
        """)

    enclosure = Attribute("""A contained IEnclosure instance or None.
        """)

class IFeed(Interface):
    """A syndication feed e.g. RSS, atom, etc.  To syndicate a container, 
    adapt it to IFeed.
    """

    def __iter__():
        """Return an iterable sequence of IFeedEntry objects with
        which to build a feed.  

        Objects are returned in sorted order.
        """

    description = Attribute("""The description of this feed.
        """)

    modified = Attribute("""The last modified datetime that applies to the whole feed.

        The date must be a datetime.datetime instance 
        (standard python library datetime format).
        """)

    modifiedString = Attribute("The RFC3339-formatted date string.")

    name = Attribute("Name(id) for this feed.")

    title = Attribute("Title of this feed, for display purposes.")

    UID = Attribute("Universally unique ID for this feed.")

    config = Attribute("Get the configuration defining this feed.")

    alternate_url = Attribute("Alternate URL for this feed.")

    self_url = Attribute("URL for this feed.")

class IFeedable(IAttributeAnnotatable):
    """Marker interface promising that an implementing object may be syndicated using 'IFeedConfigs' annotations.
    """

class IFeedUUIDable(IAttributeAnnotatable):
    """Marker interface used to mark an object as annotatable with a feed 
    UUID.
    """

class IItemUUIDable(IAttributeAnnotatable):
    """Marker interface used to mark an object as annotatable with feed entry
    UUIDs.
    """

class IFeedConfig(Interface):
    """Configuration for an individual feed.

    It extends IAnnotatable so that we can store a uuid utility on
    the feed as an annotation.
    """

    auto_discover = Bool(title=_(u'Auto Discover'),
                         description=_(u'Make this feed the auto-dicover link.'),
                   default=False,
                  )

    enabled = Bool(title=_(u'Enabled'),
                   description=_(u'Enable or disable this feed.'),
                   default=False,
                  )

    name = TextLine(title=_(u'Name'),
                    description=_(u'Name for this feed. Will be used as a label for end-users.'),
                   )

    format = Choice(title=_(u'Format'),
                    description=_(u'Data format for this feed'),
                    vocabulary="Feed Formats",
                   )

    recurse = Bool(title=_(u'Recurse'),
                   description=_(u'Include items in all containers under the current container'),
                   default=False,
                  )

    published_url = TextLine(title=_(u'Published URL'),
                             description=_(u'URL to publish or blank for default'),
                             required=False,
                            )

    def id():
        """Get the id for this feed. Generated based on current name the first
        time the method is called, but then set for all time. Will fail with an
        AttributeError if name is blank.
        """


def checkSubSchemataInvariants(self, iface=IFeedConfig):
    subSchemata = self.configs
    for subSchema in subSchemata:
        iface.validateInvariants(subSchema)


class IFeedConfigs(Interface):
    """Annotation that indicates the object can provide IFeed
    and that stores the current feed configuration.
    """
    
    invariant(checkSubSchemataInvariants)

    enabled = Bool(title=_(u'Enable syndication'),
                   description=_(u'Enable or disable all feeds of the current object'),
                   default=False,
                  )

    configs = Tuple(title=_(u'Feeds'),
                    description=_(u'Feeds available from the current object'),
                    required=False,
                    default=(),
                    value_type=Object(title=_(u'Feed configuration'),
                                      description=_(u'Feed configuration'),
                                      schema=IFeedConfig,
                                     ),
                   )

    max_items = Int(title=_(u'Maximum Items'),
                    description=_(u'Maximum number of items for all feeds of '
                                   'the current object.  Negative value '
                                   'implies no limit'),
                    required=True,
                  )

    def findConfigByID(url):
        """Find an IFeedConfig in IFeedConfigs by its ID.
        """
    def configForAutodetect():
        """Find the IFeedConfig for feed autodetection. Returns None if no
        autodetect feed is configured.
        """

class IItemUUID(Interface):
    """Get the UUID for this item in thus feed.
    """

    UUID = TextLine(title=_(u'UUID'),
                    description=_(u'UUID for item in this feed.'),
                    required=False,
                    readonly=True,
                   )

class IItemUUIDs(IUUIDs):
    """A uuid utility used as an annotation on a feed to track the
    uuids of the entries in the feed.
    """

class IFeedUUID(Interface):
    """Get the UUID for this feed.
    """

    UUID = TextLine(title=_(u'UUID'),
                    description=_(u'UUID for this feed.'),
                    required=False,
                    readonly=True,
                   )

class IFeedSettings(Interface):
    """Utility to hold the feed settings for a site.
    """

    enabled = Bool(title=_(u'Enabled'),
                   description=_(u'Enable potential syndication of all site '
                                 'content.'),
                   default=False)

    max_items = Int(title=_(u'Maximum Items'),
                    description=_(u'Default maximum number of items for all '
                                   'feeds. Negative value implies no limit.'),
                   required=True,
                   default=-1,
                  )

    published_url_enabled = Bool(title=_(u'Enable Published URLs'),
                                 description=_(u'Enable publishing URLs for '
                                                'feeds that differ from their '
                                                'actual URLs. Useful for '
                                                'Feedburner integration.'),
                                 default=True)

    recursion_enabled = Bool(title=_(u'Enable Recursion'),
                             description=_(u'Enable recusive feeds.'),
                             default=True)

class INormalizedString(Interface):
    """Converts a string into a normalized ID suitable for a URL.
    """

    def __str__():
        """Get the normalized string.
        """