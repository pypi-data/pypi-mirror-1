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
Unit tests for twisted_goodies.pybywire.pack
"""

import scipy as s

import mock, pack


class Test_PackUnpack(mock.TestCase):
    def test_packFloat(self):
        for val in (s.pi, 0.0, 1.23E5, s.exp(0), 10, -1.7985E20):
            packer = pack.Packer()
            packer.append(val)
            x = packer()
            up = pack.Unpacker(x)
            self.failUnlessAlmostEqual(up(), val, 15)

    def test_packOneElementArray(self):
        x = pack.Packer(s.array([0.5]))()
        up = pack.Unpacker(x)
        self.failUnlessEqual(list(up), [0.5])

    def test_packVector(self):
        vector = s.linspace(-s.pi, +s.pi, 1024)
        x = pack.Packer(vector)()
        up = pack.Unpacker(x)
        X = up()
        self.failUnlessArraysAlmostEqual(X, vector)

    def test_packArray(self):
        array = s.arange(100).reshape((10,10))
        x = pack.Packer(array)()
        up = pack.Unpacker(x)
        self.failUnlessEqual(sum(sum(up()-array)), 0.0)

    def test_packArray_base64(self):
        array = s.randn(100).reshape((10,10))
        x = pack.Packer(array)(encode=True)
        up = pack.Unpacker(x, decode=True)
        self.failUnlessEqual(sum(sum(up()-array)), 0.0)

    def test_packMultiple(self):
        scalar = s.pi
        array = s.linspace(-s.pi, +s.pi, 10)
        packer = pack.Packer()
        packer.append(scalar)
        packer.append(array)
        packer.append(0.0)
        packer.append(-array)
        x = packer()
        up = pack.Unpacker(x)
        self.failUnlessAlmostEqual(up(), scalar, 15)
        self.failUnlessArraysAlmostEqual(up(), array) 
        self.failUnlessAlmostEqual(up(), 0.0, 15)
        self.failUnlessArraysAlmostEqual(up(), -array)
        
    def test_packAsIterable(self):
        packer = pack.Packer()
        myList = [1.0, 2.0, 3.0]
        for value in myList:
            packer.append(value)
        x = packer()
        up = pack.Unpacker(x)
        for k, value in enumerate(up):
            self.failUnlessEqual(value, myList[k])
        self.failUnlessEqual(list(up), myList)
        self.failUnlessEqual(tuple(up), tuple(myList))


class Test_packwrap(mock.TestCase):
    class Thingy(mock.Mock):
        def stupidMethod(self):
            return 10

        def scale(self, x):
            return 5*x
        
        def addTwoVectors(self, X, Y):
            return X + Y

    def setUp(self):
        self.thingy = self.Thingy()

    def _unpack(self, X):
        return list(pack.Unpacker(X))

    def test_wrapsFunction(self):
        substitute = pack.packwrap(lambda x: 2*x)
        self.failUnlessEqual(self._unpack(substitute(10)), [20])

    def test_wrapsMethod(self):
        result = pack.packwrap(self.thingy.stupidMethod)()
        self.failUnlessEqual(self._unpack(result), [10])

    def test_unpacksOneScalarArg(self):
        x = pack.Packer(0.5)()
        packedResult = pack.packwrap(self.thingy.scale)(x)
        result = list(pack.Unpacker(packedResult))
        self.failUnlessEqual(result, [2.5])

    def test_unpacksOneArrayArg(self):
        x = pack.Packer(s.array([0.5]))()
        packedResult = pack.packwrap(self.thingy.scale)(x)
        result = list(pack.Unpacker(packedResult))
        self.failUnlessEqual(result, [2.5])

    def test_unpacksMultipleArgs(self):
        X = s.linspace(-5, +5, 10)
        Y = s.linspace(10, 20, 10)
        packedArgs = pack.Packer(X, Y)()
        packedResult = pack.packwrap(self.thingy.addTwoVectors)(packedArgs)
        result = list(pack.Unpacker(packedResult))
        self.failUnlessElementsEqual(result[0], X+Y)

