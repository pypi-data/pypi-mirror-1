from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from csci.postfeeds import postfeedsMessageFactory as _

class Ipostfeed(Interface):
    """Post feeds from here"""
    
    # -*- schema definition goes here -*-
    news_onoff = schema.Bool(
        title=_(u"Post a news item for posts?"), 
        required=False,
        description=_(u"check box to keep a site record of posts"),
    )

    lastpost = schema.Text(
        title=_(u"Last post captured"), 
        required=False,
        description=_(u"This is the last post captured from the feed"),
    )

    t_pass = schema.TextLine(
        title=_(u"Twitter Password"), 
        required=False,
        description=_(u"password to twitter"),
    )

    t_uname = schema.TextLine(
        title=_(u"Twitter Username"), 
        required=False,
        description=_(u"enter username here"),
    )

    t_onoff = schema.Bool(
        title=_(u"Post to Twitter"), 
        required=False,
        description=_(u"Post to twitter"),
    )

    feedurl = schema.TextLine(
        title=_(u"Feed URL"), 
        required=True,
        description=_(u"http://......."),
    )

