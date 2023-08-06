"""on.sales - Plone product to fulfill requirements
of a middle-sized Sales Management

Copyright (C) 2008 Oeko.neT <support@oeko.net>
"""

from zope.i18nmessageid import MessageFactory
from on.sales import config

from Products.Archetypes import atapi
from Products.CMFCore import utils

OnSalesMessageFactory = MessageFactory('on.sales')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    import salesagent
    import salesarea
    import salesagentproxy
    
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Now initialize all these content types.

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)    

