### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 52208 2008-12-26 10:29:24Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52208 $"

from zope.interface import Interface
from zope.viewlet import interfaces
from ng.skin.base.viewlet.viewletmain.interfaces import ICurrentBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import INewsListBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import ICommonNewsListBoxProvider
from ng.skin.base.viewlet.viewlettoolbox.interfaces import IToolBoxProvider

class IProjectBoxProvider(Interface):
    """ Interface for ProjectsBox provider """


class ISearchBoxProvider(Interface):
    """ Interface for ProjectsBox provider """


class ILeftColumn(IProjectBoxProvider,
                  ISearchBoxProvider,
                  ICurrentBoxProvider,
                  ICommonNewsListBoxProvider,
                  IToolBoxProvider,
                  interfaces.IViewletManager):
    """ ILeftColumn """
