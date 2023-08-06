from zope.component import adapts
from zope.interface import implements
from zope.location.interfaces import ILocation

from bebop.ordering.interfaces import IOrderable
from bebop.ordering.orderable import Orderable as DefaultOrderable
from bebop.protocol import protocol

from bop import annotation

from interfaces import IMarkedAsOrderable


class Orderable(DefaultOrderable):
    implements(IOrderable, ILocation)
    adapts(IMarkedAsOrderable)
    protocol.require(IOrderable, permission="zope.View")


OrderableFactory = annotation.factory(Orderable)