"""Definition of the postfeed content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from csci.postfeeds import postfeedsMessageFactory as _
from csci.postfeeds.interfaces import Ipostfeed
from csci.postfeeds.config import PROJECTNAME

postfeedSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    
    atapi.LinesField(
        'feedurl',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"Feed URL"),
            description=_(u"http"),
        ),
        required=True,
    ),
    
    atapi.TextField(
        'lastpost',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Last post captured"),
            description=_(u"This is the last post captured from the feed - do NOT edit"),
        ),
    ),

    atapi.BooleanField(
        'news_onoff',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Post a news item for posts?"),
            description=_(u"check box to keep a site record of posts"),
        ),
    ),
    
    atapi.BooleanField(
        't_onoff',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Post to Twitter"),
            description=_(u"Post to twitter"),
        ),
    ),

    atapi.StringField(
        't_uname',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Twitter Username"),
            description=_(u"enter username here"),
        ),
    ),

    atapi.StringField(
        't_pass',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Twitter Password"),
            description=_(u"password to twitter"),
        ),
    ),
    
    
    atapi.BooleanField(
        'enable_filters',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Enable Filters"),
            description=_(u"enable the filters below"),
        ),
    ),


    atapi.LinesField(
        'filter_inc',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"AND Filter"),
            description=_(u"accept posts containing ALL of the following"),
        ),
    ),

    
    atapi.LinesField(
        'filter_inc_or',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"OR filter"),
            description=_(u"accept posts containing ONE OR MORE of the following"),
        ),
    ),


    atapi.LinesField(
        'filter_excl',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"NOT Filter"),
            description=_(u"accept posts containing NONE of the following"),
        ),
    ),
    
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

postfeedSchema['title'].storage = atapi.AnnotationStorage()
postfeedSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(postfeedSchema, moveDiscussion=False)

class postfeed(base.ATCTContent):
    """Post feeds from here"""
    implements(Ipostfeed)

    meta_type = "postfeed"
    schema = postfeedSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    filter_inc_or = atapi.ATFieldProperty('filter_inc_or')

    enable_filters = atapi.ATFieldProperty('enable_filters')

    filter_excl = atapi.ATFieldProperty('filter_excl')

    filter_inc = atapi.ATFieldProperty('filter_inc')

    news_onoff = atapi.ATFieldProperty('news_onoff')

    lastpost = atapi.ATFieldProperty('lastpost')

    t_pass = atapi.ATFieldProperty('t_pass')

    t_uname = atapi.ATFieldProperty('t_uname')

    t_onoff = atapi.ATFieldProperty('t_onoff')

    feedurl = atapi.ATFieldProperty('feedurl')


atapi.registerType(postfeed, PROJECTNAME)
