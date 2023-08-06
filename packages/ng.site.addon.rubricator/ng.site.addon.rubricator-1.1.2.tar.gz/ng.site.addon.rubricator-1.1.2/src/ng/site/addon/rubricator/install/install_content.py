### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installAbout, installArticles, installMirrors, installNews, installRubric
and installRubrics scripts for the Zope 3 based ng.site.content.install package

$Id: product.py 49265 2008-01-08 12:18:26Z cray $
"""
__author__  = "Yegor Shershnev, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49265 $"

from zope.app.folder.folder import Folder

from zope.app.component.hooks import setSite
from zope.app.component import site

from ng.content.article.division.division import Division
from ng.content.article.article.article import Article
from ng.app.objectqueue.interfaces import IObjectQueueAnnotation
from zope.app.container.interfaces import IContainer

def install_Rubric(context, **kw):
    """ Создаёт раздел Rubricator
    """
    rubricator = context[u'rubricator'] = Division()
    rubricator.title = kw['rubricator']
    rubricator.abstract = kw['rubricator_abstract']
    rubricator.author = kw['author']
    IObjectQueueAnnotation(rubricator).use = True
    IObjectQueueAnnotation(rubricator).islast = False

    return "Success"

#def install_Rubrics(context, **kw) :
#    rubrics = kw['rubrics']
#    
#    for rubric in rubrics :
#       division = Division()
#       division.title = rubric.title
#       division.abstract = rubric.abstract
#       division.author = kw['author']
#       context[rubric.name] = division
#       IObjectQueueAnnotation(division).use = True
#       IObjectQueueAnnotation(division).islast = False
#
#    return "Success"
