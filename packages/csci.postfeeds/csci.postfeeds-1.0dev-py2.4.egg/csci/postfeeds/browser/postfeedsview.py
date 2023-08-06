from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from csci.postfeeds import postfeedsMessageFactory as _

import urllib
import datetime
import time
import random
import unicodedata
from lib import twitter
from lib import feedparser
from lib import google_short


# some utility functions
def _removeSymb(text):
    from string import maketrans
    illegal  = '.,!"£$%^&*()_+=[]{}@#~?/><|\'¬`;:'
    
    for ill in illegal:
        text = text.replace(ill,'')
    
    return text
    
def _feedToList(url):
    ''' takes in a url and uses a universal feed parser to return 
    a list of entries with their own properties'''
    page = feedparser.parse(url)
    entries = page['entries']
    return entries

def _getPendingPosts(time_sec, entries):
    '''gets the posts which have been added 
    since the last check (time_sec)'''
    try:
        p_time = time.mktime(entries[0]['updated_parsed'])
    
        new_entries = []
        #grab the new entries
        if float(p_time) >= time_sec:
            for i in entries:
                if float(time.mktime(i['updated_parsed'])) <= time_sec:
                    break
                new_entries.append(i)
                print '--- added new post ---'
        errors = ' -posting OK'
    except:
        new_entries = []
        errors = ' -ERROR processing feed'

    return new_entries, errors

def _publishNews(context, title, description, text):
    '''publishes a news item to the site repository'''
    #####################################
    ##post and publish news item

    _newsSubDir = 'news'
    today = datetime.date.today()
    news_id = str(title)+ '-' +str(today)
    news_id += '-' + str(random.random()*100)[:2]
    news_id = news_id.replace(' ','-')
    news_id = _removeSymb(news_id)
    news_id = news_id.lower()

    #go to news folder
    root_app = context.restrictedTraverse(_newsSubDir)
    #create item
    news_item = root_app.invokeFactory(type_name='News Item',
                                       id=news_id,
                                       title=title,
                                       description=description,
                                       text=text)
    root_app.reindexObject()
    
    #automatically publish news item
    root_app = context.restrictedTraverse('news/'+news_id)
    urltool  = getToolByName(context, 'portal_url')
    workflow = getToolByName(context, "portal_workflow")
    review_state = workflow.getInfoFor(root_app, 'review_state')
    if review_state != 'published':
        error=workflow.doActionFor(root_app,'publish',comment='publised programmatically') 
    root_app.reindexObject()
    
def _postToTwitter(uname, passwd, text):
    '''sends a post to twitter under specified username'''
    print '------posting a tweet---'
    errors = ''
    ##login to twitter
    try:
        api = twitter.Api(username=uname, password=passwd)
    except:
        errors += 'Twitter login fail'
        return errors

    ##post the message
    try:
        statuses = api.PostUpdate(status=text[:140], in_reply_to_status_id=None)
    except:
        errors += 'Failed at posting'
        return errors
    
    return None
        
def _get_short(server='',
              action='get_or_create_hash',
              hmac='',
              email='',
              url='',
              short_name='anything',
              is_public='true'):    
    
    request_url = google_short.make_request_uri(server,                           #short.cannonscientific.com
                                                action,                           #get_or_create_hash
                                                hmac,                             #foobar
                                                user=email,                       #toor@cannonscientific.com
                                                url=url,                          #http://www.google.com
                                                shortcut=short_name,              #anything
                                                is_public=str(is_public).lower()  #true
                                                )

    response = urllib.urlopen(request_url)
    res = response.read()
    res = res.replace('true','True')
    res_dict = eval(res)
    end_url = 'http://' + str(server) + '/' + str(res_dict['shortcut'])
    
    return end_url
#

# main plone classes
class IpostfeedsView(Interface):
    """
    postfeeds view interface
    """

    def test():
        """ test method"""


class postfeedsView(BrowserView):
    """
    postfeeds browser view
    """
    implements(IpostfeedsView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def lookfornew(self):
        
        toPost = []
        #grab time of last update
        if self.context.lastpost == '':
            self.context.lastpost = str(time.mktime(datetime.datetime.utcnow().timetuple()))
        time_sec = float(self.context.lastpost)
        
        #loop over all feeds used:
        errors_out = []
        for rss in self.context.feedurl:
            if rss != '':
                #get the rss feed posts
                entries = _feedToList(str(rss))

                if entries == None:
                    break
                #check feed for new posts since last check
                new_list, errors = _getPendingPosts(time_sec,entries)
                toPost.extend(new_list)
                if errors is not None:
                    errors_out.append((str(rss) +'<br>'+errors))
        
        ####
        ## now post the new posts to various places
        for post in toPost:
            
            # convert unicode title and summary to ascii
            # needs import unicodedata
            text = post['summary']
            post['summary'] = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
            text = post['title']
            post['title']   = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
            
            ## news item
            if self.context.news_onoff:
                #create news item
                create_body = str(post['summary']) + '<br>'
                create_body +='<p><a href="%s" title="... read the original here ...">%s</a></p>' % (str(post['link']),str(post['title']))
                _publishNews(self.context, 
                             title=post['title'], 
                             description='',
                             text=create_body)

            ## twitter
            if self.context.t_onoff:
                #post to twitter
                print '---posting to twitter---',
                print str(post['summary'])[:70],
                uname  = self.context.t_uname
                passwd = self.context.t_pass
                
                # add short link to article/news
                shorturl = _get_short(server    ='s.14o.tw',
                                      action    ='get_or_create_hash',
                                      hmac      ='bubbles0909',
                                      email     ='toor@14o.tw',
                                      url       = post['link'],
                                      short_name='anything',
                                      is_public ='true')
                shorturl = shorturl.replace('/s.14o','/14o')
                
                # add url to tweet
                text = str(post['summary']) + ' ' + str(shorturl)
                text = text[:140]
                errors = _postToTwitter(uname, passwd, text)
                
                if errors is not None:
                    print errors
                else:
                    print 'twitter OK'
                    
                    
        #update time of last update
        self.context.lastpost = str(time.time()) 
        self.context.reindexObject()
                
        return errors_out
    
    
    
    