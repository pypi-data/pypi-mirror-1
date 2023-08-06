### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: orderinformation.py 52840 2009-04-06 17:28:47Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52840 $"

from ng.lib.orderinformation import OrderInformation

class ContentOrderInformation(OrderInformation) :
    name = ["photo", "abstract", "contenticons", "body",   "backref",   "reference",  "comment", "content", ]

class ColumnOrderInformation(OrderInformation) :
    name = ["projectbox","currentbox","searchbox","newslistbox","toolbox"]    
                        