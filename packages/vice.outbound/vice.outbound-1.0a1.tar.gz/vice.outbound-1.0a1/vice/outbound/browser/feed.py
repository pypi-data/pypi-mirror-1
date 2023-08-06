from vice.outbound.interfaces import IFeed, IFeedSettings
from vice.outbound.feedformats.interfaces import IFeedFormats
from zope.annotation.interfaces import IAnnotations
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import adapts, getAdapter, getMultiAdapter, \
    provideAdapter, getUtility
from zope.interface import implements
from zope.dublincore.interfaces import IZopeDublinCore
from zope.publisher.browser import BrowserPage
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
try: # zope2
    from zExceptions import NotFound
except ImportError: # zope3
    from zope.publisher.interfaces import NotFound
import logging

class FeedViewBase(BrowserPage):
    """Base browser view class. Unless you know a good reason, you
    should be extending BaseFeedViewWithUrlID and not this class.
    Need to define getTemplate in subclasses.
    """

    def getTemplate(self):
        raise ValueError, ("getTemplate method must be implemented in subclass")

    def __call__(self):
        context = self.context
        response = self.request.response

        futil = getUtility(IFeedFormats)
        format_info = futil.getFormatInfo(self.__name__)
        self.feed = getMultiAdapter((self.context, self.feed_name, 
                                     format_info['item_adapter_name']), 
                                    IFeed, name=format_info['feed_adapter_name'])

        if not (getUtility(IFeedSettings).enabled 
                and self.feed.config.enabled):
            raise NotFound, 'There is no feed at this address.'

        # removed because I don't know how to set the encoding based on a
        # container that may contain objects in several different
        # encodings...
        # besides, all the examples in the atom spec are in utf-8, so it
        # seems possible that atom *must* be in utf-8
        #encoding = context.getEncoding()
        #header = 'application/atom+xml; charset=%s' % encoding
        header = '%s; encoding=%s' \
                 % (format_info['MIME_type'], format_info['encoding'])
        response.setHeader('Content-Type', header)

        modified_gmt = getRFC822GMTDatetime(self.feed.modified)
        response.setHeader('Last-Modified', modified_gmt)

        return self.getTemplate()().encode(format_info['encoding'])

    def webURL(self):
         return absoluteURL(self.context, self.request)
    
    def publishTraverse(self, request, name):
        """ This uses the next argument as a setting and returns a self, configured. """
        self.feed_name=name
        return self

class FeedViewWithUrlIdBase(FeedViewBase):
    """Base class that adds getting the feed id from the URL.
    Split from FeedViewBase is necessary to allow backwards
    compatible feeds in Plone. All custom feed view classes should 
    extend this class, not FeedViewBase. Still need to define
    getTemplate in subclasses.
    """

    def __init__(self, context, request):
        if request['TraversalRequestNameStack']:
            self.feed_name = request['TraversalRequestNameStack'][-1]
        super(BrowserPage, self).__init__(context, request)

class Atom_1_0_FeedView(FeedViewWithUrlIdBase):
    """Browser view for Atom 1.0 feeds.
    """

    template = ViewPageTemplateFile('atom-1.0.pt')
    def getTemplate(self):
        return self.template

class RSS_2_0_FeedView(FeedViewWithUrlIdBase):
    """Browser view for RSS 2.0 feeds.
    """

    template = ViewPageTemplateFile('rss-2.0.pt')
    def getTemplate(self):
        return self.template

class RSS_1_0_FeedView(FeedViewWithUrlIdBase):
    """Browser view for RSS 1.0 feeds.
    """

    template = ViewPageTemplateFile('rss-1.0.pt')
    def getTemplate(self):
        return self.template

def getRFC822GMTDatetime(datetime):
        
	# TODO: figure out how to get the current timezone
	#       sometimes astimezone raises 'Naive datetime' errors
	#       import time; time.tzname returns some timezone info
	#       but returns a list not an string, so we cannot figure
	#       out which one is the correct timezone
	import rfc822, pytz, time
        
	#gmt = datetime.astimezone(pytz.timezone('GMT'))
	gmt = datetime
	if gmt:
            if hasattr(gmt, 'timetuple'):
		return rfc822.formatdate(time.mktime(gmt.timetuple()))
            else:
                return rfc822.formatdate(gmt)
