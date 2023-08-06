====================
Extrinsic References
====================

Extrinsic reference registries record a key and one or more values to which
they refer.  The key and all values must be adaptable to
zope.app.keyreference.interfaces.IKeyReference.

    >>> import zc.extrinsicreference
    >>> references = zc.extrinsicreference.ExtrinsicReferences()
    >>> references.add(1, 2)
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', 1...
    >>> from zope import interface, component
    >>> from zope.app.keyreference.interfaces import IKeyReference
    >>> class IMyObject(interface.Interface):
    ...     "An interface for which we register an IKeyReference adapter"
    ...     id = interface.Attribute("An id unique to IMyObject instances")
    ...
    >>> class MyObject(object):
    ...     interface.implements(IMyObject)
    ...     _id_counter  = 0
    ...     @classmethod
    ...     def _getId(cls):
    ...         val = cls._id_counter
    ...         cls._id_counter += 1
    ...         return val
    ...     def __init__(self):
    ...         self.id = self._getId()
    ...
    >>> class DummyKeyReference(object):
    ...     interface.implements(IKeyReference)
    ...     component.adapts(IMyObject)
    ...     key_type_id = 'zc.extrinsicreference.doctest'
    ...     def __init__(self, obj):
    ...         self.object = obj
    ...     def __call__(self):
    ...         """Get the object this reference is linking to.
    ...         """
    ...         return self.object
    ...     def __hash__(self):
    ...         """Get a unique identifier of the referenced object.
    ...         """
    ...         return hash(self.object.id)
    ...     def __cmp__(self, other):
    ...         """Compare the reference to another reference.
    ...         """
    ...         if self.key_type_id == other.key_type_id:
    ...             return cmp(self.object.id, other.object.id)
    ...         return cmp(self.key_type_id, other.key_type_id)
    ...
    >>> component.provideAdapter(DummyKeyReference)
    >>> object1 = MyObject()
    >>> references.add(object1, 2)
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', 2...
    >>> value1 = MyObject()
    >>> value2 = MyObject()
    >>> references.add(object1, value1)
    >>> references.add(object1, value2)

Values can be retrieved by their key:

    >>> set(references.get(object1)) == set((value1, value2))
    True

References can be removed:

    >>> references.remove(object1, value1)
    >>> list(references.get(object1)) == [value2]
    True

But if the reference is not registered, removing it raises a KeyError.

    >>> references.remove(object1, value1)
    Traceback (most recent call last):
    ...
    KeyError:...
    >>> object2 = MyObject()
    >>> references.remove(object2, value2)
    Traceback (most recent call last):
    ...
    KeyError:...

If you prefer to silently ignore these errors, use `discard`.

    >>> references.discard(object1, value1)
    >>> references.discard(object2, value2)

Otherwise, you can use `contains` to determine if the reference exists:

    >>> references.contains(object1, value1)
    False
    >>> references.contains(object2, value2)
    False
    >>> references.contains(object1, value2)
    True

If a key has no associated values, an empty iterable is returned:

    >>> references.discard(object1, value2)
    >>> list(references.get(object1))
    []

Adding a value more than once does not cause the value to be included
in the result sequence more than once:

    >>> references.add(object1, value1)
    >>> references.add(object1, value1)
    >>> list(references.get(object1)) == [value1]
    True

The `set` method destructively sets the given values for the object.  Repeated
objects are collapsed to a single instance.

    >>> references.set(object1, (value2, object2, value2, value2, object2))
    >>> references.contains(object1, value1)
    False
    >>> len(list(references.get(object1)))
    2
    >>> set(references.get(object1)) == set((value2, object2))
    True
    >>> references.set(object1, ())
    >>> len(list(references.get(object1)))
    0

The `update` method adds values to the previous values, non-destructively.

    >>> references.add(object1, value1)
    >>> references.update(object1, (value2, object2, value2))
    >>> len(list(references.get(object1)))
    3
    >>> set(references.get(object1)) == set((value1, value2, object2))
    True
