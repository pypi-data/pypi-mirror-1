#!/usr/bin/env python

"""
maths.py - Classes to describe mathematical markup in TechWriter documents.

Copyright (C) 2007 David Boddie <david@boddie.org.uk>

This file is part of the TechWriter Python package.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


class MathsObject:

    def __init__(self, *arguments):
    
        self.arguments = arguments

class Group(MathsObject):

    pass

class Division(MathsObject):

    pass

class Sqrt(MathsObject):

    pass

class InlineText(MathsObject):

    pass

class Subscript(MathsObject):

    pass

class Superscript(MathsObject):

    pass

class SubAndSuperscript(MathsObject):

    pass

