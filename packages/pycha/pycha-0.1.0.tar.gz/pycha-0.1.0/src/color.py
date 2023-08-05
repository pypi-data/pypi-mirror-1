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

def clamp(minValue, maxValue, value):
    if value < minValue:
        return minValue
    if value > maxValue:
        return maxValue
    return value
    
def hex2rgb(hexstring, top=255.0):
    if isinstance(hexstring, (tuple, list)):
        return hexstring

    r = int(hexstring[1:3], 16)
    g = int(hexstring[3:5], 16)
    b = int(hexstring[5:7], 16)
    return r / top, g / top, b / top

def lighten(r, g, b, amount):
    return (clamp(0.0, 1.0, r + amount),
            clamp(0.0, 1.0, g + amount),
            clamp(0.0, 1.0, b + amount))
    
def generateColorscheme(hex, keys):
    r, g, b = hex2rgb(hex)
    light = 0.098
    scheme = {}
    for key in keys:
        scheme[key] = lighten(r, g, b, light)
        light += 0.098
    return scheme

def defaultColorscheme(keys):
    return generateColorscheme('#3c581a', keys)

def getColorscheme(color, keys):
    return generateColorscheme(colorSchemes.get(color, color), keys)

colorSchemes = dict(
    red='#6d1d1d',
    green='#3c581a',
    blue='#224565',
    grey='#444444',
    black='#000000',
    darkcyan='#305755'
    )
