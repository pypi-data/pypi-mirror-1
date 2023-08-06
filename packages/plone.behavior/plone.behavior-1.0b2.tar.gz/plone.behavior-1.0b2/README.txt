==============
plone.behavior
==============

By Martin Aspeli

This package provides optional support for "behaviors". A behavior is 
essentially a conditionally available adapter.

For example, let's say that your application needs to support object-level
locking, and that this can be modelled via an adapter, but you want to leave
it until runtime to determine whether locking is enabled for a particular 
object. You could then register locking as a behavior.

Requirements
------------

This package comes with support for registering behaviors and factories. It
does not, however, implement the policy for determining what behaviors are
enabled on a particular object at a particular time. That decision is deferred
to an `IBehaviorAssignable` adapter, which you must implement.

The intention is that behavior assignment is generic across an application, 
used for multiple, optional behaviors. It probably doesn't make much sense to
use plone.behavior for a single type of behavior. The means to keep track
of which behaviors are enabled for what types of objects will be application
specific.

Usage
-----

A behavior is written much like an adapter, except that you don't specify
the type of context being adapted directly. For example::

    from zope.interface import Interface, implements

    class ILockingSupport(Interface):
       """Support locking
       """
   
       def lock():
           """Lock an object
           """
       
       def unlock():
           """Unlock an object
           """
       
    class LockingSupport(object):
        implements(ILockingSupport)
    
        def __init__(self, context):
            self.context = context
        
        def lock(self):
            # do something
    
        def unlock(self):
            # do something
 
This interface (which describes the type of behavior) and class (which
describes the implementation of the behavior) then need to be registered.
 
The simplest way to do that is to load the meta.zcml file from this package 
and use ZCML::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:plone="http://namespaces.plone.org/plone"
        i18n_domain="my.package">

        <include package="plone.behavior" file="meta.zcml" />
        
        <plone:behavior
            name="my.package.Locking"
            title="Locking support"
            description="Optional object-level locking"
            interface=".interfaces.ILockingSupport"
            factory=".locking.LockingSupport"
            />
    
    </configure>

After this is done - and presuming an appropriate IBehaviorAssignable adapter
exists for the context - you can adapt a context to ILockingSupport as 
normal::

    locking = ILockingSupport(context, None)

    if locking is not None:
        locking.lock()

You'll get an instance of LockingSupport if context can be adapted to 
IBehaviorAssignable (which, recall, is application specific), and if the
implementation of IBehaviorAssignable says that this context supports this
particular behavior.

Please see behavior.txt and directives.txt for more details.
