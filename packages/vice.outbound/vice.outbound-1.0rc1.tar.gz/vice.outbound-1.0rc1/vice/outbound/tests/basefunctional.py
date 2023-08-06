from Globals import package_home
from cStringIO import StringIO
from datetime import datetime
import logging
import time
import os
import re
from transaction import get
from zope.interface import implements, Interface, providedBy, alsoProvides
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility
from zope.component import getSiteManager
from vice.outbound.feedsettings import FeedSettings
from urllib2 import HTTPError
from vice.outbound.interfaces import IFeedConfigs, INormalizedString
from vice.outbound.feedconfig import FeedConfig
from vice.outbound.interfaces import IFeed, IFeedItem, \
    IFeedSettings
from vice.outbound.feedformats.interfaces import IFeedFormats
from datetime import datetime
import time
#from feedvalidator import _validate
import logging
from feedparser import parse
from Testing import ZopeTestCase
try:
  from Products.Five.testbrowser import Browser
except ImportError:
  from zope.testbrowser.testing import Browser
from mechanize._mechanize import LinkNotFoundError

import vice.outbound

atom_format = 'atom'
rss1_format = 'rss-1'
rss2_format = 'rss-2'

class BaseTestFeeds(object):
    def testAtom(self):
        self._testAllFeeds(atom_format, False, True)

    def testRss_1(self):
        self._testAllFeeds(rss1_format, False, True)

    def testRss_2(self):
        self._testAllFeeds(rss2_format, False, True)

    def testAtomRecurse(self):
        self._testAllFeeds(atom_format, True, True)

    def testRss1Recurse(self):
        self._testAllFeeds(rss1_format, True, True)

    def testRss2Recurse(self):
        self._testAllFeeds(rss2_format, True, True)

    def testAtomDisabled(self):
        self._testOneFeed(atom_format, False, False)

    def testRss_1Disabled(self):
        self._testOneFeed(rss1_format, False, False)

    def testRss_2Disabled(self):
        self._testOneFeed(rss2_format, False, False)

    def testFeedSettings(self):
        fs = getUtility(IFeedSettings)
        self.assertEqual(fs.enabled, False)
        fs.enabled = True
        self.assertEqual(fs.enabled, True)
        fs.enabled = False
        self.assertEqual(fs.enabled, False)

    def testAtomGlobalDisabled(self):
        self._testOneFeed(atom_format, False, True, -1, False)

    def testRss_1GlobalDisabled(self):
        self._testOneFeed(rss1_format, False, True, -1, False)

    def testRss_2GlobalDisabled(self):
        self._testOneFeed(rss2_format, False, True, -1, False)

    def testMaxItemsNegative(self):
        self._testAllFeeds(atom_format, False, True, -100)

    def testMaxItemsZero(self):
        self._testAllFeeds(atom_format, False, True, 0)

    def testMaxItemsOne(self):
        self._testAllFeeds(atom_format, False, True, 1)

    def testMaxItemsLarge(self):
        self._testAllFeeds(atom_format, False, True, 1000)

    def _getRoot(self):
        pass

    def _initAdminBrowser(self):
        # XXX TODO: should save off old roles here, but not sure how
        self.setRoles(['Manager'])

        adminBrowser = Browser()
        adminBrowser.open(self._getRoot().absolute_url())
        adminBrowser.getControl('Log in').click()
        adminBrowser.getControl('Login Name').value = 'manager'
        adminBrowser.getControl('Password').value = 'secret'
        adminBrowser.getControl('Log in').click()

        self.adminBrowser = adminBrowser

        # XXX TODO: uncomment this when figured out how to get old_roles
        #self.setRoles(old_roles)
        
        
    def _testOneFeed(self, format, recurse, enabled, max_items=-1, global_enabled=True):
        self._initAdminBrowser()
        feeds = self.localSetUp(format, recurse, enabled, max_items, number=1)
        self._testFeeds(format, recurse, enabled, max_items, global_enabled, feeds)

    def _testAllFeeds(self, format, recurse, enabled, max_items=-1, global_enabled=True):
        self._initAdminBrowser()
        feeds = self.localSetUp(format, recurse, enabled, max_items)
        self._testFeeds(format, recurse, enabled, max_items, global_enabled, feeds)
    
    def _testFeeds(self, format, recurse, enabled, max_items=-1, global_enabled=True, feeds=[]):

        self.global_setup(global_enabled, True, -1, True, True)

        browser = Browser()
        # commented out to make the 404 test for disabled feeds work
