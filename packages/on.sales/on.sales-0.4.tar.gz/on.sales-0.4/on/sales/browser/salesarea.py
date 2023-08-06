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

from on.sales.interfaces import ISalesArea
from on.sales import OnSalesMessageFactory as _
#from on.sales import config
import salesmail

class SalesAreaView(BrowserView):
    """Default view of a user folder
    """
    __call__ = ViewPageTemplateFile('salesarea.pt')

    def listOneFolder(self):
        """ Martin Aspeli:
            http://plone.org/documentation/tutorial/richdocument/folder-listings
        """
        catalog = getToolByName(self, 'portal_catalog')
        results = catalog.searchResults(path = {'query' : '/'.join(self.getPhysicalPath()),
                                                'depth' : 1 },
                                        sort_on = 'getObjPositionInParent',
                                        )
        return results

    def listAreas1(self, depth = 0): #, area = self):
        """get the areas which are contained in the current area so that
           we can display them
        """
        # [ (1, obj1), (2, obj2), (3, obj3) ]
        areas = PortalFolderBase.contentItems(self.context)
        # debugging only:
        prefix = depth * "  "
        for i in range(len(areas)):
            # print "%slistAreas(%d): %d" % (prefix, depth, i)
            area = areas[i][1]
            # print "%s  area = %s" % (prefix, str(area))
            if depth < 2:
                subareas = area.listAreas(depth = depth + 1)
            #    print "%s  subareas = %s" % (prefix, str(subareas))
        return str(areas)






