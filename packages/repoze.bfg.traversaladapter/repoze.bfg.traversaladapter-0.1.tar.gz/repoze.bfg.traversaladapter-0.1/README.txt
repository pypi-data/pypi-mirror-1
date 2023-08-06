repoze.bfg.traversaladapter
===========================

An alternate implementation of the
``repoze.bfg.interfaces.ITraverserFactory`` (a "traverser") which
allows you to register an adapter factory for the type or interface(s) of
objects encountered during traversal. This is a generalization of the
``repoze.bfg.traversalwrapper`` package which automatically wraps each
traversed object into a location-aware proxy.

To enable this custom traverser factory, you need to add a dependency on
``repoze.bfg.traversaladapter`` to your application and replace the default
traverser factory in the ``configure.zcml`` configuration file like this: ::

    <adapter
        factory="repoze.bfg.traversaladapter.ModelGraphTraverser"
        provides="repoze.bfg.interfaces.ITraverserFactory"
        for="*"
        />

Given a simple factory for adapters for a model class ``mymodule.Foo``
defined in the module ``mymodule`` like this ::

def foo_factory(foo, parent, name):
    return FooAdapter(foo, parent, name)

you could then register ``foo_factory`` as a traversal adapter factory as
follows: ::

    <adapter
        factory="mymodule.foo_factory"
        provides="repoze.bfg.traversaladapter.ITraversalAdapterFactory"
        for="mymodule.Foo"
        />

If ``Foo`` was implementing the interface ``mymodule.IFoo``, the following
registration would also work: ::

    <adapter
        factory="mymodule.foo_factory"
        provides="repoze.bfg.traversaladapter.ITraversalAdapterFactory"
        for="mymodule.IFoo"
        />

During traversal of your ``repoze.bfg`` application, each object of type
``Foo`` will then automatically be wrapped in a ``FooAdapter`` instance.

Note that the registered factory always gets the current model object, its
parent and its name passed as arguments. If your ``FooAdapter`` class was set
up to receive a ``Foo`` instance, a parent object, and a name string in its
constructor like so ::

class FooAdapter(object):
    def __init__(self, foo, parent, name):
        self.foo = foo
        self.parent = parent
        self.name = name

you could register the adapter class itself as the adapter factory.

See the ``repoze.bfg.traversaladapter.tests.TraversalAdapterTests`` 
module for further examples.
