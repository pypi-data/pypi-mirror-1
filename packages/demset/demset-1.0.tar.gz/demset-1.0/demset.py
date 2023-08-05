#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
""" The set and frozenset data types.

 This is a re-implementation of the built-in Python 2.4 set types,
 but which is compatible with Python 2.2 or later.

 Sets are unordered collections of items (called elements, the set's
 members).  The sets in this module are finite sets in the
 mathematical sense.  They support most set operations, such as
 fast membership testing, union, intersection, and so forth.

 This module defines two types of set classes:

   * frozenset - an immutable set class
   * set - a mutable set class

 Frozen sets can be used where ever immutable and hashable types are
 needed, such as the keys to dictionaries.  Sets, although not
 hashable, can be modified by having elements added to or removed from
 the set.

 In general, operations involving both sets and frozensets (such as
 set union) can be mixed.  The type of set returned will be the same
 as the type of set of the left-hand parameter.  Sets and frozensets
 can be compared with each other for equality and subset relations
 with expected results.

 Sets of either type may only contain hashable types as their members.
 The member elements do not have to all be the same type.  The typical
 way to create these is:

    S1 = frozenset(['blue','red','green'])
    S2 = set([1,3,5,7,11])

 Compatibility: Care has been taken to keep this module quite compatible
 with the Python 2.4 types.  However a few differences do exist:

    * Although you can pickle these set types, the pickled values are
      not interchangeable between this module and Python 2.4's builtin
      types.
    * The type inheritance chain of the set types may be different.
      In particular isinstance(set,frozenset) will return True for
      my module, but false in Python 2.4's builtin types.
    * The code is 100% python rather than C, so it may have slightly
      poorer performance or memory usage.

 Importing hints: To use this module as a replacement for the set and
 frozenset types in your own code which needs to run in Python 2.2,
 but still allow it to use the faster built-in types if you are
 running in Python 2.4, then you should import this module into your
 own code as follows:

    try:
       type(frozenset)
    except NameError:
       from demset import set, frozenset
"""
__author__ = "Deron Meranda <http://deron.meranda.us/>"
__date__ = "2005-12-15"
__version__ = "1.0"
__credits__ = """Copyright (c) 2005 Deron E. Meranda <http://deron.meranda.us/>
This module is Open Source -- Released under same terms as Python
version 2.2 or any later version, see <http://python.org/>.
"""

