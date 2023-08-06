### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The object event channel

$Id: objecteventchannel.py 51890 2008-10-21 08:05:28Z cray $
"""
__author__  = "Andrey Orlov 2006 12 05"
__license__ = "GPL"
__version__ = "$Revision: 51890 $"

from zope.interface import implements
from zope.event import subscribers

def objectEventChannel(event) :
    #notify(event.object,event)
    #notify is misdeclared as one-argument function and we are to use
    #its content to call all dispatcher 
    for dispatch in subscribers :
        dispatch(event.object,event)
        