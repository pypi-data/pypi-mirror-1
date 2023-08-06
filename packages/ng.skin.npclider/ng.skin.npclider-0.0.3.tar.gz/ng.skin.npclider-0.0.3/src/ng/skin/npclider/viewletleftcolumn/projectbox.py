### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Mix-in class for viewlet with project box

$Id: projectbox.py 52320 2009-01-13 12:58:18Z corbeau $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52320 $"

from zope.app.zapi import getUtility, absoluteURL
from zope.app.container.interfaces import IContainer
from ng.content.article.article.interfaces import IArticle
from ng.skin.base.viewlet.viewletmain.mainbox import MainBox

class ProjectBox(MainBox) :
    """ Project box
    """
    
    foldername = "projects"
    folderinterface = IContainer
