# Twisted Goodies:
# Miscellaneous add-ons and improvements to the separately maintained and
# licensed Twisted (TM) asynchronous framework. Permission to use the name was
# graciously granted by Twisted Matrix Laboratories, http://twistedmatrix.com.
#
# Copyright (C) 2007 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Pack and unpack SciPy arrays and Python floats before and after transmission
via PB.
"""

import struct, base64


try:
    import scipy as s
except:
    pass


def needsPacking(obj):
    return str(type(obj)).startswith("<type 'numpy.")


class Packer(object):
    """
    I pack up SciPY arrays of one or two dimensions, and Python floats.

    You can supply one or more such arrays to my constructor, or use my
    L{append} method to supply them individually. Then call the instance to get
    a compact binary representation (a string) of the entire package of
    packed-up arrays.
    """
    __slots__ = ['dataList']
    
    def __init__(self, *values):
        self.dataList = []
        for value in values:
            self.append(value)

    def append(self, X):
        dims = len(s.shape(X))
        if dims == 1:
            X = s.array(X).reshape((len(X), 1))
        elif dims == 0:
            X = [[X]]
        rows, cols = s.shape(X)
        formatString = "d" * cols
        dataStrings = [struct.pack("ii", rows, cols)]
        for row in X:
            dataStrings.append(struct.pack(formatString, *row))
        self.dataList.append("".join(dataStrings))
    
    def __call__(self, encode=False):
        result = struct.pack("B", len(self.dataList)) + "".join(self.dataList)
        if encode:
            result = base64.b64encode(result)
        return result


class Unpacker(object):
    """
    I unpack SciPY 1-D arrays, 2-D arrays, and Python floats from a binary
    representation supplied to my constructor as a string. Call the constructed
    instance of me once for each thing to unpack.

    """
    __slots__ = ['dataString', 'k', 'count', 'N']
    
    def __init__(self, dataString, decode=False):
        if decode:
            dataString = base64.b64decode(dataString)
        self.dataString = dataString[1:]
        self.k = 0
        self.N = struct.unpack("B", dataString[0])[0]

    def __len__(self):
        return self.N

    def __iter__(self):
        self.k = 0
        self.count = 0
        return self

    def next(self):
        if self.count == self.N:
            raise StopIteration()
        self.count += 1
        return self()

    def __call__(self):
        rows, cols = struct.unpack("ii", self.dataString[self.k:self.k+8])
        self.k += 8
        Z = s.empty((rows, cols), s.float64)
        formatString = "d" * cols
        for k in xrange(rows):
            rowString = self.dataString[self.k:self.k+8*cols]
            self.k += 8*cols
            Z[k, :] = struct.unpack(formatString, rowString)
        if cols > 1:
            return Z
        if rows > 1:
            return Z[:,0]
        return Z[0][0]
    
    
def packwrap(f):
    """
    Decorate a function I{f} with me and I will give you a substitute function
    that you can call with a packed version of the function's args. The
    function must return one or more packable values. The substitute function
    will return a packed version of that result.
    """
    def substituteFunction(*args):
        if len(args) == 1 and isinstance(args[0], str):
            args = tuple(Unpacker(args[0]))
        result = f(*args)
        if not isinstance(result, (list, tuple)):
            result = (result,)
        return Packer(*result)()

    substituteFunction.func_name = f.func_name
    return substituteFunction


