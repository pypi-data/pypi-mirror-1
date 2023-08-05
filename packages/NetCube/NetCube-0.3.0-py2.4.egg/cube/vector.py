#!/usr/bin/env python

# Copyright 2005 Jeffrey J. Kyllo

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Functions for working with vectors.

Vector provides a class for performing operations on and with vectors.
Internally they are represented using a list and in many cases can be treated
as such.  The semantics of vectors override those of lists, however so one
should be careful when working with them as lists."""

class Vector:
    """A Vector represents a vector of an arbitrary dimension.  The Vector
    object can be resized using the setsize() method or at instantiation with
    the size parameter.  Otherwise, it will assume the size of the array given
    at instantiation or a size of 0 if none is given.  Common vector operations
    are implemented to make working with vectors in Python easier on the
    programmer.
    """
    def __init__(self, *args, **kwargs):
	"""Initialize a new Vector object.  The vector is initialized with
	values from the given arguments.  If no non-keyword arguments are
	given, then the 'size' keyword argument sets the desired size of the
	new vector or 0 if one is not provided.
	"""
	self.members = []

	if len(args) > 0:
	    self.members[:] = args
	else:
	    if kwargs.has_key('size'):
		self.setsize(kwargs['size'])

    def dot(self, other):
	self.__mul__(other)

    def cross(self, other):
	pass

    def setsize(self, newsize):
	"""Increases or decreases the number of dimensions stored in this
	Vector to newsize.
	"""
	if newsize > len(self):
	    for i in range(newsize-len(self)):
		self.members.append(None)
	elif newsize < len(self):
	    self.members = self.members[0,newsize]

    def magnitude(self):
	"""Calculate the magnitude of this Vector.

	x.magnitude() <==> |x|
	"""
	import math
	sum = 0
	for i in range(len(self)):
	    sum += self[i] ** 2
	return math.sqrt(sum)

    def _vadd(self, a, b, o):
	"""Add the members of two vectors a and b, storing the results in o.
	This method should not be used directly and is provided only for use as
	a consolidation of the add method.

	x._vadd(a, b, o) <==> o=a+b
	"""
	if len(a) != len(b):
	    raise Exception, 'Dimension mismatch.'
	o.setsize(len(a))
	for i in range(len(a)):
	    o[i] = a[i] + b[i]
	return o

    def _vmul(self, a, b, r):
	"""Multiply the members of two vectors a and b, storing the results in
	r.  This method should not be used directly and is provided only for
	use as a consolidation of the mul, imul, and rmul methods.

	x._vmul(a, b, r) <==> r=a*b
	"""
	atype = type(a)
	btype = type(b)
	if not isinstance(r, Vector):
	    raise Exception, 'Result must be a vector'

	if atype is int or atype is float:
	    if btype is int or btype is float:
		raise Exception, "No vector found."
	    elif btype is list or isinstance(b, Vector):
		n = a
		v = b
	    else:
		raise 'Unrecognized type in Vector multiplication:  %s.' % typea
	elif atype is list or isinstance(a, Vector):
	    if btype is int or btype is float:
		n = b
		v = a
	    elif btype is list or isinstance(b, Vector):
		if len(a) != len(b):
		    raise 'Dimension mismatch'
		n = b
		v = a
	    else:
		raise 'Unrecognized type in Vector multiplication:  %s.' % btype
	else:
	    raise 'Unrecognized type in Vector multiplication:  %s.' % atype

	for i in range(len(v)):
	    if type(n) is list or isinstance(n, Vector):
		o = n[i]
	    else:
		o = n
	    r[i] = v[i] * o

	return r

    def __add__(self, y):
	"""Add the members of the given vector to this vector and return a new
	vector with the results.  Both vectors must have the same number of
	dimensions.

	x.__add__(y) <==> x + y
	"""
	return self._vadd(self, y, Vector(len(self)))

    def __eq__(self, y):
	"""Check whether this vector is equivalent to the given vector."""
	if len(self) != len(y):
	    return False
	else:
	    for i in range(len(self)):
		if self[i] != y[i]:
		    return False
	    return True

    def __getitem__(self, y):
	"""Get the value of a particular dimension of this vector."""
	return self.members[y]

    def __getslice__(self, i, j):
	"""Get the values of a particular set of dimensions of this vector."""
	return self.members[i:j]

    def __hash__(self):
	return self.members.__hash__()

    def __iadd__(self, y):
	"""Add the given to this vector and store the results in this vector.

	x.__iadd__(y) <==> x += y
	"""
	return self._vadd(self, y, self)

    def __imul__(self, y):
	"""Multiply this vector's members by the members of the given vector and store the results in this vector.

	x.__imul__(y) <==> x *= y
	"""
	return self._vmul(self, y, self)

    def __iter__(self):
	"""Return an iterator of the dimensions of this vector."""
	return self.members.__iter__()

    def __len__(self):
	"""Return the number of dimensions stored in this vector."""
	return len(self.members)

    def __mul__(self, n):
	"""Multiply this vector's members by the members of the given vector and return them in a new vector.  In other words, return the dot product of the two vectors.

	x.__mul__(y) <==> x*n
	"""
	return self._vmul(self, n, Vector(len(self)))

    def __ne__(self, y):
	"""Check whether this vector is not equivalent to the given vector."""
	return not self.__eq__(y)

    def __neg__(self):
	"""Return the negative vector of this vector.
	i.e. -[1, 2, 3] = [-1, -2, -3]."""
	return Vector([-x for x in self.members])

    def __repr__(self):
	"""Return a string representation of this vector.  Results in a string of the form '([val][, val]...)"""
	ret = ""
	for i in range(len(self)):
	    ret += repr(self[i])
	    if i < (len(self) - 1):
		ret += ', '

	return '(' + ret + ')'

    def __rmul__(self, n):
	"""Multiply the members of the given vector by those in this vector and return the result in a new vector.  Note that this function is the reverse order of __mul__ although the result is the same."""
	return self._vmul(n, self, Vector(len(self)))

    def __setitem__(self, i, y):
	"""Store the given value y in this vector as dimension i."""
	self.members[i] = y

    def __setslice__(self, i, j, y):
	"""Store the given values of y as the dimensions from i through j-1."""
	self.members[i:j] = y

