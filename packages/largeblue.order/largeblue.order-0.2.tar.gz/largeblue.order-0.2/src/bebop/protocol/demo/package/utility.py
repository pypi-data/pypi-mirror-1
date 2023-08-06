#A module that uses the utility protocol
import zope.interface
from zope.component.interfaces import IFactory

from bebop.protocol import protocol

import interfaces

class SampleUtility(object):
    zope.interface.implements(interfaces.ISampleUtility)
    
protocol.utility(factory=SampleUtility)

class SampleComponentUtility(object):
    zope.interface.implements(interfaces.ISampleComponentUtility)
    
# If we want to specify a variable that can be loaded from a module we
# have to specify the name of the variable
sampleComponent = SampleComponentUtility()
protocol.utility(component=sampleComponent, variable='sampleComponent')

# Most of the time we will register classes as utilities or factories
# in this case we can use the class object directly, since it
# can be converted into a dotted name easily
protocol.utility(component=SampleComponentUtility, provides=IFactory)


class SampleNamedUtility(object):
    zope.interface.implements(interfaces.INamedSampleUtility)
    
protocol.utility(factory=SampleNamedUtility, name='demo', permission='zope.View')

