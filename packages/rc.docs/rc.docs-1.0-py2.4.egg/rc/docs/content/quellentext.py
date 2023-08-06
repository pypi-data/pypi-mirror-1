"""Definition of the Quellentext content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from rc.docs import docsMessageFactory as _
from rc.docs.interfaces import IQuellentext
from rc.docs.config import PROJECTNAME

QuellentextSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

# QuellentextSchema = BaseSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'fundort',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Fundort"),
            description=_(u"ID oder String"),
        ),
        required=False,
    ),


    atapi.StringField(
        'druckort',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Druckort"),
            description=_(u"ID oder String"),
        ),
        required=False,
    ),

    atapi.TextField(
        'regest',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Regest"),
            description=_(u"Kurzbeschreibung eingeben."),
        ),
        default_output_type='text/html',
        searchable=1,
    ),


    atapi.TextField(
        'originaltext',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Originaltext"),
            description=_(u"Text erfassen."),
        ),
        default_output_type='text/html',
        searchable=1,
    ),

    atapi.TextField(
        'kommentar',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Kommentar"),
            description=_(u"Kommentare zum Artikel eingeben."),
        ),
        default_output_type='text/html',
        searchable=1,
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

QuellentextSchema['title'].storage = atapi.AnnotationStorage()
QuellentextSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(QuellentextSchema, moveDiscussion=False)

# Hide the 'description' field
QuellentextSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

class Quellentext(base.ATCTContent):
    """Quellentext zum Projekt einfügen"""
    implements(IQuellentext)

    meta_type = "Quellentext"
    schema = QuellentextSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    fundort = atapi.ATFieldProperty('fundort')
    druckort = atapi.ATFieldProperty('druckort')
    regest = atapi.ATFieldProperty('regest')
    originaltext = atapi.ATFieldProperty('originaltext')
    kommentar = atapi.ATFieldProperty('kommentar')

atapi.registerType(Quellentext, PROJECTNAME)
