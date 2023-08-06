from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from csci.countdown import countdownMessageFactory as _

class Icountdown(Interface):
    """Count down to a date"""
    
    # -*- schema definition goes here -*-
    tweetschedule = schema.List(
        title=_(u"schedules tweets for today:"), 
        required=False,
        description=_(u"Field description"),
    )

    tpass = schema.TextLine(
        title=_(u"Twitter Password"), 
        required=False,
        description=_(u"password"),
    )

    tuser = schema.TextLine(
        title=_(u"New Field"), 
        required=False,
        description=_(u"username"),
    )

    debugmode = schema.Bool(
        title=_(u"New Field"), 
        required=False,
        description=_(u"debug mode to create schedule every time"),
    )

    abovecount = schema.SourceText(
        title=_(u"Text Above count"), 
        required=True,
        description=_(u"enter <daystogo> to include the days left"),
    )

    target = schema.TextLine(
        title=_(u"Target Date and Time"), 
        required=True,
        description=_(u"dd/mm/yy HH:MM"),
    )

