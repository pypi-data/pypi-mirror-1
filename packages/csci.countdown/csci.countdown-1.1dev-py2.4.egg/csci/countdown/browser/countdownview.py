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
        
        #get the target @ GMT
        target_date = datetime.datetime(*time.strptime(self.context.target, "%d/%m/%y %H:%M")[:5])
        target_date = target_date.timetuple()
        #get the date and time NOW at GMT
        today = datetime.datetime.utcnow()
        today = today.timetuple()
        
        #calc the time diff:        
        togo = time.mktime(target_date) - time.mktime(today)
        togo = datetime.timedelta(seconds=togo)
        
        #get the params to return
        returned_dates = {}
        returned_dates['target'] = self.context.target
        returned_dates['days']   = togo.days
        togo_list = str(togo).split(' ')
        togo_list = togo_list[2].split(':')
        returned_dates['hours']  = togo_list[0]
        returned_dates['mins']   = togo_list[1]
        returned_dates['secs']   = togo_list[2]
        
        #store the results
        self.context.returned_dates = returned_dates
        
        raw_text = str(self.context.abovecount)
        raw_text = raw_text.replace('$daystogo$', str(togo.days))
        
        returned_dates['text'] = raw_text
        
        return returned_dates
    
    
    
    
    
    
    
    