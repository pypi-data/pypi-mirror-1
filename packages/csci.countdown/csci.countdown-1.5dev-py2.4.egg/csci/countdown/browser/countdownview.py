from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from csci.countdown import countdownMessageFactory as _

import time
import datetime


class IcountdownView(Interface):
    """
    countdown view interface
    """

    def test():
        """ test method"""


class countdownView(BrowserView):
    """
    countdown browser view
    """
    implements(IcountdownView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


    
    def calc_diff(self):
        

        t_text = str(self.context.abovecount)
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
            

        else:
            t_text = t_text.replace('$days$','0')
            t_text = t_text.replace('$hours$','0')
            t_text = t_text.replace('$mins$', '0')
                
                
        returned_dates['text'] = t_text
        
        return returned_dates
    
    
    
    
    
    
    
    