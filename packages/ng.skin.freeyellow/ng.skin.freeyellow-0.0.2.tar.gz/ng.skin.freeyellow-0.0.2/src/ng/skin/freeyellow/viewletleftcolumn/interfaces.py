### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 52839 2009-04-06 17:03:12Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52839 $"

from zope.interface import Interface
from zope.viewlet import interfaces
from ng.skin.base.viewlet.viewletmain.interfaces import ICurrentBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import INewsListBoxProvider
from ng.skin.base.viewlet.viewletmain.interfaces import ICommonNewsListBoxProvider
from ng.skin.base.viewlet.viewlettoolbox.interfaces import IToolBoxProvider
from ng.skin.freeyellow.viewlet.viewletsearchbox.interfaces import ISearchBoxProvider
from ng.skin.freeyellow.viewlet.viewletprojectbox.interfaces import IProjectBoxProvider



class ILeftColumn(IProjectBoxProvider,
                  ISearchBoxProvider,
                  ICurrentBoxProvider,
                  ICommonNewsListBoxProvider,
                  IToolBoxProvider,
                  interfaces.IViewletManager):
    """ ILeftColumn """
