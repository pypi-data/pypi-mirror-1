from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from csci.countdown import countdownMessageFactory as _

import datetime
import time
import urllib
import twitter
import signal

import socket
from lib import twitter

def _postToTwitter(uname, passwd, text):
    '''sends a post to twitter under specified username'''
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
        
#


class IdailytweetView(Interface):
    """
    dailytweet view interface
    """

    def test():
        """ test method"""


class dailytweetView(BrowserView):
    """
    dailytweet browser view
    """
    implements(IdailytweetView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def daily_tweet(self):
        
        today = datetime.date.today()       

        #in debug mode, overwrite the last posting record with '0'
        if self.context.debugmode:
            print '-----------------debug: counter reset'
            self.context.lastpost = str(time.mktime(datetime.datetime.utcnow().timetuple()))
            self.context.debugmode = False
            
        #grab time of last update
        if not hasattr(self.context, 'lastpost'):
            self.context.lastpost = str(time.mktime(datetime.datetime.utcnow().timetuple()))
        time_sec = float(self.context.lastpost)
       
        #calc time till next post
        next_post = float(time_sec) + float(self.context.t_interval)*60
        print '-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'
        print next_post - (time.mktime(datetime.datetime.utcnow().timetuple()))
        print next_post
        print (time.mktime(datetime.datetime.utcnow().timetuple()))
        if (next_post-1) <= (time.mktime(datetime.datetime.utcnow().timetuple())):

            #update the time of last post
            #self.context.lastpost = str(time.mktime(datetime.datetime.utcnow().timetuple()))
            self.context.lastpost = next_post            
            
            #set up the variables
            t_text = str(self.context.tweettext)
            returned_dates = {}

            #############################
            #get the target @ GMT
            target_date = datetime.datetime(*time.strptime(self.context.target, "%d/%m/%y %H:%M")[:5])
            target_date = target_date.timetuple()
            #get the date and time NOW at GMT
            today_tt = datetime.datetime.utcnow()
            today_tt = today_tt.timetuple()            
            #calc the time diff:        
            togo = time.mktime(target_date) - time.mktime(today_tt)
            togo = datetime.timedelta(seconds=togo)

            #if the event has not passed
            if time.mktime(target_date) > time.mktime(today_tt):

                returned_dates['days'] = togo.days
                returned_dates['hours'] = str(float(togo.seconds)/60/60)
                returned_dates['hours'] = returned_dates['hours'].split('.')
                returned_dates['hours'] = returned_dates['hours'][0]
                returned_dates['mins'] = (togo.seconds - (int(returned_dates['hours'])*60*60))/60
                returned_dates['seconds'] = togo.seconds
                            
                #if the event has passed, end
    
                #print 'days:', returned_dates['days'],
                #print ', hours:', returned_dates['hours'],
                #print ', mins:', returned_dates['mins'],
                #print ', seconds:', returned_dates['seconds'],
    
                #now format the tweet:
                t_text = t_text.replace('$days$',(str(returned_dates['days'])))
                t_text = t_text.replace('$hours$',(str(returned_dates['hours'])))
                t_text = t_text.replace('$mins$',(str(returned_dates['mins'])))
                
                print t_text
                error=_postToTwitter(uname=self.context.tuser, passwd=self.context.tpass, text=t_text[:140])
                if error is not None:
                    print error
                    

                output = '---updates complete---'
        
            else:
                output = '--- event passed ---'
        else:
            output = '--- not time to post yet ---'
            
        #self.context.reindexObject()
        return output
        