#        browser.handleErrors = False
        # no secured feeds as of now, so shouldn't log in
        # XXX TODO: will need to selectively re-enable when testing 
        # secure feeds
#        browser.open(self._getRoot().absolute_url() + '/login_form')
#        browser.getControl('Login Name').value = 'manager'
#        browser.getControl('Password').value = 'secret'
#        browser.getControl('Log in').click()

        futil = getUtility(IFeedFormats)

        for feed in feeds:

            try:
                browser.open('%s/folder_listing' % self._getRoot().absolute_url())
                browser.getLink(feed['content_name']).click()
                browser.getLink(feed['feed_name']).click()
                #print browser.url
            except Exception, e:
                if not (enabled and global_enabled) \
                    and isinstance(e, LinkNotFoundError):
                    continue
                print '%s\n%s\n%s' % (self._getRoot().absolute_url(), 
                                      feed['content_name'], feed['feed_name'])
                raise
            if 'Forgot your password?' in browser.contents:
                self.fail('Got a login page, not a  feed')
            self.assertEqual(global_enabled, True)
            self.assertEqual(enabled, True)
            parsed = parse(browser.contents)
            self_url = findUrl(u'self', parsed.feed.links, parsed.feed.link)
            fed = getFedFromZope(self_url, self._getRoot())
            feed_adapter_name = futil.getFormatInfo(feed['format'])['feed_adapter_name']
            item_adapter_name = futil.getFormatInfo(feed['format'])['item_adapter_name']
            ifd = getMultiAdapter((fed, 
                                   str(INormalizedString(feed['feed_name'])), 
                                   item_adapter_name), 
                                  IFeed, feed_adapter_name)
            syndItems = self.getSyndicatableItems(fed, ifd, recurse, self)

            self.createFeedChecker(fed, ifd, parsed.feed, format).check()

            # Confirm that the number of syndicated items in the folder can be
            # adapted to IFeedItem and match the number of items in the feed,
            # taking into account the max items for the feed (if set)
            # This checks the feed adapter's traversal algorithm, 
            # not entry adaptation
            max_items = IFeedConfigs(fed).max_items
            if max_items >= 0:
              # max_items only applies when positive.  confirm we parsed
              # the number we should expect.
              if len(syndItems) > len(parsed.entries):
                self.assertEqual(max_items, len(parsed.entries))
              else:
                self.assertEqual(len(syndItems), len(parsed.entries))
            else:
              self.assertEqual(len(syndItems), len(parsed.entries))

            if len(parsed.entries):
                previousTimestamp = \
                    datetimeFromRFC3339(parsed.entries[0].updated)
            for entry in parsed.entries:
                thisTimestamp = datetimeFromRFC3339(entry.updated)
                if (thisTimestamp > previousTimestamp):
                    self.fail("Syndicated items not ordered modified desc " \
                              "in %s" % zope_url)
                previousTimestamp = thisTimestamp
                eo = syndItems[entry.link]
                self.createEntryChecker(eo, entry, ifd, format).check()

    def createFeedChecker(self, fed, ifd, feed, format):
        """Override to provide a feedchecker with specific dependencies.
        """

        pass

    def createEntryChecker(self, eo, entry, ifd, format):
        """Override to provide a entrychecker with specific dependencies.
        """

        pass

    def getSyndicatableItems(self, container, ifd, recurse, test):
        """Return a dictionary whose values are all the items in the container
        that are syndicatable (i.e. adaptable to IFeedItem).  The keys are
        the urls used in the feeds.
         """

        syndItems = {}
        for item in container.values():
            ifaces = providedBy(item).flattened()
            if ITestSyndicated in ifaces:
                if queryMultiAdapter((item, ifd, ifd.item_adapter_name), IFeedItem):
                    syndItems[self.getLinkForItem(item)] = item
                else:
                    test.fail("""'%s' marked ITestSyndicated w/o an IFeedItem 
                              adapter""" % item.__class__)
            elif recurse and isFolderish(item):
                for a in self.getSyndicatableItems(item, ifd, recurse, test).items():
                    syndItems[a[0]] = a[1]
        return syndItems

    def getLinkForItem(self, item):
        """Override to provide a link finder with specific dependencies.
        """

        pass

    def global_setup(self, enabled, visible, max_items):
        getUtility(IFeedSettings).enabled = enabled

    def localSetUp(self, format, recurse, enabled, max_items=-1, number=None):
        """Set up the test directory

        format the type of format, atom.xml or rss-1.0.xml

        Returns a list of folder urls
        """

        feedlist = []
        futil = getUtility(IFeedFormats)
        factories = self.getTestFactories()
        if number > -1:
            factories = factories[:number]
        for f in factories:
            content_name, feed = f(self._getRoot(), format)
            feed_name = content_name + 'feed'
            self.feed(feed, feed_name, format, recurse, enabled, max_items)
            view = futil.viewForDisplayName(self.decodeFormat(format))
            feedlist.append({'content_name':content_name, 
                             'feed_name':feed_name,
                             'format':format,
                            })
        get().commit()
        return feedlist

    def decodeFormat(self, format):
        return {'atom':'Atom',
                'rss-1':'RSS 1.0',
                'rss-2':'RSS 2.0',
               }[format]

    def getTestFactories(self):
        pass

    def feed(self, feedable, name, format, recurse, enabled, max_items=-1):
        pass

    def afterSetUp(self):
        # now registering using genericsetup
        # which is zope2-specific and lives in the app hierarchy
        # XXX TODO: once we start testing in zope3, we'll have to come
        # up with a way that is zope3ish to handle registering
        # the sitelocal IFeedSettings utility
        #sm = getSiteManager(self._getRoot())
        #sm.registerUtility(FeedSettings())
        pass

