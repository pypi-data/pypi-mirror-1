### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Event Handler used to propagate container interface on his new content

$Id: interfacewave.py 51890 2008-10-21 08:05:28Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51890 $"

from interfaces import IPropagateInterface
from zope.app.container.interfaces import IContained
from zope.interface import alsoProvides, providedBy

def InterfaceWave(ob,event) :
    try :
        cont = IContained(ob).__parent__
    except TypeError :
        print "Can't propagate interface on not-IContent object"
    else :
        for interface in providedBy(cont) :
            if interface.extends(IPropagateInterface) :
                alsoProvides(ob, interface)
