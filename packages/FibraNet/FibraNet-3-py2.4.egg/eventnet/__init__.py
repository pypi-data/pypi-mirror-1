"""

EventNet provides a generic, global dispatcher system for Event driven
systems.


= Posting Events =

To post an event, use:

eventnet.driver.post(event_name, **kw)

Any registered subscribers will be called with the event as the first
argument. An instance of an event has a name attribute, an args dictionary.
All keys in the args dictionary are also attributes of the instances.


= Handling Events with Functions =

To subscribe a function to an event, use the subscriber decorator.

@eventnet.driver.subscribe(event_name)
def event_handler(event):
    print event.name, event.args

A subscribed function has an unsubscribe method which will stop the function
from being called when subscribed event is posted.


= Handling Events with Classes =

A class which inherits from eventnet.driver.Subscriber can handle multiple
events.

class Handler(eventnet.driver.Subscriber):
    def EVT_Event(self, event):
        print event

    def EVT_SomeOtherEvent(self, event):
        print event


The above class defined two methods which are prefixed with 'EVT_'. This
prefix causes the class to automatically subscribe those methods to with the
event name which is taken from the remainder of the method name. Eg: the
method EVT_Event would be called whenever

eventnet.driver.post('Event')

is called.

To allow a class instance to start handling events, the capture method must
be called. To stop a class instance from handling events, the release method
must be called.

"""

import driver




if __name__ == "__main__":
    def test():
        class Handler(driver.Subscriber):
            def EVT_Event(self, event):
                print event

            def EVT_SomeOtherEvent(self, event):
                print event

        h = Handler()
        h.capture()
        driver.post('Event',a=1,b=2)
        h.release()
        driver.post('Event',a=1,b=2)
    test()
