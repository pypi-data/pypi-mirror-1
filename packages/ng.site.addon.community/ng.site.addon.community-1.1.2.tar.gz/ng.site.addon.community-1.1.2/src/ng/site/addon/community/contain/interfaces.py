### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 52221 2008-12-27 15:01:41Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52221 $"
 

from zope.schema import Field
from zope.interface import Interface
from ng.lib.containconstraint import ContainConstraint

class IDenyContainCommunity_(Interface) :
    """ """

class IDenyContainCommunity(IDenyContainCommunity_) :
    __parent__ = Field(constraint = ContainConstraint(IDenyContainCommunity_).deny)
    
    