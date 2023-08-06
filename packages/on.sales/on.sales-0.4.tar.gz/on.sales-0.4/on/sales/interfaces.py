from zope.interface import Interface
from zope import schema
# import plone.Archetypes

from Products.Archetypes.atapi import *

# from zope.app.container.constraints import contains

from on.sales import OnSalesMessageFactory as _



class ISalesAgent(Interface):
    """Data Sheet of a sales agent"""

    id = schema.TextLine(title = _(u"Id"),
                            required = True)

    #portrait = schema.ImageWidget(title = _(u"Portrait"),
    #                             required = False)

    email = schema.TextLine(title = _(u"Email"),
                               required = True)

    title = schema.TextLine(title=_(u"Sales Agent Name"),
                            required=True)

    department = schema.TextLine(title = _(u"Department"),
                              required = False)

    phone = schema.TextLine(title = _(u"Phone number"),
                              required = False)

    internal = schema.Bool(title = _(u"Internal"),
                              required = False)

    notes = schema.SourceText(title = _(u"Notes"))


class ISalesAgentProxy(Interface):
    """Data Sheet of a sales agent proxy

       We should compute all of these values, except for the one value
       of the referenced SalesAgent. The other values should be filled
       in automatically, and be kept in sync via events.
    """

    real_salesagent = schema.List(title=_(u"Sales Agent"),
                                         description=_(u"The real sales agent"),
                                         value_type=schema.Object(title=_(u"Sales Agent"),
                                                                  schema=ISalesAgent)
                                  )

    id = schema.TextLine(title = _(u"Id"),
                            required = True)


class ISalesArea(Interface):
    """Data sheet of sales area"""

