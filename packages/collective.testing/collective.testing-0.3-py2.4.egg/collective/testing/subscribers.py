from cStringIO import StringIO

from zope.interface import Interface

class EventPrinter(object):
    _event_filter=Interface
    _interface=Interface

    def __init__(self, buffer):
        self.buffer = buffer
        
    def channelPrinter(self, obj, event):
        if self._interface.providedBy(obj) or self._event_filter.providedBy(event):
            print >> self.buffer, "%s.%s :: %s %s" %(event.__module__, event.__class__.__name__, obj, obj.getId())

    def eventPrinter(self, event):
        if self._event_filter.providedBy(event):
            print >> self.buffer, "%s.%s" %(event.__module__, event.__class__.__name__)

# default is standard out
import sys
_ep = EventPrinter(sys.stdout)

eventPrinter = _ep.eventPrinter
channelPrinter = _ep.channelPrinter

class Null(Interface):
    """ nothing """

def setFilter(interface=Null, event=Null, reset=False):
    if reset:
        setFilter(Interface, Interface)
    _ep._event_filter = event
    _ep._interface = interface

def setBuffer(buffer):
    oldbuffer = _ep.buffer
    _ep.buffer = buffer
    return oldbuffer

def load_eventprint():
    from Products.Five import zcml
    from collective import testing
    zcml.load_config('printevent.zcml', testing)
