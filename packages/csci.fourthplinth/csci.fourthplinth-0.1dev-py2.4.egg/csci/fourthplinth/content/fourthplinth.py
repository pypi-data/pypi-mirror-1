"""Definition of the fourthplinth content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from csci.fourthplinth import fourthplinthMessageFactory as _
from csci.fourthplinth.interfaces import Ifourthplinth
from csci.fourthplinth.config import PROJECTNAME

fourthplinthSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.BooleanField(
        'debugmode',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Debug Mode"),
            description=_(u"enter debug mode"),
        ),
    ),


    atapi.LinesField(
        'tschedule',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"Posts to schedule"),
            description=_(u"Enter: Date, Time, Tweet use new line for each entry"),
            rows=20,
            columns=30,
        ),
    ),


    atapi.StringField(
        'tpassword',
        storage=atapi.AnnotationStorage(),
        widget=atapi.PasswordWidget(
            label=_(u"Twitter Password"),
            description=_(u"Password"),
        ),
        required=True,
    ),


    atapi.StringField(
        'tusername',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"New Field"),
            description=_(u"Field description"),
        ),
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

fourthplinthSchema['title'].storage = atapi.AnnotationStorage()
fourthplinthSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(fourthplinthSchema, moveDiscussion=False)

class fourthplinth(base.ATCTContent):
    """Fourth Plinth"""
    implements(Ifourthplinth)

    meta_type = "fourthplinth"
    schema = fourthplinthSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    debugmode = atapi.ATFieldProperty('debugmode')

    tschedule = atapi.ATFieldProperty('tschedule')

    tpassword = atapi.ATFieldProperty('tpassword')

    tusername = atapi.ATFieldProperty('tusername')


atapi.registerType(fourthplinth, PROJECTNAME)
