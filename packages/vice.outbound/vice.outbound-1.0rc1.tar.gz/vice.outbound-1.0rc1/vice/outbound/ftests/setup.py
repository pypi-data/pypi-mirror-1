from transaction import get
from zope.dublincore.interfaces import IZopeDublinCore
from vice.interfaces import IFeedConfigs
from vice.syndication import FeedConfig
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.folder import Folder
from zope.app.file import File
from datetime import datetime
import time

def _buildFeedUrl(stringlist):
	return u'http://localhost/' + _buildFeedRelativeUrl(stringlist)

def _buildFeedRelativeUrl(stringlist):
    return '/'.join(stringlist)

def _dir(location, test, format, name, **kwargs):
    """Build a directory

    location The parent location
    test The test instance
    format The format for the feed on this directory
    name The name of the new directory

    **kwargs
    title The dc title of the new directory
    description The dc description of the new directory

    Returns the new directory
    """
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

def _feed(feedable, name, format, recurse, enabled, feed_url):
    configs = IFeedConfigs(feedable)
    config = FeedConfig()
    config.name = name
    config.format = format
    config.recurse = recurse
    config.enabled = enabled
    config.referring_URL = feed_url
    config.local_URL = feed_url
    configs.configs = ( config, )
    configs.enabled = enabled
    return feedable

def _file(folder, name, type, data, **kwargs):
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

def setUp(test, format):
    """Set up the test directory

    test The test that is being run, pass in self
    format the type of format, atom.xml or rss-1.0.xml

    Returns a list of folder urls
    """
    root = test.getRootFolder()

    feedlist = []

    content_name = u'emptyDir'
    feed_url = _buildFeedUrl([content_name, format])	
    feed = _dir(root, test, format, content_name, 
                description=u'Empty directory')
    feed = _feed(feed, u'emptyDirFeed', format, False, True, feed_url)
    feedlist.append(_buildFeedRelativeUrl([content_name, format]))

    content_name = u'OneFileDir'
    feed_url = _buildFeedUrl([content_name, format])
    feed = _dir(root, test, format, content_name,
                description=u'One file directory')
    feed = _file(feed, u'file1', u'text/plain', u'Data would be here.', description=u'A description for this file.')
    feed = _feed(feed, content_name + 'Feed', format, False, True, feed_url)
    feedlist.append(_buildFeedRelativeUrl([content_name, format]))

    content_name = u'TwoFileDir'
    feed_url = _buildFeedUrl([content_name, format])
    feed = _dir(root, test, format, content_name,
                description=u'Two file directory')
    feed = _file(feed, u'file1', u'data would be here', u'text/plain')
    time.sleep(2) # two entries with same timestamp is invalid
    feed = _file(feed, u'file2', u'more data would be here', u'text/plain')
    feed = _feed(feed, content_name + 'Feed', format, False, True, feed_url)
    feedlist.append(_buildFeedRelativeUrl([content_name, format]))

    get().commit()
    return feedlist
