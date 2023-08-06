from zope.annotation.interfaces import IAnnotatable

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")


class IMarkedAsOrdering(IAnnotatable):
    """
      Marker interface containers can implement to
      allow their contents to be ordered.
      
      
    """


class IMarkedAsOrderable(IAnnotatable):
    """
      Marker interface objects need to implement to
      be ordered.
      
      
    """

