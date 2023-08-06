### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 51890 2008-10-21 08:05:28Z cray $
"""
__author__  = ""
__license__ = "GPL"
__version__ = "$Revision: 51890 $"
 
from zope.interface import Interface

class IUseInterfaceWave(Interface) :
    """ InterfaceWave will be used on object having the interface """
                            
class IPropagateInterface(Interface) :
    """ Subinterfaces of the interface will be propagate on container items """
    