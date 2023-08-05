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

import cairo

from pycha.color import defaultColorscheme, getColorscheme, hex2rgb

class Chart(object):

    def __init__(self, surface, options={}):
        self.resetFlag = False

        # initialize storage hash
        self.dataSets = []

        # set the default options
        self.options = Option(
            axis=Option(
                lineWidth=1.0,
                lineColor='#000000',
                tickSize=3.0,
                labelColor='#666666',
                labelFont='Tahoma',
                labelFontSize=9,
                labelWidth=50.0,
                x=Option(
                    hide=False,
                    ticks=None,
                    tickCount=10,
                    tickPrecision=1,
                    range=None,
                ),
                y=Option(
                    hide=False,
                    ticks=None,
                    tickCount=10,
                    tickPrecision=1,
                    range=None,
                ),
            ),
            background=Option(
                color='#f5f5f5',
                hide=False,
                lineColor='#ffffff',
                lineWidth=1.5,
            ),
            legend=Option(
                opacity=0.8,
                borderColor='#000000',
                style={},
                hide=False,
                position=Option(top=20, left=40),
            ),
            padding=Option(
                left=30,
                right=30,
                top=15,
                bottom=15,
            ),
            stroke=Option(
                color='#ffffff',
                hide=False,
                shadow=True,
                width=2
            ),
            fillOpacity=1.0,
            shouldFill=True,
            barWidthFillFraction=0.75,
            xOriginIsZero=True,
            yOriginIsZero=True,
            pieRadius=0.4,
            colorScheme=defaultColorscheme(self.getDataSetsKeys()),
        )
        self.setOptions(options)

        # initialize the canvas
        self._initCanvas(surface)

    def addDataset(self, dataset):
        """Adds an object containing chart data to the storage hash"""
        self.dataSets += dataset

    def getDataSetsKeys(self):
        return [d[0] for d in self.dataSets]

    def getDataSetsValues(self):
        return [d[1] for d in self.dataSets]

    def setOptions(self, options={}):
        """Sets options of this chart"""
        self.options.merge(options)

    def reset(self):
        """Resets options and datasets"""
        self.resetFlag = True
        self.setOptions()
        self.dataSets = []

    def render(self, surface=None, options={}):
        """Renders the chart with the specified options.
        
        The optional parameters can be used to render a chart in a different
        surface with new options.
        """
        self._update(options)
        if surface:
            self._initCanvas(surface)
        
        cx = cairo.Context(self.surface)
        self._renderBackground(cx)
        self._renderChart(cx)
        self._renderAxis(cx)
        self._renderLegend(cx)

    def clean(self):
        """Clears a canvas tag.
        
        This removes all renderings including axis, legends etc
        """
        cx = cairo.Context(self.surface)
        cx.save()
        cx.set_source_rgb(1, 1, 1)
        cx.paint()
        cx.restore()

    def setColorscheme(self):
        """Sets the colorScheme used for the chart"""
        scheme = self.options.colorScheme
        keys = self.getDataSetsKeys()
        if isinstance(scheme, dict):
            if not scheme:
                self.options.colorScheme = defaultColorscheme(keys)
            return
        elif isinstance(scheme, basestring):
            self.options.colorScheme = getColorscheme(scheme, keys)
        else:
            raise TypeError("Color scheme is invalid!")

    def _initCanvas(self, surface):
        if self.resetFlag:
            self.resetFlag = False
            self.clean()
        
        self.surface = surface

    # update methods
    def _update(self, options={}):
        """Everytime a chart is rendered, we need to evaluate metric for
        the axis"""
        self.setOptions(options)
        self.stores = self.getDataSetsValues()
        self._updateXY()
        self.setColorscheme()
        self._updateChart()
        self._updateTicks()

    def _updateXY(self):
        """Calculates all kinds of metrics for the x and y axis"""
        
        # calculate area data
        width = (self.surface.get_width()
                 - self.options.padding.left - self.options.padding.right)
        height = (self.surface.get_height()
                  - self.options.padding.top - self.options.padding.bottom)
        self.area = Area(self.options.padding.left,
                         self.options.padding.top,
                         width, height)

        # gather data for the x axis
        if self.options.axis.x.range:
            self.minxval, self.maxxval = self.options.axis.x.range
            self.xscale = self.maxxval - self.minxval
        else:
            xdata = [pair[0] for pair in reduce(lambda a,b: a+b, self.stores)]
            self.minxval = 0.0 if self.options.xOriginIsZero else float(min(xdata))
            self.maxxval = float(max(xdata))

        self.xrange = self.maxxval - self.minxval
        self.xscale = 1.0 if self.xrange == 0 else 1 / self.xrange

        # gather data for the y axis
        if self.options.axis.y.range:
            self.minyval, self.maxyval = self.options.axis.y.range
            self.yscale = self.maxyval - self.minyval
        else:
            ydata = [pair[1] for pair in reduce(lambda a,b: a+b, self.stores)]
            self.minyval = 0.0 if self.options.yOriginIsZero else float(min(ydata))
            self.maxyval = float(max(ydata))

        self.yrange = self.maxyval - self.minyval
        self.yscale = 1.0 if self.yrange == 0 else 1 / self.yrange

    def _updateChart(self):
        raise NotImplementedError

    def _updateTicks(self):
        """Evaluates ticks for x and y axis"""
        
        # evaluate xTicks
        self.xticks = []
        if self.options.axis.x.ticks:
            for tick in self.options.axis.x.ticks:
                if not isinstance(tick, Option):
                    tick = Option(tick)
                label = str(tick.v) if tick.label is None else tick.label
                pos = self.xscale * (tick.v - self.minxval)
                if 0.0 <= pos <= 1.0:
                    self.xticks.append((pos, label))

        elif self.options.axis.x.tickCount > 0:
            uniqx = range(len(uniqueIndices(self.stores)) + 1)
            roughSeparation = self.xrange / self.options.axis.x.tickCount

            i = j = 0
            while i + 1 < len(uniqx) and j < self.options.axis.x.tickCount:
                if (uniqx[i + 1] - self.minxval) >= (j * roughSeparation):
                    pos = self.xscale * (uniqx[i] - self.minxval)
                    if 0.0 <= pos <= 1.0:
                        self.xticks.append((pos, uniqx[i + 1]))
                        j += 1
                i += 1

        # evaluate yTicks
        self.yticks = []
        if self.options.axis.y.ticks:
            for tick in self.options.y.ticks:
                if not isinstance(tick, Option):
                    tick = Option(tick)
                label = str(tick.v) if tick.label is None else tick.label
                pos = self.yscale * (tick.v - self.minyval)
                if 0.0 <= pos <= 1.0:
                    self.yticks.append((pos, label))

        elif self.options.axis.y.tickCount > 0:
            prec = self.options.axis.y.tickPrecision
            num = self.yrange / self.options.axis.y.tickCount
            roughSeparation = 1 if (num < 1 and prec == 0) else round(num, prec)
            
            for i in range(self.options.axis.y.tickCount + 1):
                yval = self.minyval + (i * roughSeparation)
                pos = 1.0 - ((yval - self.minyval) * self.yscale)
                if 0.0 <= pos <= 1.0:
                    self.yticks.append((pos, round(yval, prec)))
            
    # render methods
    def _renderBackground(self, cx):
        """Renders the background of the chart"""
        if self.options.background.hide:
            return
        
        cx.save()
        cx.set_source_rgb(*hex2rgb(self.options.background.color))
        cx.rectangle(self.area.x, self.area.y, self.area.w, self.area.h)
        cx.fill()
        cx.set_source_rgb(*hex2rgb(self.options.background.lineColor))
        cx.set_line_width(self.options.axis.lineWidth)
        
        self._renderLines(cx)
        
        cx.restore()

    def _renderLines(self, cx):
        """Aux function for _renderBackground"""
        ticks = self.yticks
        for tick in ticks:
            self._renderLine(cx, tick, False)
        
    def _renderLine(self, cx, tick, horiz):
        x1, x2, y1, y2 = (0, 0, 0, 0)
        if horiz:
            x1 = x2 = tick[0] * self.area.w + self.area.x
            y1 = self.area.y
            y2 = y1 + self.area.h
        else:
            x1 = self.area.x
            x2 = x1 + self.area.w
            y1 = y2 = tick[0] * self.area.h + self.area.y

        cx.new_path()
        cx.move_to(x1, y1)
        cx.line_to(x2, y2)
        cx.close_path()
        cx.stroke()

    def _renderChart(self, cx):
        raise NotImplementedError

    def _renderAxis(self, cx):
        """Renders axis"""
        if self.options.axis.x.hide and self.options.axis.y.hide:
            return
        
        cx.save()
        cx.set_source_rgb(*hex2rgb(self.options.axis.lineColor))
        cx.set_line_width(self.options.axis.lineWidth)
        
        if not self.options.axis.y.hide:
            if self.yticks:
                def collectYLabels(tick):
                    if callable(tick):
                        return
                    
                    x = self.area.x
                    y = self.area.y + tick[0] * self.area.h
                    
                    cx.new_path()
                    cx.move_to(x, y)
                    cx.line_to(x - self.options.axis.tickSize, y)
                    cx.close_path()
                    cx.stroke()
                    
                    label =  unicode(tick[1])
                    extents = cx.text_extents(label)
                    labelWidth = extents[2]
                    labelHeight = extents[3]
                    cx.move_to(x - self.options.axis.tickSize - labelWidth - 5,
                               y + labelHeight / 2.0)
                    cx.show_text(label)
                    
                    return label
                self.ylabels = [collectYLabels(tick) for tick in self.yticks]
                
            cx.new_path()
            cx.move_to(self.area.x, self.area.y)
            cx.line_to(self.area.x, self.area.y + self.area.h)
            cx.close_path()
            cx.stroke()

        if not self.options.axis.x.hide:
            if self.xticks:
                def collectXLabels(tick):
                    if callable(tick):
                        return
                    
                    x = self.area.x + tick[0] * self.area.w
                    y = self.area.y + self.area.h
                    
                    cx.new_path()
                    cx.move_to(x, y)
                    cx.line_to(x, y + self.options.axis.tickSize)
                    cx.close_path()
                    cx.stroke()
                    
                    label = unicode(tick[1])
                    extents = cx.text_extents(label)
                    labelWidth = extents[2]
                    labelHeight = extents[3]
                    cx.move_to(x - labelWidth / 2.0,
                               y + self.options.axis.tickSize + 10)
                    cx.show_text(label)
                    return label
                self.xlabels = [collectXLabels(tick) for tick in self.xticks]
            
            cx.new_path()
            cx.move_to(self.area.x, self.area.y + self.area.h)
            cx.line_to(self.area.x + self.area.w, self.area.y + self.area.h)
            cx.close_path()
            cx.stroke()

        cx.restore()

    def _renderLegend(self, cx):
        """This function adds a legend to the chart"""
        if self.options.legend.hide:
            return
        
        padding = 4
        bullet = 15
        width = 0
        height = padding
        keys = self.getDataSetsKeys()
        for key in self.getDataSetsKeys():
            extents = cx.text_extents(key)
            width = max(extents[2], width)
            height += max(extents[3], bullet) + padding
        width = padding + bullet + padding + width + padding

        cx.save()
        cx.rectangle(self.options.legend.position.left,
                     self.options.legend.position.top,
                     width, height)
        cx.set_source_rgba(1, 1, 1, self.options.legend.opacity)
        cx.fill_preserve()
        cx.set_line_width(self.options.stroke.width)
        cx.set_source_rgb(*hex2rgb(self.options.legend.borderColor))
        cx.stroke()
        
        def drawKey(key, x, y, text_height):
            cx.rectangle(x, y, bullet, bullet)
            cx.set_source_rgb(*self.options.colorScheme[key])
            cx.fill_preserve()
            cx.set_source_rgb(0, 0, 0)
            cx.stroke()
            cx.move_to(x + bullet + padding,
                       y + bullet / 2.0 + text_height / 2.0)
            cx.show_text(key)
        
        cx.set_line_width(1)
        x = self.options.legend.position.left + padding
        y = self.options.legend.position.top + padding
        for key in keys:
            extents = cx.text_extents(key)
            drawKey(key, x, y, extents[3])
            y += max(extents[3], bullet) + padding

        cx.restore()

def uniqueIndices(arr):
    return range(max([len(a) for a in arr]))
            
class Area(object):
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

class Option(dict):
    def __getattr__(self, name):
        if name in self.keys():
            return self[name]
        else:
            raise AttributeError(name)

    def merge(self, other):
        for key, value in other.items():
            if self.has_key(key):
                if isinstance(self[key], Option):
                    self[key].merge(other[key])
                else:
                    self[key] = other[key]