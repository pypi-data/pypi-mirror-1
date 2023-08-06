from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from csci.fourthplinth import fourthplinthMessageFactory as _

class Ifourthplinth(Interface):
    """Fourth Plinth"""
    
    # -*- schema definition goes here -*-
    debugmode = schema.Bool(
        title=_(u"Debug Mode"), 
        required=False,
        description=_(u"enter debug mode"),
    )

    tschedule = schema.Text(
        title=_(u"Generated schedule for today"), 
        required=False,
        description=_(u"Field description"),
    )

    tpassword = schema.TextLine(
        title=_(u"Twitter Password"), 
        required=True,
        description=_(u"Password"),
    )

    tusername = schema.TextLine(
        title=_(u"New Field"), 
        required=False,
        description=_(u"Field description"),
    )

