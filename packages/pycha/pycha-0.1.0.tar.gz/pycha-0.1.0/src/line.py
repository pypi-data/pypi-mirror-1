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

from pycha.chart import Chart
from pycha.color import hex2rgb, clamp

class LineChart(Chart):
    
    def __init__(self, surface=None, options={}):
        super(LineChart, self).__init__(surface, options)
        self.points = []
        
    def _updateChart(self):
        """Evaluates measures for line charts"""
        self.points = []

        for i, (name, store) in enumerate(self.dataSets):
            for item in store:
                xval, yval = item
                x = (xval - self.minxval) * self.xscale
                y = 1.0 - (yval - self.minyval) * self.yscale
                point = Point(x, clamp(0.0, 1.0, y), xval, yval, name)
                
                if 0.0 <= point.x <= 1.0:
                    self.points.append(point)
    
    def _renderChart(self, cx):
        """Renders a line chart"""        
        def preparePath(storeName):
            cx.new_path()
            cx.move_to(self.area.x, self.area.y + self.area.h)
            for point in self.points:
                if point.name == storeName:
                    cx.line_to(point.x * self.area.w + self.area.x,
                               point.y * self.area.h + self.area.y)
            cx.line_to(self.area.w + self.area.x, self.area.h + self.area.y)
            cx.line_to(self.area.x, self.area.y + self.area.h)

            if self.options.shouldFill:
                cx.close_path()
            else:
                cx.set_source_rgb(*self.options.colorScheme[storeName])
                cx.stroke()
        

        cx.save()
        cx.set_line_width(self.options.stroke.width)
        if self.options.shouldFill:
            def drawLine(storeName):
                if self.options.stroke.shadow:
                    # draw shadow
                    cx.save()
                    cx.set_source_rgba(0, 0, 0, 0.15)
                    cx.translate(2, -2)
                    preparePath(storeName)
                    cx.fill()
                    cx.restore()
                
                # fill the line
                cx.set_source_rgb(*self.options.colorScheme[storeName])
                preparePath(storeName)
                cx.fill()
                
                if not self.options.stroke.hide:
                    # draw stroke
                    cx.set_source_rgb(*hex2rgb(self.options.stroke.color))
                    preparePath(storeName)
                    cx.stroke()

            # draw the lines
            for key in self.getDataSetsKeys():
                drawLine(key)
        else:
            for key in self.getDataSetsKeys():
                preparePath(key)

        cx.restore()

class Point(object):
    def __init__(self, x, y, xval, yval, name):
        self.x, self.y = x, y
        self.xval, self.yval = xval, yval
        self.name = name