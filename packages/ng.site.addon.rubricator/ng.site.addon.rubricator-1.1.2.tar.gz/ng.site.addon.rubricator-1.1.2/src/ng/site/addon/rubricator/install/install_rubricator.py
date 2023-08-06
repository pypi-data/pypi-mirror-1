### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installRubricator script for the Zope 3 based ng.site.content.install
package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.component.site import SiteManagementFolder

from ng.app.link.linkbackreference.linkbackreference import LinkBackReference 
from ng.app.link.linkbackreference.interfaces import ILinkBackReference

def install_LinkBackReference(context, **kw) :
    """ Install reverse reference index """

    sm = context.getSiteManager()
    rubricator = sm[u'rubricator'] = SiteManagementFolder()
    lbr = rubricator[u'LinkBackReference'] = LinkBackReference()
    lbr.newsRefId = u'intid'
    
    sm.registerUtility(lbr, provided=ILinkBackReference)

