"""Definition of the sales agent content type.
"""
from Acquisition import aq_inner, aq_base

from zope.interface import implements, directlyProvides
from zope.component import adapts

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName

from Products.Archetypes import atapi

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from on.sales.interfaces import ISalesAgentProxy, ISalesAgent
from on.sales.salesagent import SalesAgentSchema, SalesAgent, ResponsibleAgentFactory

from on.sales.config import PROJECTNAME

from on.sales import OnSalesMessageFactory as _

SalesAgentProxySchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField('id',
        required=True,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u"Id"),
                                  description=_(u"Unique ID Code"))
                      ),

    atapi.ReferenceField('real_salesagent',
        relationship='isResponsibleForArea',
        languageIndependent = 1,
        multiValued=False,
        storage=atapi.AnnotationStorage(),
        vocabulary_factory=u"on.sales.SalesAgents",
        vocabulary_display_path_bound=-1, # Avoid silly Archetypes object title magic
        widget=atapi.SelectionWidget(label=_(u"Sales Agent Proxy"),
                                          description=_(u"point to exactly one SalesAgent"),
                                          )
        ))
     )

finalizeATCTSchema(SalesAgentProxySchema, folderish=False, moveDiscussion=False)

class SalesAgentProxy(base.ATCTContent):
    """Display Sales Agent Information without having to get the real object
    """
    implements(ISalesAgentProxy)
    
    portal_type = "SalesAgentProxy"
    _at_rename_after_creation = True
    schema = SalesAgentProxySchema

    id = atapi.ATFieldProperty('id')
    real_salesagent = atapi.ATReferenceFieldProperty('real_salesagent')

def getAgent(self):
     """get the current agent's data"""
     context = aq_inner(self)
     agent = self.real_salesagent
     rv = dict(id = agent.id,
               name = agent.title,
               email = agent.email,
               phone = agent.phone,
               internal = agent.internal
               )
     return rv

atapi.registerType(SalesAgentProxy, PROJECTNAME)
