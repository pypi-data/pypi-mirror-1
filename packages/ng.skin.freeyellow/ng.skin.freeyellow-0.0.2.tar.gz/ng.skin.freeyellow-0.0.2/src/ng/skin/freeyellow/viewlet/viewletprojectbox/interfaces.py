### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The definitions of a few viewlet provider.

$Id: interfaces.py 52839 2009-04-06 17:03:12Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52839 $"

from zope.interface import Interface

class IProjectBoxProvider(Interface):
    """ Interface for ProjectsBox provider """
