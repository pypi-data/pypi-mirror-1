"""Definition of the sales agent content type.
"""
from Acquisition import aq_inner, aq_base

from zope.interface import implements
from zope.component import adapts

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

from Products.Archetypes.interfaces import IObjectPostValidation

from Products.Archetypes import atapi

from Products.ATContentTypes.content import schemata, folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from on.sales.interfaces import ISalesArea
from on.sales.config import PROJECTNAME
from on.sales.salesagentproxy import getAgent 
from on.sales import OnSalesMessageFactory as _

SalesAreaSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.ImageField('map',
        required=False,
        searchable=False,
        pil_quality = 95,
        languageIndependent = 1,
        widget=atapi.ImageWidget(label=_(u"Map"),
                                  description=_(u"Area of Responsibility")),
        max_size = (658, 500),
        sizes = { 'mini' : (80,80), 'normal' : (200,150) },
    )
))

SalesAreaSchema['title'].storage = atapi.AnnotationStorage()
SalesAreaSchema['title'].widget.label = _(u"Name")
SalesAreaSchema['title'].widget.description = _(u"")

SalesAreaSchema['description'].storage = atapi.AnnotationStorage()
SalesAreaSchema['description'].widget.label = _(u"Description")
SalesAreaSchema['description'].widget.description = _(u"")

finalizeATCTSchema(SalesAreaSchema, folderish=True, moveDiscussion=False)

class SalesArea(folder.ATFolder):
    """Display Sales Area. This content type is folderish in that it may
       contain other (=smaller) regions.
    """
    implements(ISalesArea)
    
    portal_type = "SalesArea"
    _at_rename_after_creation = True
    schema = SalesAreaSchema

    name = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')


    def getAreaDetails(self, level):
        return str(self)


    def getSalesAreaTree(self, level = 0, maxdepth = 3):
        """Create a tree of all sales areas below this view's area up to
           a depth of 'maxdepth' in a hierarchical list.

           This method is called on a SalesArea object.

           This method returns a string which is then plugged into the
           template via 'structure'.
        """
        # get content objects of a folder: folder.objectValues(['SalesArea'])
        # taken from the mailing list Wed, 20 Aug 2008 10:24:48 +0200
        # <200808201024.48631.andrija.prcic@gmail.com>

        result = []
        brains = self.getFolderContents(contentFilter={'meta_type':['SalesArea']}, full_objects=True)

        for b in brains:
            area = { 'id': b.getId(),
                     'level': level,
                     'title': b.Title(),
                     'map': b.getMap(),
                     'descr': b.Description(),
                     'api': dir(b),
                     #'rsa': b.getResponsible_salesagent()
                     }
            s = b.getSalesAreaTree(level + 1, maxdepth)
            area['view'] = ''
            area['sons'] = None
            if s:
                area['sons'] = s
            result.append(area)

        return result

        #b_areas = [(b.getObject().UID(), str(b.Title or b.getId)[:70]) for b in brains]

    def getSalesAreaTreeAsString(self, level = 0, maxdepth = 2):
        return str(self.getSalesAreaTree(level, maxdepth))

    def getSalesAgents(self):
        """get all SalesAgent proxy objects contained in the Sales area 

           This method is called on a SalesArea object.

           This method returns a string which is then plugged into the
           template via 'structure'.
        """
        # Sales agents  must be of type 'SalesAgentProxy':
        # get content objects of a folder: folder.objectValues(['SalesAgentProxy'])
        # taken from the mailing list Wed, 20 Aug 2008 10:24:48 +0200
        # <200808201024.48631.andrija.prcic@gmail.com>

        result = []
        l = 0
        brains = self.getFolderContents(contentFilter={'meta_type':['SalesAgentProxy']},
                                        full_objects=True)
        for b in brains:
            agent = {'id': b.getId(),
                     'name': b.Title(),
                     'descr': b.Description(),
                         }
            ab = getAgent(b)

            # first, we look for external available staff to show in the page
            agent['internal'] = ab['internal']
            if agent['internal'] == False:
                result.append(agent)
        l = len(result)
        if l == 0:
            try:
                result.append(agent)
            except:
                pass
        return result
        

    def haveSalesAgent(self):
        return len(self.getSalesAgents()) > 0

        

atapi.registerType(SalesArea, PROJECTNAME)


def getMaillist(agents):
    """get the mail addresses of the responsible sales agents
    and collect them in a list. We first have to get the IDs of the "real" sales agents
    and from these we can get the mail addresses
    """
    mailaddresses = []
    for i in agents:
        a = getAgent(i)
        ma = a['email']
        mailaddresses.append(ma)

    return  mailaddresses

def mailaddresses(self):

    """
       if there are any sales agents assigned to the district, call
       getMaillist to get their mail addresses, otherwise get the mail
       addresses of the surrounding area
    """
    area = self.context
    agents = self.getFolderContents(contentFilter={'meta_type':['SalesAgentProxy']}, full_objects=True)
    
    while len(agents) == 0:
        try:
            area = area.aq_inner.aq_parent # check for type "SalesArea"...
        except:
            raise ValueError, _("top area has no sales agents")

    to_addresses = getMaillist(agents)
    return to_addresses
        