def getDataDir(globals):
    """ Returns the filesystem path to the test data directory. """

    home = package_home(globals)
    datadir = os.path.join(home, 'tests', 'data')
    return datadir

class ITestSyndicated(Interface):
    """ A marker interface to mark items expected in a test feed """

class ITestSyndicatedWithEnclosure(ITestSyndicated):
    """ A marker interface to mark items expected in a test feed that should 
    contain enclosures
    """

def _buildFeedUrl(stringlist):
	return u'http://localhost/' + _buildFeedRelativeUrl(stringlist)

def _buildFeedRelativeUrl(stringlist):
    return '/'.join(stringlist)

def findUrl(rel, links, dfltlink):
    urls = filter(lambda x: x.rel == rel, links)
    if urls:
        url = urls[0].href
    else:
        url = dfltlink
    return url

def getFedFromZope(self_url, zope_root):
    path = self_url.split('/')[4:-2]
    fed = zope_root
    for element in path:
        fed = fed[element]
    return fed

def validateFeed(rawdata, baseURI, encoding, selfURIs,
                                 firstOccurrenceOnly=True):
    loggedEvents = []
    return _validate(rawdata, firstOccurrenceOnly,
                                         loggedEvents, baseURI, encoding,
                                         selfURIs)

try:
    # From Plone 2.1
    from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder
except ImportError, e:
    # Up to Plone 2.0.5
    INonStructuralFolder = None
