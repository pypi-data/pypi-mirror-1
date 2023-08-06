largeblue.order allows you to adapt ''selected'' containers and objects 
to make the container's contents orderable.  It build on and patches 
bebop.ordering, the source code and dependencies of which are included 
here (because it's not available as a standalone egg on the pypi or 
via iwm-kmrc.de).  

(Note that the bebop code is all (c) iwm-kmrc.de and is released under 
GPL).

The original bebop implementation makes all containers ordering and 
all content objects orderable.  This package re-configures the 
underlying ordering machinery, so you can adapt specific containers 
and specific objects to make the ordering and orderable.

This way you can choose, say, which objects that are contained within 
a container should be orderable.  Plus you can choose which containers 
to hang this functionality off explicitly. I should note also that the 
view that this package hangs off the container also includes the 
default container view functionality of add, delete, rename, etc.

To use it, include largeblue.order in your project dependencies, adapt 
container(s) to say they implement 
largeblue.order.interfaces.IMarkedAsOrdering and adapt the objects you 
want to order to say they implement 
largeblue.order.interfaces.IMarkedAsOrderable.

Then go to http://...path/to/my_container/@@orderable_contents.html  

For an example usage, see `largeblue.pages <http://pypi.python.org/pypi/largeblue.pages>`_).