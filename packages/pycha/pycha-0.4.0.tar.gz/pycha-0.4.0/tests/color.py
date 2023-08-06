# Copyright (c) 2007-2008 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of PyCha.
#
# PyCha is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyCha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PyCha.  If not, see <http://www.gnu.org/licenses/>.

import unittest

import pycha.color

class ColorTests(unittest.TestCase):

    def test_clamp(self):
        self.assertEqual(pycha.color.clamp(0, 1, 2), 1)
        self.assertEqual(pycha.color.clamp(0, 1, -1), 0)
        self.assertEqual(pycha.color.clamp(0, 1, 0.5), 0.5)
        self.assertEqual(pycha.color.clamp(0, 1, 1), 1)
        self.assertEqual(pycha.color.clamp(0, 1, 0), 0)

    def test_hex2rgb(self):
        color = pycha.color.hex2rgb('#ff0000')
        self.assert_(isinstance(color, tuple))
        self.assertAlmostEqual(1, color[0])
        self.assertAlmostEqual(0, color[1])
        self.assertAlmostEqual(0, color[2])

        color2 = pycha.color.hex2rgb(color)
        self.assertEqual(color, color2)

        color = pycha.color.hex2rgb('#000fff000', digits=3)
        self.assert_(isinstance(color, tuple))
        self.assertEqual(0, color[0])
        self.assertEqual(1, color[1])
        self.assertEqual(0, color[2])

        color = pycha.color.hex2rgb('#00000000ffff', digits=4)
        self.assert_(isinstance(color, tuple))
        self.assertEqual(0, color[0])
        self.assertEqual(0, color[1])
        self.assertEqual(1, color[2])

    def test_lighten(self):
        r, g, b = (1.0, 1.0, 0.0)
        r2, g2, b2 = pycha.color.lighten(r, g, b, 0.1)
        self.assertEqual((r2, g2, b2), (1.0, 1.0, 0.1))

        r3, g3, b3 = pycha.color.lighten(r2, g2, b2, 0.5)
        self.assertEqual((r3, g3, b3), (1.0, 1.0, 0.6))

    def _assertColors(self, c1, c2, precission):
        for i in range(3):
            self.assertAlmostEqual(c1[i], c2[i], precission)

    def test_generateColorscheme(self):
        keys = ('k1', 'k2', 'k3', 'k4')
        color = '#ff0000'
        scheme = pycha.color.generateColorscheme(color, keys)

        self._assertColors(scheme['k1'], (1, 0, 0), 3)
        self._assertColors(scheme['k2'], (1, 0.125, 0.125), 3)
        self._assertColors(scheme['k3'], (1, 0.250, 0.250), 3)
        self._assertColors(scheme['k4'], (1, 0.375, 0.375), 3)

    def test_defaultColorScheme(self):
        keys = ('k1', 'k2', 'k3', 'k4')
        scheme1 = pycha.color.defaultColorscheme(keys)
        color = pycha.color.DEFAULT_COLOR
        scheme2 = pycha.color.generateColorscheme(color, keys)
        self.assertEqual(scheme1, scheme2)

    def test_colorScheme(self):
        colors = ('red', 'green', 'blue', 'grey', 'black', 'darkcyan')
        for color in colors:
            self.assert_(pycha.color.colorSchemes.has_key(color))

    def test_autoLighting(self):
        """This test ensures that the colors don't get to white too fast.

        See bug #8.
        """
        # we have a lot of keys
        n = 50
        keys = range(n)
        color = '#ff0000'
        scheme = pycha.color.generateColorscheme(color, keys)

        # ensure that the last color is not completely white
        color = scheme[n-1]
        self.assertAlmostEqual(color[0], 1.0, 4) # the red component was already 1
        self.assertNotAlmostEqual(color[1], 1.0, 4)
        self.assertNotAlmostEqual(color[2], 1.0, 4)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ColorTests),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