class frozenset(object):
    """An immutable set, an unordered collection of elements.

    You can build one of these by passing in any sequence or iterable
    as the argument to the constructor.  Note that only hashable types
    may be used as set elements.

    For a mutable equivalent, see the set class.

    """
    def __init__(self, elements=None):
        """Create this set from the list of elements.

        The elements can be any iterable object, or None to create an empty set.
        """
        self._d = {}  # dictionary used to store elements
        if elements:
            for e in elements:
                self._add(e)

    def _add(self, element):
        try:
            h = hash(element)
        except TypeError:
            raise TypeError('Only hashable elements may be put in a ' + self.__class__.__name__)
        self._d[element] = None

    def __repr__(self):
        """Python-expression representation of this set"""
        return self.__class__.__name__ + '([' + ','.join(map(repr,self._d)) + '])'

    def __str__(self):
        """String human-readable representation of this set"""
        k = self._d.keys()
        k.sort()
        return '{' + ', '.join(map(str,k)) + '}'

    def __unicode__(self):
        """Unicode human-readable representation of this set"""
        k = self._d.keys()
        k.sort()
        return '{' + ', '.join(map(unicode,k)) + '}'
        
    def __getstate__(self):
        """Pickler"""
        return tuple(self._d.keys())

    def __setstate__(self, state):
        """Unpickler"""
        self.__init__(state)

    def __len__(self):
        """Returns the number of elements in this set."""
        return len(self._d)

    def __eq__(self, other):
        """Is this set equal to another set (has exactly the same member elements)."""
        if self is other:
            return True # same object (no need to scan all the elements)
        if len(self) != len(other):
            return False
        for m in self:
            if m not in other:
                return False
        return True

    def __ne__(self, other):
        """Is this set not equal to another set (converse of __eq__ method)."""
        return not self.__eq__(other)

    def copy(self):
        """A shallow copy.  Returns a new set with the same member elements."""
        C = self.__class__( self )
        return C

    def __or__(self, other):
        """Set union (| operator).

        Returns a new set whose members are those which are in either
        set.

        """
        if not hasattr(other,'union'):
            raise TypeError('The | operator requires a set object, or call the union() method')
        return self.union(other)

    def union(self, other):
        """Set union.

        Returns a new set whose members are those in either set.
        Unlike the |-operator, this method will also accept any
        iterable sequence in place of a set object.

        """
        U = self.__class__()
        for m in self:
            U._add(m)
        for m in other:
            U._add(m)
        #if not hasattr(self,'clear') and not hasattr(other,'clear'):
        #    U = frozenset(U)  # both are frozensets (or immutable) so result is too
        return U

    def __and__(self, other):
        """Set intersection (& operator).

        Returns a new set whose members are those which are in both
        sets.

        """
        if not hasattr(other,'intersection'):
            raise TypeError('The & operator requires a set object, or call the intersection() method')
        return self.intersection(other)

    def intersection(self, other):
        """Set intersection.

        Returns a new set whose members are those which are in both
        sets.  Unlike the &-operator, this method will also accept any
        iterable sequence in place of a set object.

        """
        I = self.__class__()
        for m in self:
            if m in other:
                I._add(m)
        #if not hasattr(self,'clear') and not hasattr(other,'clear'):
        #    I = frozenset(I)  # both are frozensets so result is too
        return I

    def __sub__(self, other):
        """Set difference (- operator).

        Returns a new set whose members are in this set but not in the
        other set.

        """
        if not hasattr(other,'difference'):
            raise TypeError('The - operator requires a set object, or call the difference() method')
        return self.difference(other)

    def difference(self, other):
        """Set difference.

        Returns a new set whose members are in this set but not in the
        other set.  Unlike the (-)-operator, this method will also
        accept any iterable sequence in place of a set object.

        """
        D = self.__class__()
        for m in self:
            if m not in other:
                D._add(m)
        #if not hasattr(self,'clear') and not hasattr(other,'clear'):
        #    D = frozenset(D)  # both are frozensets so result is too
        return D

    def __xor__(self, other):
        """Set symmetric difference (^ operator).

        Returns a new set whose members are those that are only in
        one of the sets, but not both.

        """
        if not hasattr(other,'symmetric_difference'):
            raise TypeError('The ^ operator requires a set object, or call the symmetric_difference() method')
        return self.symmetric_difference(other)

    def symmetric_difference(self, other):
        """Set symmetric difference.

        Returns a new set whose members are those that are only in
        one of the sets, but not both.  Unlike the ^-operator, this
        method will also accept any iterable sequence in place of a
        set object.

        """
        D = self.__class__()
        for m in self:
            if m not in other:
                D._add(m)
        for m in other:
            if m not in self:
                D._add(m)
        #if not hasattr(self,'clear') and not hasattr(other,'clear'):
        #    D = frozenset(D)  # both are frozensets so result is too
        return D

    def __nonzero__(self):
        """Returns True if this set has any members, False if it is empty."""
        return len(self._d) > 0

    def isempty(self):
        """Returns True if this set is empty, False if it has any members."""
        return len(self._d) == 0

    def __lt__(self, other):
        """Is this set a proper subset of another set (but no equal to it)?"""
        return len(self)==0 or (len(self) < len(other) and self.issubset(other))

    def __le__(self, other):
        """Is this set a subset of another set (or equal to it)?"""
        return self.issubset(other)

    def issubset(self, other):
        """Test for subset relation."""
        #  This is coded strangely so that 'other' can be any iterable.
        if len(self) == 0:
            return True  # empty set is always a subset of anything
        try:
            len2 = len(other)
            if len2 < len(self):
                return False
        except TypeError:  # must have an unsized iterator
            pass
        cnt = 0
        for m in other:
            if m in self:
                cnt += 1
            if cnt == len(self):
                return True
        return False

    def __gt__(self, other):
        """Test for proper superset relation.  See issuperset() method."""
        if len(self) <= len(other):
            return False
        return self.issuperset(other)

    def __ge__(self, other):
        """Test for superset relation.  See issuperset() method."""
        return self.issuperset(other)

    def issuperset(self, other):
        """Test for superset relation."""
        if len(self) < len(other):
            return False
        for m in other:
            if m not in self:
                return False
        return True

    def __contains__(self, element):
        """Set membership testing.

        Returns True if the element is a member of the set.
        """
        return self._d.has_key(element)

    def __iter__(self):
        """Creates an iterator for the members of the set.

        Note that the members are not produced in any predictable order.
        """
        i = iter(self._d)
        if not hasattr(i,'__len__'):
            # Emulate Python 2.4's dictitionary-iterator which provides __len__
            n = len(self)
            class setiter(object):
                def __init__(self,i,n):
                    self._i = i
                    self._n = n
                def next(self):
                    return self._i.next()
                def __len__(self):
                    return self._n
            i = setiter(i,n)
        return i

    def __hash__(self):
        """Returns a hash value for the set, useful for dictionary keys.

        The hash value is dependent only upon the set members.
        """
        k = self._d.keys()
        k.sort()
        return hash(tuple(k))


