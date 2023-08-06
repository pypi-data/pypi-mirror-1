from zope.interface import implements
from zope.component import adapter, adapts
from zope.annotation import factory
from BTrees.IOBTree import IOBTree
import persistent
from uuid import uuid1
from vice.outbound.interfaces import IFeedConfigs, \
    IFeedable, IFeedConfig, IItemUUIDable, IFeedSettings, INormalizedString
from zope.component import getUtility

import logging


class FeedConfig(persistent.Persistent):
    """See IFeedConfig.
    
    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.feedconfig import FeedConfig
    >>> from vice.outbound.interfaces import IFeedConfig
    >>> from vice.outbound.interfaces import IItemUUIDable
    >>> verifyClass(IFeedConfig, FeedConfig)
    True
    >>> verifyClass(IItemUUIDable, FeedConfig)
    True

    >>> from zope.component import provideAdapter
    >>> from vice.outbound.feedconfig import NormalizedString
    >>> provideAdapter(NormalizedString, adapts=(unicode,))

    >>> fc = FeedConfig()
    >>> fc.name = u'foo'
    >>> fc.id()
    'foo'
    
    >>> fc = FeedConfig()
    >>> fc.id()
    Traceback (most recent call last):
       ...
    AttributeError: Attribute 'name' is blank
    
    """

    implements(IFeedConfig, IItemUUIDable)

    auto_discover = False
    enabled = False
    name = u''
    format = u''
    recurse = False
    published_url = u''
    UUID = uuid1()

    def id(self):
        if getattr(self, 'id_state', None) is None:
            if self.name == u'':
                raise AttributeError("Attribute 'name' is blank")
            self.id_state = str(INormalizedString(self.name))
        return self.id_state

class FeedConfigs(persistent.Persistent):
    """See IFeedConfigs

    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.feedconfig import FeedConfigs
    >>> from vice.outbound.interfaces import IFeedConfigs
    >>> verifyClass(IFeedConfigs, FeedConfigs)
    True
    
    >>> from zope.interface import implements
    >>> from zope.component import provideUtility
    >>> from vice.outbound.interfaces import IFeedSettings
    >>> class DummyFeedSettings(object):
    ...     implements(IFeedSettings)
    ...     max_items = 5
    >>> provideUtility(DummyFeedSettings())
    >>>
    >>> fcs = FeedConfigs()
    >>> fcs.max_items
    5
    >>> [x for x in fcs]
    []
    >>> fcs.findConfigByID('foo')
    Traceback (most recent call last):
       ...
    KeyError: 'No match for foo in []'
    >>> fcs.configForAutodetect()

    >>> from vice.outbound.feedconfig import FeedConfig
    >>> c1 = FeedConfig()
    >>> c1.auto_discover = False
    >>> c1.name = u'foo'
    >>> c2 = FeedConfig()
    >>> c2.auto_discover = True
    >>> c2.name = u'bar'    
    >>> fcs.configs = (c1, c2)
    >>> len([x for x in fcs])
    2
    >>> fcs.findConfigByID(u'foo').id()
    'foo'
    >>> fcs.configForAutodetect().auto_discover
    True
    
    """
    implements(IFeedConfigs)
    adapts(IFeedable)
    enabled = False
    configs = ()

    def __init__(self):
        self.max_items = getUtility(IFeedSettings).max_items

    def findConfigByID(self, id):
        """See IFeedConfigs
        """
        try: 
            return [s for s in self.configs if s.id() == id][0]
        except IndexError:
            ids = [s.id() for s in self.configs]
            raise KeyError('No match for %s in %s' % (id, ids))

    def configForAutodetect(self):
        autos = [s for s in self.configs if s.auto_discover]
        if not autos:
             return None
        return autos[0]
    
    def __iter__(self):
        return iter(self.configs)

feedconfigs_adapter = factory(FeedConfigs)

class NormalizedString(object):
    """Normalizes a string so it can be safely used in a URL.
    
    >>> from zope.interface.verify import verifyClass
    >>> from vice.outbound.interfaces import INormalizedString
    >>> from vice.outbound.feedconfig import NormalizedString
    >>> verifyClass(INormalizedString, NormalizedString)
    True
    
    >>> str(NormalizedString('foo'))
    'foo'
    
    >>> str(NormalizedString('foo bar'))
    'foo-bar'
    
    """
    implements(INormalizedString)

    def __init__(self, s):
        self.normalized = titleToNormalizedId(s)

    def __str__(self):
        return self.normalized

##########################################################################
##########################################################################
##########################################################################
# Shout-out to wicked and Anders Pearson, the original author, for the 
# following code. Original at: 
# http://dev.plone.org/collective/browser/wicked/trunk/wicked/normalize.py
##########################################################################

import re

mapping = {138: 's', 140: 'OE', 142: 'z', 154: 's', 156: 'oe', 158: 'z', 159: 'Y', 
192: 'A', 193: 'A', 194: 'A', 195: 'A', 196: 'A', 197: 'a', 198: 'E', 199: 'C', 
200: 'E', 201: 'E', 202: 'E', 203: 'E', 204: 'I', 205: 'I', 206: 'I', 207: 'I', 
208: 'D', 209: 'n', 211: 'O', 212: 'O', 214: 'O', 216: 'O', 217: 'U', 218: 'U', 
219: 'U', 220: 'U', 221: 'y', 223: 'ss', 224: 'a', 225: 'a', 226: 'a', 227: 'a', 
228: 'a', 229: 'a', 230: 'e', 231: 'c', 232: 'e', 233: 'e', 234: 'e', 235: 'e', 
236: 'i', 237: 'i', 238: 'i', 239: 'i', 240: 'd', 241: 'n', 243: 'o', 244: 'o', 
246: 'o', 248: 'o', 249: 'u', 250: 'u', 251: 'u', 252: 'u', 253: 'y', 255: 'y'}


def normalizeISO(text=""):
    fixed = []
    for c in list(text):
        if ord(c) < 256:
            c = mapping.get(ord(c),c)
        else:
            c = "%x" % ord(c)
        fixed.append(c)
    return "".join(fixed)


pattern1 = re.compile(r"^([^\.]+)\.(\w{,4})$")
pattern2 = re.compile(r'r"([\W\-]+)"')
def titleToNormalizedId(title=""):
    title = title.lower()
    title = title.strip()
    title = normalizeISO(title)
    base = title
    ext = ""
    m = pattern1.match(title)
    if m:
        base = m.groups()[0]
        ext = m.groups()[1]
    parts = pattern2.split(base)
        
    slug = re.sub(r"[\W\-]+","-",base)
    slug = re.sub(r"^\-+","",slug)
    slug = re.sub(r"\-+$","",slug)
    if ext != "":
        slug = slug + "." + ext
    return slug

##########################################################################
# End borrowed code block
##########################################################################
##########################################################################
##########################################################################
