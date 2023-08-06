Short description ng.utility package
====================================

Package developed to be a library of small, but useful
utilits, channels and other components for use in different
dark purpose.

Channel objecteventchannel 
--------------------------

Some events (IIntIdAddedEvent, IIntIdRemovedEvent) is, in sense,
events of component life cicle, is not such structurally.
Event content attribute with value equal object of event, 
but event is not send as pair (event, object) and event handler
must processing all event and do test on interface providing.

This channel receive such events and re-emits them as pair
(event, object), It do possibile to declare handlers with
events for defined kind of object.

Utility intidsvocabulary
------------------------

This is vocabulary on IIntIds utilities using of some our products.

Package interfacewave 
---------------------
This package components catch event emited by object with interface
**IUserInterfaceWave** on creating and asign new object all interfaces from
its parent if them extent **IPropagateInterface** interface.

Hierarhy of object with dynamic interfaces such as their parents can be
created simple by this way.
