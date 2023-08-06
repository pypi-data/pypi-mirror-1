### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installRubricator script for the Zope 3 based ng.site.content.install
package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"


from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site
from zope.app.component.site import SiteManagementFolder

from ng.app.rubricator.newsref.newsrefbackreference.newsrefbackreference import NewsRefBackReference
from ng.app.rubricator.newsref.newsrefbackreference.interfaces import INewsRefBackReference

from ng.app.rubricator.rulesetevaluator.rulesetevaluator import Rulesetevaluator
from ng.app.rubricator.rulesetevaluator.interfaces import IRulesetevaluator

from ng.app.rubricator.rubricalgorithm.rubricalgorithm import RubricAlgorithm
from ng.app.rubricator.rubricalgorithm.interfaces import IRubricAlgorithm

from ng.site.content.search.interfaces import ISearch


def installRubricator(context, **kw):
    """ Устанавливает NewsRefBackReference, RubricAlgorithm, Rulesetevaluator
    """
    sm = context.getSiteManager()
    rubricator = sm[u'rubricator'] = SiteManagementFolder()

    
    nrbr = NewsRefBackReference()
    nrbr.newsRefId = u'intid'
    rubricator[u'NewsRefBackReference'] = nrbr
    
    sm.registerUtility(rubricator['NewsRefBackReference'], provided=INewsRefBackReference, name='newsrefbackreference')

    rubricator[u'Rulesetevaluator'] = Rulesetevaluator()
    sm.registerUtility(rubricator[u'Rulesetevaluator'], provided=IRulesetevaluator, name=u'rulesetevaluator')

    ra = RubricAlgorithm()
    ra.backreference = u'newsrefbackreference'
    ra.newsRefId = u'intid'
    ra.rootRubricPath = u'/' + context.__name__ + u'/rubricator'
    ra.rulesetEvaluator = u'rulesetevaluator'
    ra.interface = ISearch
    rubricator[u'RubricAlgorithm'] = ra
    sm.registerUtility(rubricator[u'RubricAlgorithm'], provided=IRubricAlgorithm)

    return "Success"
