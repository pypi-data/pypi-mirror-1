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

Uility  intidsvocabulary
------------------------

This is vocabulary on IIntIds utilities using of some our products.
