============================
 Vice Syndication Framework
============================

This package is the Zope layer of the outbound portion of the Vice syndication 
framework. It is meant to be able to run on either Zope 3 or Zope 2.10.x. 

Currently, this package is in disarray from the 2007 Google Summer of Code,
in which the Vice work was sponsored by Plone. The interfaces and utility
work, but the adapters which apply syndication capabilities to Zope (without
Plone) are out-of-date and do not work. The tests are incomplete and may fail.

This document contains some basic information about extending Vice. If you are 
interested in syndication in Plone 3.0, you should also look at the
vice.outbound.plone package. That package contains working adapters for Plone, 
as well as a Plone user interface.

Extending Vice - New Feed and Feed Entry Types

The two key interfaces for extension are IFeed and IFeedItem. IFeed represents
an entire feed and should be used to adapt a content item that can provide
individual feed entries; usually, this is a container like a folder. IFeedItem
represents an individual entry in a feed. Any items which should be able to
become entried in a feed must be adaptable to IFeedItem.

Another important interface is IFeedable. IFeedable is used to mark objects of
types that are capable of being configured as a feed. Thus, to enable a new
IFeed adapter, you must both declare the new IFeed adapter in ZCML and also
use ZCML (or another method) to mark any objects to be adapted by the new IFeed
adapter as IFeedable.

Extending Vice - New Feed Formats

In the future, this will be easy, but, as of now, it is a bit messy. Basically,
it involves creating a new page template for your feed format. Currently, if 
IFeed or IFeedItem do not provide the data you need to render your feed 
format, you will have to modify them to do so. In the future, feed adapters
will be pluggable, in concert with their feed page templates. You will also
need to make the feed format known as a possible format, which currently 
requires editing the hardcoded list of feed formats in IFeedConfig schema
in interfaces.py. Soon, all this will be done with a Vocabulary and you will
merely need to create a new Vocabulary term containing the relevant adapters
and page template.

Credits

This work was funded both by Google through Plone for the Summer of Code 2007 
and by the Georgia Institute of Technology.