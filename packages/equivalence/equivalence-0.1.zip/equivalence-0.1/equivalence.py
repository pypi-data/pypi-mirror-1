#todo: docstrings, comments

__all__ = ['Equivalence']
__docformat__ = "restructuredtext en"
__author__ = 'George Sakkis <george.sakkis AT gmail DOT com>'

from collections import defaultdict


class Equivalence(object):
    '''Representation of a general equivalence relation.

    An `Equivalence` instance can be used to maintain a partition of objects
    into equivalence sets. Two objects ``x`` and ``y`` are considered
    equivalent either implicitly through a key function or explicitly. For the
    implicit case, ``x`` and ``y`` are equivalent if ``key(x) == key(y)`` for
    some provided function ``key`` (by default the identity function ``lambda x:x``).
    For the explicit case, ``x`` and ``y`` are considered equivalent after a call
    to `merge(x,y)`, regardless of their keys.

    This class makes sure that the equivalence properties (reflexivity, symmetry,
    transitivity) are maintained, provided that ``key(x)`` remains fixed for a
    given object ``x`` (i.e. ``key`` is deterministic and does not depend on
    mutable state of ``x``).
    '''

    def __init__(self, key=None):
        '''Initialize a new equivalence relation.

        :param key: A callable that takes a single argument and returns its
            equivalence key (default: identity function).
        '''
        self._keyfunc = key
        # maps a member's key to its partition's key
        self._key2pkey = {}
        # invert mapping of self._key2pkey:
        # maps a partition key to the set of its partition members' keys
        self._pkey2keys = defaultdict(set)
        # maps a partition key to the set of its members
        self._pkey2members = defaultdict(set)

    def update(self, *objects):
        '''Update this equivalence with the given objects.'''
        for obj in objects:
            self._pkey2members[self.partition_key(obj)].add(obj)

    def merge(self, *objects):
        '''Merge all the given objects into the same equivalence set.'''
        objects = iter(objects)
        try: obj = objects.next()
        except StopIteration: return
        new_pkey = self.partition_key(obj)
        partition_members = self._pkey2members[new_pkey]
        partition_members.add(obj)
        key2pkey = self._key2pkey
        partition_keys = self._pkey2keys[new_pkey]
        for obj in objects:
            partition_members.add(obj)
            old_pkey = self.partition_key(obj)
            if old_pkey != new_pkey:
                key2pkey[old_pkey] = new_pkey
                partition_keys.add(old_pkey)
                for key in self._pkey2keys.pop(old_pkey, ()):
                    key2pkey[key] = new_pkey
                    partition_keys.add(key)
                partition_members.update(self._pkey2members.pop(old_pkey, ()))
        if not partition_keys: # don't need to key empty sets
            del self._pkey2members[new_pkey]

    def are_equivalent(self, *objects):
        '''Checks whether all objects are equivalent.

        An object doesn't have to be inserted first (through `update` or `merge`)
        in order to appear as an argument. In this case, its ``key`` is used to
        determine the partition it would belong if it was inserted.

        :rtype: bool
        '''
        if not objects:
            raise ValueError('No objects given')
        return len(set(self.partition_key(obj) for obj in objects)) == 1

    def partitions(self, objects=None):
        '''Returns the partitioning of `objects` into equivalence groups.

        :type objects: Iterable or None
        :param objects: If not None, it must be an iterable of objects to be
            partitioned. Otherwise, it defaults to the set of objects already
            inserted in the equivalence (through `update` and `merge`).

        :returns: A list of partitions, each partition being a list of objects.
        :rtype: list of lists
        '''
        if not objects:
            objects = (obj for members in self._pkey2members.itervalues()
                       for obj in members)
        key2partition = defaultdict(list)
        for obj in objects:
            key2partition[self.partition_key(obj)].append(obj)
        return key2partition.values()

    def partition(self, obj):
        '''Return the set of objects in the equivalence that are equivalent to
        `obj`.

        :rtype: set
        '''
        return self._pkey2members.get(self.partition_key(obj)) or set()

    def partition_key(self, obj):
        '''Return the key of the equivalence partition `obj` belongs to.'''
        key = self._keyfunc(obj) if self._keyfunc else obj
        return self._key2pkey.get(key,key)