if __name__ == '__main__':
    print "Testing class Vector"
    tests = {}
    tests['__init__'] = lambda: isinstance(Vector(), Vector)

    def setsize_test():
	v = Vector()
	v.setsize(3)
	if len(v.members) == 3:
	    return True
	else:
	    return False

    tests['setsize'] = setsize_test

    def magnitude_test():
	v = Vector(3)
	v[0:3] = [1, 2.0, 3]
	import math
	if v.magnitude() == math.sqrt(14):
	    return True
	else:
	    return False
    tests['magnitude'] = magnitude_test

    def add_test():
	v = Vector(3)
	v[0:3] = [1, 2, 3]
	o = v + [3, 2, 1]
	if o[0:3] == [4, 4, 4]:
	    return True
	else:
	    return False
    
    tests['__add__'] = add_test


    def eq_test():
	v = Vector(3)
	v[0:3] = [1, 2, 3]
	return v == [1, 2, 3]

    tests['__eq__'] = eq_test

    def getitem_test():
	v = Vector(1)
	v[0] = 1
	return v[0] == 1

    tests['__getitem__'] = getitem_test

    def iadd_test():
	v = Vector(3)
	v[0:3] = [0, 0, 0]
	v += [1, 2, 3]
	return v == [1, 2, 3]

    tests['__iadd__'] = iadd_test

    def imul_test():
	v = Vector(3)
	v[0:3] = [1, 2, 3]
	v *= [1, 2, 3]
	return v == [1, 4, 9]

    tests['__imul__'] = imul_test

    tests['__iter__'] = lambda: False

    def mul_test():
	v = Vector(3)
	v[0:3] = [1, 2, 3]
	o = 3
	return (v * o) == [3, 6, 9]

    tests['__mul__'] = mul_test

    def ne_test():
	v = Vector(3)
	v[0:3] = [1, 2, 3]
	return v != [2, 1, 3]

    tests['__ne__'] = ne_test

    def rmul_test():
	v = Vector(3)
	v[0:3] = [1, 2, 3]
	o = 3
	return (o * v) == [3, 6, 9]

    tests['__rmul__'] = rmul_test


    for k in tests.keys():
	each_test = tests[k]
	if type(each_test) is not list:
	    test_list = [each_test]
	else:
	    test_list = each_test

	for test in test_list:
	    try:
		ret = test()
		if ret:
		    status = 'Successful'
		else:
		    status = 'Failed'
	    except Exception, e:
		status = 'Failed due to exception: %s' % e
		import traceback
		traceback.print_exc()


	    print '%s test %s.' % (k, status)



origin = Vector(0.0, 0.0, 0.0)
i = Vector(1.0, 0.0, 0.0)
j = Vector(0.0, 1.0, 0.0)
k = Vector(0.0, 0.0, 1.0)

unit_vectors = (i, j, k)
