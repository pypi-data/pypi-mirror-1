# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

# A simple publisher/subscriber framework

class Subscriber:
    """A Subscriber subscribes to a Publishers event stream."""
    def notify(self, event, value):
        """This method must be overriden in a sub-class in order to receive
           events.
        """
        pass  

class Publisher:
    """Base-class for implementing a publisher."""
    def __init__(self):
        self.__subscribers = []

    def subscribe(self, subscriber):
        """Register a subscriber with a publisher."""
        if not isinstance(subscriber, Subscriber):
            raise TypeError('The subscriber is not of type Subscriber')

        self.__subscribers.append(subscriber)            

    def unsubscribe(self, subscriber):
        """Unregister a subscriber from a publisher."""
        self.__subscribers.remove(subscriber)

    def subscribers(self):
        return self.__subscribers
