#Copyright (c) 2006 Simon Wittber
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation files
#(the "Software"), to deal in the Software without restriction,
#including without limitation the rights to use, copy, modify, merge,
#publish, distribute, sublicense, and/or sell copies of the Software,
#and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

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

To subscribe a function to an event, use the subscriber decorator. If the 
event has arg1 and arg2 attributes, they will be passed to the function. The 
function signature need only specify the event attributes it needs.

@eventnet.driver.subscribe(event_name)
def event_handler(arg1, arg2):
    print arg1, arg2

A subscribed function has a release method which will stop the function
from being called when subscribed event is posted.


= Handling Events with Classes =

A class which inherits from eventnet.driver.Subscriber can handle multiple
events.

class Handler(eventnet.driver.Subscriber):
    def EVT_Event(self, arg1, arg2):
        print arg1, arg2

    def EVT_SomeOtherEvent(self, arg1):
        print arg1


The above class defined two methods which are prefixed with 'EVT_'. This
prefix causes the class to automatically subscribe those methods to with the
event name which is taken from the remainder of the method name. Eg: the
method EVT_Event would be called whenever

eventnet.driver.post('Event', arg1=1, arg2=2, arg3=3)

is called. Only the arguments in the method signature are supplied, the 
method need not handle all potential event attributes.

To allow a class instance to start handling events, the capture method must
be called. To stop a class instance from handling events, the release method
must be called.

"""

import driver



