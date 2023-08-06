""" NB - this file has been renamed in order to prevent the enclosed
tests from running (and failing).  At this date, we are not testing
in Zope 3 - which these tests are intended to exercise.  Bring back
to life when ready by renaming this file to:
  testFunctional.py
"""

from vice.outbound.tests.basefunctional \
    import BaseTestFeeds, FeedChecker, EntryChecker
from transaction import get
from zope.dublincore.interfaces import IZopeDublinCore
#from vice.outbound.interfaces import IFeedConfigs
#from vice.outbound.feedconfig import FeedConfig
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.folder import Folder
from zope.app.file import File
from datetime import datetime
import time
from cStringIO import StringIO
#from feedvalidator import _validate
from Testing.ZopeTestCase.ZopeTestCase import FunctionalTestCase

class TestZopeFeeds(BaseTestFeeds, FunctionalTestCase):
    def _getRoot(self):
        return self.folder

    def getTestFactories(self):
        return (createTestEmptyDir,
                createTestOneFileDir,
                createTestTwoFileDir,
               )

    def createFeedChecker(self, fed, ifd, feed, format):
        return ZopeFeedChecker(fed, ifd, feed, self, format)

    def createEntryChecker(self, eo, entry, ifd, format):
        return ZopeEntryChecker(eo, entry, ifd, self, format)

    def getLinkForItem(self, item):
        return item.absolute_url()

    def afterSetUp(self):
#        zcml.load_site()
#        membership = getToolByName(self.portal, 'portal_membership')
#        membership.addMember('manager', 'secret', ('Manager',), ())\
        pass

class ZopeFeedChecker(FeedChecker):
    def modified(self):
        if self.obj.modified():
            pass # XXX TODO
        else:
            pass # XXX TODO

class ZopeEntryChecker(EntryChecker):
    def created(self):
        # We shouldn't be using RFC3339 to validate feed correctness, as
        # it's used in producing the feed and thus can't check itself,
        # but given the timezone/DST issues, we know no other option.
        pass # XXX TODO

    def modified(self):
        # We shouldn't be using RFC3339 to validate feed correctness, as
        # it's used in producing the feed and thus can't check itself,
        # but given the timezone/DST issues, we know no other option.
        if self.obj.modified():
            pass # XXX TODO
        else:
            pass # XXX TODO

    def content(self):
        content = self.entry.content[0].value
        pass # XXX TODO


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZopeFeeds))
    return suite

def _dir(location, format, name, **kwargs):
    """Build a directory

    location The parent location
    format The format for the feed on this directory
    name The name of the new directory

    **kwargs
    title The dc title of the new directory
    description The dc description of the new directory

    Returns the new directory
    """

    if 'title' in kwargs:
       title = kwarrgs['title']
    else:
        title = name

    current = location[name] = Folder()
    zdc = IZopeDublinCore(current)
    if 'title' in kwargs:
        zdc.title = title
    else:
        zdc.title = name
    if 'description' in kwargs:
        zdc.description = kwargs['description']
    if 'created' in kwargs:
        zdc.created = kwargs['created']
    else:
        zdc.created = datetime.utcnow()
    return current

def _file(folder, name, type, data, **kwargs):

    if 'title' in kwargs:
        title = kwargs['title']
    else:
        title = name

    folder[name] = File(data, type)
    zdc = IZopeDublinCore(folder[name])
    if 'title' in kwargs:
        zdc.title = title
    else:
        zdc.title = name
    if 'description' in kwargs:
        zdc.description = kwargs['description']
    if 'created' in kwargs:
        zdc.created = kwargs['created']
    else:
        zdc.created = datetime.utcnow()
    return folder

def createTestEmptyDir(root, format):
    content_name = 'emptyDir'
    feed = _dir(root, format, content_name, 
                description=u'Empty directory')
    return (content_name, feed)

def createTestOneFileDir(root, format):
    content_name = 'OneFileDir'
    feed = _dir(root, format, content_name,
                description=u'One file directory')
    feed = _file(feed, u'file1', u'text/plain', u'Data would be here.', description=u'A description for this file.')
    return (content_name, feed)

def createTestTwoFileDir(root, format):
    content_name = 'TwoFileDir'
    feed = _dir(root, format, content_name,
                description=u'Two file directory')
    feed = _file(feed, u'file1', u'data would be here', u'text/plain')
    time.sleep(2) # two entries with same timestamp is invalid
    feed = _file(feed, u'file2', u'more data would be here', u'text/plain')
    return (content_name, feed)

###############################

def compare(format, parsed, zope_root):
    self_url = findSelfUrl(parsed.feed.links, parsed.feed.link)
    path = self_url.split('/')[3:-1]
    feed = zope_root
    for element in path:
        feed = feed[element]

    if format == 'atom.xml':
        compareAtom(parsed, feed, self_url)
    elif format == 'rss-1.0.xml':
        compareRss1(parsed, feed)
    else:
        fail('Unknown format:', format)

    def compareAtom(parsed, feed, self_url):
        zdc = IZopeDublinCore(feed)
        print zdc.title
        ifd = getMultiAdapter((feed, AbsoluteURLStub(self_url)), IFeed)
        assertEqual(parsed.feed.title, zdc.title)
        assertEqual(parsed.feed.link, '/'.join(ifd.absolute_url().split('/')[:-1]))
        assertEqual(parsed.feed.subtitle, zdc.description)
        if zdc.modified:
            assertEqual(parsed.feed.updated_parsed, zdc.modified.utctimetuple())
        else:
            assertEqual(parsed.feed.updated_parsed, zdc.created.utctimetuple())
        assertEqual(parsed.feed.id, 'urn:syndication:' + ifd.UID)

        for entry in parsed.entries:
            child = findSelfUrl(entry.links, entry.link).split('/')[-1:][0]
            eo = feed[child]
            ezdc = IZopeDublinCore(eo)
            assertEqual(entry.title, ezdc.title)
            ifdi = getMultiAdapter((eo, ifd), IFeedItem)
            assertEqual(entry.id, 'urn:syndication:' + ifdi.UID)
            assertEquals(entry.published_parsed, ezdc.created.utctimetuple())
            if ezdc.modified:
                assertEquals(entry.updated_parsed, ezdc.modified.utctimetuple())
            else:
                assertEquals(entry.updated_parsed, ezdc.created.utctimetuple())
            if hasattr(entry, 'summary'):
                assertEquals(entry.summary, ezdc.description)
            else:
                assertEquals(u'', ezdc.description)
            assertEquals(entry.content[0].value, eo.data)
