#!/usr/bin/env python

"""
text.py - Classes to describe text effects and styles in TechWriter documents.

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


class Effect:

    def __init__(self, text, style = None):
    
        self.text = text
        self.style = style
    
    def __repr__(self):
    
        if hasattr(self.style, "name"):
            name = self.style.name or "untitled"
        else:
            name = "no"
        return "<Effect ("+name+" style): "+repr(self.text)+">"

class BaseText(Effect):

    def __repr__(self):
    
        return "<BaseText: "+repr(self.text)+">"

class Italic(Effect):

    def __repr__(self):
    
        return "<Italic: "+repr(self.text)+">"

class Bold(Effect):

    def __repr__(self):
    
        return "<Bold: "+repr(self.text)+">"

class MathPhys(Effect):

    def __repr__(self):
    
        return "<MathPhys: "+repr(self.text)+">"

class Greek(Effect):

    def __repr__(self):
    
        return "<Greek: "+repr(self.text)+">"