from Acquisition import aq_base

def isFolderish(content):
    """Can we walk in this content (recursively) ?"""
    if INonStructuralFolder is not None:
        # Plone 2.1 and up
        if INonStructuralFolder.isImplementedBy(content):
            return False
    return bool(getattr(aq_base(content), 'isPrincipiaFolderish', False))

def datetimeFromRFC3339(rfc3339):
    """For testing needs, such as comparing dates, this method does
    a cheap regex match on the expected fields in an RFC3339 datetime
    string and returns a datetime instance.  No correction for timezone
    attempted, assumed to be in UTC.  The only RFC3339 format
    supported at this time is: 'yyyy-mm-ddThh:mm:ssZ'
    """
    pattern = re.compile('(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)Z')
    match = pattern.search(rfc3339)
    return datetime(int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                    int(match.group(4)),
                    int(match.group(5)),
                    int(match.group(6)))
                    

###############################

class FeedChecker(object):
    def __init__(self, obj, ifd, feed, test, format):
        self.obj = obj
        self.ifd = ifd
        self.feed = feed # parsed.feed
        self.test = test
        self.format = format

    def check(self):
        # XXX TODO: Re-check the specs to make sure we're checking 
        # the right attributes for the right formats
        self.title()
        self.link()
        self.subtitle()
        if self.format in ('atom', 'rss-2'):
            self.modified()
        if self.format == 'atom':
            self.uid()

    def title(self):
        self.test.assertEqual(self.feed.title, self.obj.title)

    def link(self):
        # XXX TODO: Fix later
        # self.test.assertEqual(self.feed.link, '/'.join(ifd.absolute_url().split('/')[:-1]))
        pass

    def subtitle(self):
        self.test.assertEqual(self.feed.subtitle, self.obj.description)

    def modified(self):
        pass

    def uid(self):
        self.test.assertEqual(self.feed.id, 'urn:syndication:' + self.ifd.UID)

class EntryChecker(object):
    def __init__(self, obj, entry, feed, test, format):
        self.obj = obj
        self.entry = entry
        self.feed = feed
        self.test = test
        self.format = format

    def check(self):
        # XXX TODO: Re-check the specs to make sure we're checking 
        # the right attributes for the right formats
        self.title()
        self.description()
        if self.format in ('atom','rss-2'):
            self.uid()
            self.summary()
            self.modified()
            self.content()
            self.enclosure()
        if self.format == 'atom':
            self.created()

    def title(self):
        self.test.assertEqual(self.entry.title, self.obj.title)

    def uid(self):
        ifdi = getMultiAdapter((self.obj, self.feed), IFeedItem, name=self.feed.item_adapter_name)
        self.test.assertEqual(self.entry.id, 'urn:syndication:' + ifdi.UID)

    def summary(self):
        if hasattr(self.entry, 'summary'):
            self.test.assertEquals(self.entry.summary, self.obj.description)
        else:
            self.test.assertEquals(u'', self.obj.description)

    def description(self):
        # XXX TODO: killed this line because it seems to trigger a bug in
        # feedparser with atom and the event feed which results in the 
        # body ending up in the subtitle. until I get around to submitting
        # the bug and getting a fix, we'll ignore this....
        #self.test.assertEqual(self.entry.description, self.obj.description)
        pass

    def created(self):
        pass

    def modified(self):
        pass

    def content(self):
        pass

    def enclosure(self):
        if hasattr(self.entry, 'enclosures'):
            enc = self.entry.enclosures[0]
        else:
            enc = None
        if not ITestSyndicatedWithEnclosure in providedBy(self.obj).flattened():
            return
        self.test.failUnless( enc is not None)
        self.test.assertEquals(enc.href, self.obj.absolute_url())
        self.test.assertEquals(enc.length, unicode(self.obj.get_size()))
        self.test.assertEquals(enc.type, self.obj.getContentType())

