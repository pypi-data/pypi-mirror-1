# Copyright (c) 2007 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

import cairo

import pycha.bar

class RectTests(unittest.TestCase):

    def test_rect(self):
        r = pycha.bar.Rect(2, 3, 20, 40, 2.5, 3.4, 'test')
        self.assertEqual(r.x, 2)
        self.assertEqual(r.y, 3)
        self.assertEqual(r.w, 20)
        self.assertEqual(r.h, 40)
        self.assertEqual(r.xval, 2.5)
        self.assertEqual(r.yval, 3.4)
        self.assertEqual(r.name, 'test')

class BarTests(unittest.TestCase):

    def test_init(self):
        ch = pycha.bar.BarChart(None)
        self.assertEqual(ch.bars, [])
        self.assertEqual(ch.minxdelta, 0)

class VerticalBarTests(unittest.TestCase):

    def test_updateChart(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
        dataset = (
            ('dataset1', ([0, 1], [1, 1], [2, 3])),
            ('dataset2', ([0, 2], [1, 0], [3, 4])),
            )
        ch = pycha.bar.VerticalBarChart(surface)
        ch.addDataset(dataset)
        ch._updateXY()
        ch._updateChart()
        self.assertEqual(ch.xrange, 3)
        self.assertAlmostEqual(ch.xscale, 2 / 9.0, 4)
        self.assertEqual(ch.minxdelta, 1)

        bars = (
            pycha.bar.Rect(0.25/9, 3.0/4, 0.0833, 1.0/4, 0, 1, 'dataset1'),
            pycha.bar.Rect(0.25,   3.0/4, 0.0833, 1.0/4, 1, 1, 'dataset1'),
            pycha.bar.Rect(4.25/9, 1.0/4, 0.0833, 3.0/4, 2, 3, 'dataset1'),

            pycha.bar.Rect(1.0/9,  2.0/4, 0.0833, 2.0/4, 0, 2, 'dataset2'),
            pycha.bar.Rect(3.0/9,  1,     0.0833, 0, 1, 0, 'dataset2'),
            pycha.bar.Rect(7.0/9,  0,     0.0833, 1, 3, 4, 'dataset2'),
            )

        for i, bar in enumerate(bars):
            b1, b2 = ch.bars[i], bar
            self.assertAlmostEqual(b1.x, b2.x, 4)
            self.assertAlmostEqual(b1.y, b2.y, 4)
            self.assertAlmostEqual(b1.w, b2.w, 4)
            self.assertAlmostEqual(b1.h, b2.h, 4)
            self.assertEqual(b1.xval, b2.xval)
            self.assertEqual(b1.yval, b2.yval)
            self.assertEqual(b1.name, b2.name)

    def test_updateTicks(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
        dataset = (
            ('dataset1', ([0, 1], [1, 1], [2, 3])),
            ('dataset2', ([0, 2], [1, 0], [3, 4])),
            )
        ch = pycha.bar.VerticalBarChart(surface)
        ch.addDataset(dataset)
        ch._updateXY()
        ch._updateChart()
        ch._updateTicks()
        xticks = [(1/9.0, 1), (3/9.0, 2), (5/9.0, 3)]
        for i in range(len(xticks)):
            self.assertAlmostEqual(ch.xticks[i][0], xticks[i][0], 4)
            self.assertAlmostEqual(ch.xticks[i][1], xticks[i][1], 4)

    def test_shadowRectangle(self):
        ch = pycha.bar.VerticalBarChart(None)
        shadow = ch._getShadowRectangle(10, 20, 400, 300)
        self.assertEqual(shadow, (8, 18, 404, 302))

class HorizontalBarTests(unittest.TestCase):

    def test_updateChart(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
        dataset = (
            ('dataset1', ([0, 1], [1, 1], [2, 3])),
            ('dataset2', ([0, 2], [1, 0], [3, 4])),
            )
        ch = pycha.bar.HorizontalBarChart(surface)
        ch.addDataset(dataset)
        ch._updateXY()
        ch._updateChart()
        self.assertEqual(ch.xrange, 3)
        self.assertAlmostEqual(ch.xscale, 2 / 9.0, 4)
        self.assertEqual(ch.minxdelta, 1)

        bars = (
            pycha.bar.Rect(0, 0.25/9, 1.0/4, 0.0833, 0, 1, 'dataset1'),
            pycha.bar.Rect(0, 0.25,   1.0/4, 0.0833, 1, 1, 'dataset1'),
            pycha.bar.Rect(0, 4.25/9, 3.0/4, 0.0833, 2, 3, 'dataset1'),

            pycha.bar.Rect(0, 1.0/9,  2.0/4, 0.0833, 0, 2, 'dataset2'),
            pycha.bar.Rect(0, 3.0/9,  0,     0.0833, 1, 0, 'dataset2'),
            pycha.bar.Rect(0, 7.0/9,  1,     0.0833, 3, 4, 'dataset2'),
            )

        for i, bar in enumerate(bars):
            b1, b2 = ch.bars[i], bar
            self.assertAlmostEqual(b1.x, b2.x, 4)
            self.assertAlmostEqual(b1.y, b2.y, 4)
            self.assertAlmostEqual(b1.w, b2.w, 4)
            self.assertAlmostEqual(b1.h, b2.h, 4)
            self.assertEqual(b1.xval, b2.xval)
            self.assertEqual(b1.yval, b2.yval)
            self.assertEqual(b1.name, b2.name)

    def test_updateTicks(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
        dataset = (
            ('dataset1', ([0, 1], [1, 1], [2, 3])),
            ('dataset2', ([0, 2], [1, 0], [3, 4])),
            )
        ch = pycha.bar.HorizontalBarChart(surface)
        ch.addDataset(dataset)
        ch._updateXY()
        ch._updateChart()
        ch._updateTicks()
        yticks = [(1/9.0, 1), (3/9.0, 2), (5/9.0, 3)]
        for i in range(len(yticks)):
            self.assertAlmostEqual(ch.yticks[i][0], yticks[i][0], 4)
            self.assertAlmostEqual(ch.yticks[i][1], yticks[i][1], 4)

    def test_shadowRectangle(self):
        ch = pycha.bar.HorizontalBarChart(None)
        shadow = ch._getShadowRectangle(10, 20, 400, 300)
        self.assertEqual(shadow, (10, 18, 402, 304))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(RectTests),
        unittest.makeSuite(BarTests),
        unittest.makeSuite(VerticalBarTests),
        unittest.makeSuite(HorizontalBarTests),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