class set(frozenset):
    """A mutable set, an unordered collection of elements.

    You can build one of these by passing in any sequence or iterable
    as the argument to the constructor.  Note that only hashable types
    may be used as set elements.

    For an immutable equivalent, see the frozenset class.

    """
    def __hash__(self):
        raise TypeError('mutable sets are not hashable')

    #def copy(self):
    #    """Shallow copy"""
    #    C = set( self )
    #    return C

    def clear(self):
        """Removes all members from the set, making it an empty set."""
        self._d = {}

    def add(self, element):
        """Add the element to the set"""
        self._add(element)

    def __delitem__(self, element):
        self.remove(element)

    def remove(self, element):
        """Removes member from set, or raises KeyError if not a member"""
        del self._d[element]

    def discard(self, element):
        """Removes member from set if it is a member"""
        try:
            self.remove(element)
        except KeyError:
            pass

    def pop(self):
        """Removes and returns one arbitrary member from the set"""
        i = iter(self)
        try:
            k = i.next()
        except StopIteration:
            raise KeyError('Set is empty')
        else:
            self.remove(k)
            return k

    def update(self, other):
        """Adds all the elements of the other set into this one."""
        if other:
            for m in other:
                self._add(m)

    def intersect_update(self, other):
        """Removes any elements from this set that are not also in the other set."""
        to_del = [m for m in self if m not in other]
        for m in to_del:
            self.remove(m)

    def difference_update(self, other):
        """Removes any elements from this set which are in the other set."""
        for m in other:
            self.discard(m)

    def symmetric_difference_update(self, other):
        """Modifies the set so that it contains all the elements that are in just one of the two sets."""
        to_add = [m for m in other if m not in self]
        to_del = [m for m in self if m in other]
        for m in to_del:
            self.remove(m)
        for m in to_add:
            self.add(m)


def _test_sets():
    """Run some self-tests of the set and frozenset classes.

    Will raise an AssertionError if any test fails.
    """
    s1 = set([1,2,3])
    s2 = set([3,4,5])
    s3 = frozenset([3,2,1])
    assert s1 != s2
    assert s1 == s3
    assert s1 | s2 == set([1,2,3,4,5])
    assert s1 - s2 == set([1,2])
    assert s1 ^ s2 == set([1,2,4,5])
    print 'All set tests succeeded'
    return True

if __name__ == '__main__':
    _test_sets()
