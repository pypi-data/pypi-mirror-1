# -*- coding: utf-8 -*-
"""The object event channel

$Id: objecteventchannel.py 457 2007-01-19 03:55:29Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 457 $"
__date__ = "$Date: 2007-01-19 06:55:29 +0300 (Птн, 19 Янв 2007) $"
__credits__ = """Andrey Orlov, for idea and common control"""

from zope.interface import implements
from zope.event import subscribers

def objectEventChannel(event) :
    #notify(event.object,event)
    #notify is misdeclared as one-argument function and we are to use
    #its content to call all dispatcher 
    for dispatch in subscribers :
        dispatch(event.object,event)