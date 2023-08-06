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
        
        
        raw_text = str(self.context.abovecount)        
        
        returned_dates = {}
        
        ##############################
        ##get the target @ GMT
        target_date = datetime.datetime(*time.strptime(self.context.target, "%d/%m/%y %H:%M")[:5])
        target_date = target_date.timetuple()
        ##get the date and time NOW at GMT
        today_tt = datetime.datetime.utcnow()
        today_tt = today_tt.timetuple()            
        ##calc the time diff:        
        togo = time.mktime(target_date) - time.mktime(today_tt)
        togo = datetime.timedelta(seconds=togo)
        ##get the days left to return
        returned_dates['days'] = togo.days
        returned_dates['hours'] = str(float(togo.seconds)/60/60)
        returned_dates['hours'] = returned_dates['hours'].split('.')
        returned_dates['hours'] = returned_dates['hours'][0]
        returned_dates['mins'] = (togo.seconds - (int(returned_dates['hours'])*60*60))/60
        returned_dates['seconds'] = togo.seconds
        ##############################


        #now format the tweet:
        if int(returned_dates['days']) > 0 :
            raw_text = raw_text.replace('$days$',(str(returned_dates['days']) + ' day'))
        elif int(returned_dates['days']) > 1 :
            raw_text = raw_text.replace('$days$',(str(returned_dates['days']) + ' days'))
        else:
            raw_text = raw_text.replace('$days$','')
            
        if int(returned_dates['hours']) > 0 :
            raw_text = raw_text.replace('$hours$',(str(returned_dates['hours']) + ' hour'))
        if int(returned_dates['hours']) > 1 :
            raw_text = raw_text.replace('$hours$',(str(returned_dates['hours']) + ' hours'))
        else:
            raw_text = raw_text.replace('$hours$','')
            
        if int(returned_dates['mins']) > 0 :
            raw_text = raw_text.replace('$mins$',(str(returned_dates['mins']) + ' min'))
        if int(returned_dates['mins']) > 1 :
            raw_text = raw_text.replace('$mins$',(str(returned_dates['mins']) + ' mins'))
        else:
            raw_text = raw_text.replace('$mins$','')
               
        
        returned_dates['text'] = raw_text
        
        return returned_dates
    
    
    
    
    
    
    
    