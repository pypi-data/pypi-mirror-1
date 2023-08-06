# -*- coding: utf-8 -*-

from zope.interface import Interface

##code-section HEAD
##/code-section HEAD

class Irss_manager(Interface):
    """Marker interface for .rss_manager.rss_manager
    """

class Irss_feed(Interface):
    """Marker interface for .rss_feed.rss_feed
    """

class Irss_item(Interface):
    """Marker interface for .rss_item.rss_item
    """

class Irss_instance(Interface):
    """Marker interface for .rss_instance.rss_instance
    """

class Irss_history(Interface):
    """Marker interface for .rss_history.rss_history
    """

##code-section FOOT
##/code-section FOOT