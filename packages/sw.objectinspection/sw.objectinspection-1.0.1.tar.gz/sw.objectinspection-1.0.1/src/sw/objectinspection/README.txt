===================
sw.objectinspection
===================

ObjectInspection is a tool, that provides you with a generic API to inspect
objects for their attributes and their children objects. It comes with two
basic inspectors (`BasicAttributesInspector` and `BasicChildrenInspector`)
which can be easily replaced with your own inspectors.


Setup
=====

Create some objects, which are inspected later on:

    >>> class Child1(object):
    ...     pass
    >>> class Child2(object):
    ...     pass
    >>> class Child3(object):
    ...     pass
    >>> class Child4(object):
    ...     misc = Child1()
    >>> class ToInspect(object):
    ...     some_var = ["some tupel", (Child2(), Child3())]
    ...     other_var = {"foo": "bar"}
    ...     _private_var = 10
    ...     desc = Child4()
    ...
    ...     def some_method(self):
    ...         pass


Inspecting for attributes
=========================

Get the `AttributesInspector` by adapting to `IAttributesInspector`:

    >>> from sw.objectinspection import IAttributesInspector
    >>> inspector = IAttributesInspector(ToInspect())

Because there is no specialized inspector for the `ToInspect` object registered,
the `BasicAttributesInspector` is used:

    >>> inspector
    <sw.objectinspection.BasicAttributesInspector object at 0x11f69d0
     used for ToInspect object at 0x11f6910>

To start the inspection, simply call the inspector:

    >>> inspector()
    ['desc', 'other_var', 'some_var']


Inspecting for children
=======================

Inspection for children works the same way like inspection for attributes:

    >>> from sw.objectinspection import IChildrenInspector
    >>> inspector = IChildrenInspector(ToInspect())

    >>> inspector
    <sw.objectinspection.BasicChildrenInspector object at 0x11f6a10
     used for ToInspect object at 0x11f6910>

    >>> sorted(inspector())
    [<Child2 object at 0x119cc10>,
     <Child3 object at 0x11f5790>,
     <Child4 object at 0x11f5830>]


Writing own inspectors
======================

You can write your own inspector and register it as a more special adapter than
the basic ones which come with this package:

    >>> from sw.objectinspection import BasicInspector
    >>> import zope.component
    >>> import zope.interface

    >>> class DummyAttributesInspector(BasicInspector):
    ...     zope.component.adapts(ToInspect)
    ...     zope.interface.implements(IAttributesInspector)
    ...
    ...     def __call__(self):
    ...         # The object, which is to be inspected, can be accessed
    ...         # with self._inspecting
    ...         return ['foo', 'bar']

    >>> gsm = zope.component.getGlobalSiteManager()
    >>> gsm.registerAdapter(DummyAttributesInspector)

Now, when inspecting `ToInspect` for attributes, we get our
`DummyAttributesInspector`:

    >>> inspector = IAttributesInspector(ToInspect())
    >>> inspector
    <DummyAttributesInspector object at 0x11f69d0
     used for ToInspect object at 0x11f6910>
    >>> inspector()
    ['foo', 'bar']
