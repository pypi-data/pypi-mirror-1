"""ngo.members - Plone product to manage
a sales organisation

Copyright (C) 2008 Oeko.neT <support@oeko.net>
"""

import cgi
from Acquisition import aq_inner

from zope.component import getUtility

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from on.sales.interfaces import ISalesAgentProxy
from on.sales import OnSalesMessageFactory as _
#from on.sales import config
import salesmail

class SalesAgentProxyView(BrowserView):
    """Default view of a user folder
    """
    __call__ = ViewPageTemplateFile('salesagentproxy.pt')

    @memoize
    def getAgent(self):
        """get the current agent's data"""
        context = aq_inner(self.context)
        agent = context.real_salesagent
        
        rv = dict(name = agent.title,
                  email = agent.email,
                  department = agent.department,
                  phone = agent.phone,
                  notes = agent.notes,
                  internal = agent.internal
                  )
        try:
            rv['portrait'] = agent.portrait
        except:
            pass

        return rv




