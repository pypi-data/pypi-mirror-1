Orderable Objects
=================

Any container can be adapted to an ordering which guarantees that each
object within the container has a unique position.

    >>> root = getRootFolder()
    >>> from bebop.ordering.interfaces import IOrdering, IOrderable

Let's add some objects to the root folder:

    >>> import bop
    >>> bop.add.activate()
    
    >>> a = bop.add(root, 'a', bop.Folder())
    >>> b = bop.add(root, 'b', bop.Folder())
    >>> c = bop.add(root, 'c', bop.Folder())

    >>> sorted(root.keys())
    [u'a', u'b', u'c']

Each object has a corresponding position:

    >>> IOrdering(root).keys()
    [0, 1, 2]

You can also ask for the ordered names:

    >>> IOrdering(root).getNames()
    [u'a', u'b', u'c']

Positions can be changed with various methods. Here we use the moveTo method:

    >>> IOrdering(root).moveTo(0, 2)
    >>> IOrdering(root).getNames()
    [u'b', u'a', u'c']

The order of a named object can be accessed in various ways:

    >>> IOrderable(a).order
    1
    >>> IOrderable(b).order
    0
    >>> IOrderable(c).order
    2
    
    >>> IOrdering(root).order('a')
    1
    >>> IOrdering(root).order('b')
    0
    >>> IOrdering(root).order('c')
    2
    
A tricky problem is the adding of objects. If we want to know the new position
we must ask the IOrdering for the next available position:

    >>> IOrdering(root).next()
    3
    
The problem is that this should also work within the processing of the
ObjectAddedEvent:

    >>> from zope.app.container.interfaces import IObjectAddedEvent
    >>> def added(event):
    ...     if IObjectAddedEvent.providedBy(event):
    ...         obj = event.object
    ...         name = event.newName
    ...         ordering = IOrdering(event.newParent)
    ...         ordering.debug = True
    ...         print "IOrderable.order", IOrderable(obj).order
    ...         print "IOrdering.order", ordering.order(name)
   
    >>> import zope.event
    >>> zope.event.subscribers.append(added)
    
    >>> bop.add(root, 'd', bop.Folder())
    IOrderable.order 3
    IOrdering.order 3
    <zope.app.folder.folder.Folder object at ...>
    
    >>> bop.add(root, 'e', bop.Folder())
    IOrderable.order 4
    IOrdering.order 4
    <zope.app.folder.folder.Folder object at ...>
    
    >>> zope.event.subscribers.remove(added)

    