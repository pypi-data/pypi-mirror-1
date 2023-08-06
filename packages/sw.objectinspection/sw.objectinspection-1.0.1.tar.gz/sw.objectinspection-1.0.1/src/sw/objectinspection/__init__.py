# Copyright (c) 2009 Sebastian Wehrmann
# See also LICENSE.txt

import types
import zope.component
import zope.interface


class IAttributesInspector(zope.interface.Interface):
    pass


class IChildrenInspector(zope.interface.Interface):
    pass


class BasicInspector(object):

    zope.component.adapts(object)

    def __init__(self, obj):
        self._inspecting = obj

    def __repr__(self):
        own_repr = super(BasicInspector, self).__repr__()
        inspec_repr = self._inspecting.__repr__()
        return '%s used for %s' % (own_repr[:-1], inspec_repr[1:])


class BasicAttributesInspector(BasicInspector):

    zope.interface.implements(IAttributesInspector)

    def __call__(self):
        attributes = []
        for name in dir(self._inspecting):
            if name.startswith('_'):
                continue
            try:
                value = getattr(self._inspecting, name)
            except Exception:
                continue
            if isinstance(value, type(self.__init__)):
                continue
            # XXX: Classmethods ausschliessen
            attributes.append(name)
        return attributes


class BasicChildrenInspector(BasicInspector):

    zope.interface.implements(IChildrenInspector)

    def __call__(self):
        children = []
        attributes = IAttributesInspector(self._inspecting)()
        for attribute in attributes:
            value = getattr(self._inspecting, attribute)
            for elem in self._traverse(value):
                children.append(elem)
        return children

    def _traverse(self, value):
        values = ()
        if self._is_dict(value):
            values = value.values()
        elif self._is_list(value) or self._is_tuple(value):
            values = value
        elif self._is_class(value):
            yield value

        for elem in values:
            if self._is_class(elem):
                yield elem
            else:
                for subelem in self._traverse(elem):
                    yield subelem

    def _is_list(self, obj):
        if isinstance(obj, types.ListType) or\
              str(type(obj)).endswith("PersistentList'>"):
            return True
        return False

    def _is_tuple(self, obj):
        if isinstance(obj, types.TupleType):
            return True
        return False

    def _is_dict(self, obj):
        if isinstance(obj, dict):
            # Short circuit.
            return True
        # Heuristic for sniffing a dict
        obj_names = set(dir(obj))
        dict_names = set(['__getitem__', 'keys', 'values', 'get', '__len__'])
        if dict_names.issubset(obj_names):
            return True
        return False

    def _is_class(self, obj):
        classstring = str(type(obj))
        if classstring.startswith("<class"):
            return True
        return False
