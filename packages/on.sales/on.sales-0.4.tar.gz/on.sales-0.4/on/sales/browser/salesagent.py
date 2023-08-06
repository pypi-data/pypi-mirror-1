"""ngo.members - Plone product to manage
a sales organisation

Copyright (C) 2008 Oeko.neT <support@oeko.net>
"""

from Acquisition import aq_inner

from zope.component import getUtility

#from plone.memoize.instance import memoize

#from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from on.sales.interfaces import ISalesAgent
from on.sales import OnSalesMessageFactory as _
#from on.sales import config

class SalesAgentView(BrowserView):
    """Default view of a user folder
    """
    __call__ = ViewPageTemplateFile('salesagent.pt')


    
