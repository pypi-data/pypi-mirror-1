from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from csci.fourthplinth import fourthplinthMessageFactory as _

##
import datetime
from datetime import timedelta
import urllib
import re
from Products.statusmessages.interfaces import IStatusMessage
import time
import twitter
import random

import google_short

class IUDscheduleView(Interface):
    """
    UDschedule view interface
    """

    def test():
        """ test method"""


class UDscheduleView(BrowserView):
    """
    UDschedule browser view
    """
    implements(IUDscheduleView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        
    def update_schedule(self):
        '''this updates the page schedule and creates the twitter schedule'''
        
        ###################################################################
        ## get gmt dictionary
        #get the current gmtoffset for London:
        try:
            print '---trying---'
            gmt_page = urllib.urlopen("http://www.righthearted.com/runner.py?TZ_DATA_['London']")
            #gmt_page = urllib.urlopen("http://192.168.2.60/runner.py?TZ_DATA_['London']")
    
            gmt_page = gmt_page.readlines()

            gmt_offsets = {}
            for loc in gmt_page:
                loc = loc.replace('\n','')
                loc = loc.split('=')
                gmt_offsets[loc[0]] = int(loc[1])        

            self.context.gmt_offsets = gmt_offsets
            print '---sucess---'

        except:
            print '---failed---'
            if hasattr(self.context, 'gmt_offsets'):
                print '---got old one---'
                gmt_offsets = self.context.gmt_offsets
            else:
                print '---got new one---'
                gmt_offsets = {}
                gmt_offsets['London'] = 0
                self.context.gmt_offsets = gmt_offsets
        ##
        ###################################################################
        
        print gmt_offsets['London']
                
        #get schedule once a day
        today = datetime.date.today()
        today_t = str(today)+' '+'00:10'  # do the update at 00:10!

        now_date = datetime.datetime.utcnow() + timedelta(seconds=gmt_offsets['London'])
        when_date = datetime.datetime( *time.strptime(today_t,"%Y-%m-%d %H:%M")[:5])
        
        print '---checking for updates---', now_date
        
        #create last post parameter
        if not hasattr(self.context, 'lastpost'):
            self.context.lastpost = '0ೌ'
        if not hasattr(self.context, 'tschedule'):
            self.context.tschedule = ()

        
        #in debug mode, overwrite the last posting record with '0'
        if self.context.debugmode:
            self.context.lastpost = '0ೌ'
            
        #if not posted yet today ...
        if today != self.context.lastpost:
                    
            #check time
            if now_date > when_date:
                
                print '------getting new schedule---'
                #construct the page address for today
                fpurl = 'http://www.oneandother.co.uk/participants/day?day='
                fpurl += str(now_date).replace('/','-')[:10]
                #get the page
                raw_page = urllib.urlopen(fpurl)
                raw_page = raw_page.read()     
                
                #search for the partisipants:
                rawstr = r"""<li\ class=".+">\s*<span\ class='starts_at'>\s*<span\ class='time'>(?P<hour>\d+)
                \s*</span>\s*<span\ class='am-pm'>(?P<ampm>\w+)
                \s*</span>\s*<span\ class='corners'>\s*</span>\s*</span>\s*<span\ class='avatar'>\s*<img\ alt=".+"\ src="(?P<avatar>.+)"\ />
                \s*<span\ class='corners'></span>\s*</span>\s*<span\ class='name-wrapper'>\s*<span\ class='name'>
                ((\s*<a.+?"(?P<upath>.+?)">(?P<uname>.*)</a>)|\s*Anonymous)"""
                compile_obj = re.compile(rawstr,  re.MULTILINE| re.VERBOSE)        
                match_obj = compile_obj.findall(raw_page)
                
                #create the page layout for the page and news item
                twitter_schedule = ()
                schedule_html = '<h2>Schedule for ' + str(now_date).replace('/','-')[:10] + '</h2><br><br><table width=400px border=0px padding=5px ALIGN="CENTER">'
                
                for partisipant in match_obj:
                    hour   = str(partisipant[0])
                    ampm   = str(partisipant[1])
                    avatar = str(partisipant[2])
                    uurl   = 'http://www.oneandother.co.uk' + str(partisipant[5])
                    uname  = str(partisipant[6])
                    if uname == '' or uname == ' ':
                        uname = 'Anonymous'
                        
                    
                    shorturl = google_short.get_short(server    ='s.14o.tw',
                                                      action    ='get_or_create_hash',
                                                      hmac      ='bubbles0909',
                                                      email     ='toor@14o.tw',
                                                      url       = uurl,
                                                      short_name='anything',
                                                      is_public ='true')
                    
                    shorturl = shorturl.replace('/s.14o','/14o')

                    schedule_html += '<tr><td><h2>'+ hour +' '+ ampm + '</h2></td><td><img src="' + avatar + '" alt="No Image" /></td><td><a href="' +uurl + '">' +uname +  '</a></td></tr>'
                    
                    #Convert to 24hour
                    if ampm == 'PM':
                        if hour != '12':
                            hour = str(int(hour)+12)
                    #Correct midnight to 00:00
                    if ampm == 'AM':
                        if hour == '12':
                            hour = '00'                    
                        
                    twitstring = str(now_date).replace('-','/')[:10] + ', ' + hour + ':00, #oneandother '+ hour + ':00 - ' + uname + ' is just starting on the Fourth Plinth ' + shorturl
                    twitter_schedule += (twitstring,)
                
                schedule_html += '</table>'
                
                #store to results of our work:
                self.context.schedule_html = schedule_html
                self.context.tschedule += twitter_schedule
                
                
                #####################################
                ##post and publish news item

                #create news item as history
                root_app = self.context.restrictedTraverse('news')
                news_id = 'Fourth Plinth ' +str(today)
                if self.context.debugmode:
                    news_id += '-' + str(random.random()*100)[:2]
                news_id = news_id.replace(' ','-')
                news_id = news_id.replace(':','-')
                                
                news_item = root_app.invokeFactory(type_name='News Item',
                                                   id=news_id,
                                                   title='Fourth Plinth Schedule on ' +str(today),
                                                   description='The following people are on the plinth',
                                                   text=schedule_html)
                root_app.reindexObject()
                
                #automatically publish news item
                root_app = self.context.restrictedTraverse('news/'+news_id)
                urltool  = getToolByName(self.context, 'portal_url')
                workflow = getToolByName(self.context, "portal_workflow")
                review_state = workflow.getInfoFor(root_app, 'review_state')
                if review_state != 'published':
                    error=workflow.doActionFor(root_app,'publish',comment='publised programmatically') 
                    
                self.context.lastpost = today 
        
        
        
        #####################################
        ##check schedule for posts to send

        for post in self.context.tschedule:
            post_list = post.split(',')
            if len(post_list)>3:
                IStatusMessage(self.request).addStatusMessage(_('Badly formatted Tweet',len(post_list)), type='error')
            twit_date = post_list[0]
            twit_time = post_list[1]
            twit_text = post_list[2]

            #get posting date and time:
            
            #    adjust the time by -2 mins
            orig_time = time.strptime(twit_date+twit_time, "%Y/%m/%d %H:%M")
            orig_time = time.mktime(orig_time)
            orig_time += -121 #take off 2 mins (120 secs)
            new_time = time.localtime(orig_time)
            
            when_date = datetime.datetime(*new_time[:5])
            
            if now_date >= when_date:
                    print '------posting a tweet---', twit_text[:50]
                    ##post on twitter!
                    if self.context.tusername == '':
                        IStatusMessage(self.request).addStatusMessage(_('Username not set! Cannot post'), type='error')
                    if self.context.tpassword == '':
                        IStatusMessage(self.request).addStatusMessage(_('Password not set! Cannot post'), type='error')
                    
                    if not self.context.debugmode:
                        ##login to twitter
                        api = twitter.Api(username=self.context.tusername, password=self.context.tpassword)
                            
                        ##post the message
                        statuses = api.PostUpdate(status=twit_text[:140], in_reply_to_status_id=None)
                        
                    ##remove the posted entry from list
                    tweetstogo_out = ()
                    for item in self.context.tschedule:
                        if item != post:
                            tweetstogo_out += (item,)
                    self.context.tschedule = tweetstogo_out   

        
        
        
        return '---updates complete---'
        

    
    
    
        
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
