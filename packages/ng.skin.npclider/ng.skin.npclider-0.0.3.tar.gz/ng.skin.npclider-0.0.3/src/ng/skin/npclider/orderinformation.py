### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: orderinformation.py 52414 2009-01-30 12:53:58Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52414 $"

from ng.lib.orderinformation import OrderInformation

class ContentOrderInformation(OrderInformation) :
    name = ["abstract", "body", "photo",   "backref",  "contenticons", "reference",  "comment", "content", ]

class ColumnOrderInformation(OrderInformation) :
    name = ["currentbox","projectbox","searchbox","newslistbox","toolbox"]    
                        