"""Definition of the countdown content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from csci.countdown import countdownMessageFactory as _
from csci.countdown.interfaces import Icountdown
from csci.countdown.config import PROJECTNAME

countdownSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.LinesField(
        'tweetschedule',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"schedules tweets for today:"),
            description=_(u"Field description"),
        ),
    ),


    atapi.StringField(
        'target',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Target Date and Time"),
            description=_(u"dd/mm/yy HH:MM"),
        ),
        required=True,
        default=_(u"dd/mm/yy HH:MM"),
    ),


    atapi.TextField(
        'abovecount',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Text to include count down"),
            description=_(u"enter %daystogo% to include the days left"),
        ),
        required=True,
    ),

    atapi.StringField(
        'tuser',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Twitter Username"),
            description=_(u"username"),
        ),
    ),
        
    atapi.StringField(
        'tpass',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Twitter Password"),
            description=_(u"password"),
        ),
    ),

    atapi.BooleanField(
        'debugmode',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Debug mode"),
            description=_(u"debug mode to create schedule every time"),
        ),
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

countdownSchema['title'].storage = atapi.AnnotationStorage()
countdownSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(countdownSchema, moveDiscussion=False)

class countdown(base.ATCTContent):
    """Count down to a date"""
    implements(Icountdown)

    meta_type = "countdown"
    schema = countdownSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    tweetschedule = atapi.ATFieldProperty('tweetschedule')

    tpass = atapi.ATFieldProperty('tpass')

    tuser = atapi.ATFieldProperty('tuser')

    debugmode = atapi.ATFieldProperty('debugmode')

    abovecount = atapi.ATFieldProperty('abovecount')

    target = atapi.ATFieldProperty('target')


atapi.registerType(countdown, PROJECTNAME)
