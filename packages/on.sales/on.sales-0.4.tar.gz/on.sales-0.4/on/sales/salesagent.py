"""Definition of the sales agent content type.
"""
import re

from zope.interface import implements, directlyProvides
from zope.component import adapts

from zope import schema

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName

from Products.Archetypes import atapi

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from on.sales.interfaces import ISalesAgent
from on.sales.config import PROJECTNAME

from on.sales import OnSalesMessageFactory as _

""" Define a valiation method for email addresses
    taken from optilux-code
"""
class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")

check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match
def validate_email(value):
    if not check_email(value):
        raise NotAnEmailAddress(value)
    return True



class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")


SalesAgentSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField('id',
        required=True,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u"Id"),
                                  description=_(u"Unique ID Code"))
                      ),

    atapi.ImageField('portrait',
        required=False,
        languageIndependent = 1,
        searchable=False,
        max_size = (300,500),
        sizes = {'large': (262,360),
                 'standard': (131,180),
                 'small': (97,128) },
        widget=atapi.ImageWidget(label=_(u"Portrait"),
                                 description=_(u"Portrait of Sales Agent"),
                                 show_content_type = False)
                          ),

    atapi.StringField('email',
        required=True,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u"Email"),
                                  description=_(u"Email Address")),
        constraint=validate_email
                          ),

    atapi.StringField('department',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u"Department"),
                                  description=_(u"The department the sales person is organized in"))
                      ),
    
    atapi.StringField('phone',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u"Phone number"),
                                  description=_(u"Office phone number"))
                      ),

    atapi.BooleanField('internal',
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(label=_(u"Internal only"),
                                  description=_(u"wether to show this salesagent publically")),
        default = False,
                      ),

    atapi.TextField('notes',
        required=False,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        validators=('isTidyHtmlWithCleanup',),
        widget=atapi.RichWidget(label=_(u"Additional information"),
                                rows=25,
                                allow_file_upload=False)
                    )
    ))

SalesAgentSchema['title'].storage = atapi.AnnotationStorage()
SalesAgentSchema['title'].widget.label = _(u"Name")
SalesAgentSchema['title'].widget.description = _(u"")

SalesAgentSchema['description'].storage = atapi.AnnotationStorage()
SalesAgentSchema['description'].widget.label = _(u"Info")
SalesAgentSchema['description'].widget.description = _(u"")

finalizeATCTSchema(SalesAgentSchema, folderish=False, moveDiscussion=False)

class SalesAgent(base.ATCTContent):
    """Display Sales Agent Information.
    """
    implements(ISalesAgent)
    
    portal_type = "SalesAgent"
    _at_rename_after_creation = True
    schema = SalesAgentSchema
    
    title = atapi.ATFieldProperty('title')
    id = atapi.ATFieldProperty('id')
    email = atapi.ATFieldProperty('email')
    department =  atapi.ATFieldProperty('department')
    phone = atapi.ATFieldProperty('phone')
    internal = atapi.ATFieldProperty('internal')
    notes =  atapi.ATFieldProperty('notes')

atapi.registerType(SalesAgent, PROJECTNAME)

def ResponsibleAgentFactory(context):
    """Vocabulary factory for sales agents
    """
    catalog = getToolByName(context, 'portal_catalog')
    items = [(r.Title, r.UID) for r in 
                catalog(object_provides=ISalesAgent.__identifier__,
                        review_state="published",
                        sort_on='sortable_title')]

    # This turns a list of title->id pairs into a Zope 3 style vocabulary
    return SimpleVocabulary.fromItems(items)
directlyProvides(ResponsibleAgentFactory, IVocabularyFactory)

