#!/usr/bin/env python

"""
opendocumentwriter.py - An OpenDocument writer module for the TechWriter
                        Python package.

Copyright (C) 2008 David Boddie <david@boddie.org.uk>

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

import os, string
from odf.opendocument import OpenDocumentText
import odf.draw
import odf.grammar
import odf.math
import odf.namespaces
import odf.style
from odf.text import H, P, Span

from TechWriter.objects import *
from TechWriter.maths import *
from TechWriter.text import *


class OOObject:

    charmap = {
        0x91: u"'",
        0x94: unichr(8220),
        0x95: unichr(8221),
        0x97: unichr(8212),
        0xfb: unichr(8706)
        }
    
    def __init__(self, writer):
    
        self.writer = writer
    
    def markup(self, text):
    
        text = text.replace("\r", "\n").replace("\0", "")
        new_text = []
        for char in text:
            if ord(char) in self.charmap:
                new_text.append(self.charmap[ord(char)])
            else:
                new_text.append(unicode(char, self.writer.encoding))
        
        return u"".join(new_text)


class OOTextWriter(OOObject):

    def write(self, obj, element):
    
        self._write(obj.inline_styles(), element)
    
    def _write(self, objects, element):
    
        for obj in objects:
        
            if isinstance(obj, BaseText):
                element.addText(self.markup(obj.text))
            
            elif isinstance(obj, Effect):
                style_data = obj.style
                span = Span(stylename = self.writer.styles[style_data.id()],
                            text = self.markup(obj.text))
                element.addElement(span)
            
            elif isinstance(obj, Object):
                self.writer.add_structure(obj)


class MathMLElement(odf.math.Element):

    def __init__(self, name, **attributes):
    
        odf.math.Element.__init__(self, qname = (odf.namespaces.MATHNS, name),
                                  **attributes)

def CN(text):
    element = MathMLElement(u"cn")
    element.addText(text)
    return element

def CI(text):
    element = MathMLElement(u"ci")
    element.addText(text)
    return element

def CSYMBOL(text):
    element = MathMLElement(u"csymbol")
    element.addText(text)
    return element

def MN(text):
    element = MathMLElement(u"mn")
    element.addText(text)
    return element

def MI(text, style = None):
    attributes = {}
    if style:
        attributes[(odf.namespaces.MATHNS, u"mathvariant")] = style
    
    element = MathMLElement(u"mi", attributes = attributes)
    element.addText(text)
    return element

def MO(text):
    element = MathMLElement(u"mo")
    element.addText(text)
    return element

def MTEXT(text, style = None):
    attributes = {}
    if style:
        attributes[(odf.namespaces.MATHNS, u"mathvariant")] = style
    
    element = MathMLElement(u"mtext", attributes = attributes)
    element.addText(text)
    return element

odf.grammar.allows_text += (
    (odf.namespaces.MATHNS, u"cn"),
    (odf.namespaces.MATHNS, u"ci"),
    (odf.namespaces.MATHNS, u"csymbol"),
    (odf.namespaces.MATHNS, u"mn"),
    (odf.namespaces.MATHNS, u"mi"),
    (odf.namespaces.MATHNS, u"mo"),
    (odf.namespaces.MATHNS, u"mtext")
    )


class OOMathsWriter(OOObject):

    charmap = {
        0x40: unichr(183),
        0x91: u"(-+)",
        0x96: unichr(8734),
        0xa7: unichr(167),
        0xac: unichr(8801),
        0xae: MathMLElement(u"approx"), # unichr(8773),
        0xc6: unichr(8804),
        0xc9: unichr(8747),
        0xd7: unichr(215),
        0xdb: unichr(8711),
        0xe1: unichr(732),
        0xee: unichr(8594),
        0xfb: unichr(8706)
        }
    
    greek = {
        "A": unichr(913), "B": unichr(914), "C": unichr(915), "D": unichr(916),
        "E": unichr(917), "Z": unichr(918), "H": unichr(919), "": unichr(920),
        "I": unichr(921), "K": unichr(922), "L": unichr(923), "M": unichr(924),
        "N": unichr(925), "X": unichr(926), "O": unichr(927), "P": unichr(928),
        "R": unichr(929), "S": unichr(931), "T": unichr(932), "": unichr(933),
        "V": unichr(934), "F": unichr(935), "Y": unichr(936), "W": unichr(937),
        "a": unichr(945), "b": unichr(946), "c": unichr(947), "d": unichr(948),
        "e": unichr(949), "z": unichr(950), "g": unichr(951), "h": unichr(952),
        "i": unichr(953), "k": unichr(954), "l": unichr(955), "m": unichr(956),
        "n": unichr(957), "x": unichr(958), "o": unichr(959), "p": unichr(960),
        "r": unichr(961), "": unichr(962), "s": unichr(963), "t": unichr(964),
        "": unichr(965), "f": unichr(966), "v": unichr(967), "y": unichr(968),
        "w": unichr(969)
    }
    
    mathphys_greek = {
        "A": "&Alpha;", "B": "&Beta;", "X": "&Chi;", "D": "&Delta;",
        "E": "&Epsilon;", "F": "&Phi;", "G": "&Gamma;", "H": "&Eta;",
        "I": "&Iota;", "J": "&phi;",  "K": "&Kappa;", "L": "&Lambda;",
        "M": "&Mu;",   "N": "&Nu;",   "O": "&Omicron;", "P": "&Pi;",
        "Q": "&Theta;", "R": "&Rho;", "S": "&Sigma;", "T": "&Tau;",
        "": "&Upsilon;", "V": "&#935;", "W": "&Omega;", "X": "&Xi;",
        "Y": "&Psi;", "Z": "&Zeta;",
        "a": "&alpha;", "b": "&beta;", "c": "&chi;", "d": "&delta;",
        "e": "&epsilon;", "f": "&phi;", "g": "&gamma;", "h": "&eta;",
        "i": "&iota;", "j": "&phi;", "k": "&kappa;", "l": "&lambda;",
        "m": "&mu;",   "n": "&nu;",   "o": "&omicron;", "p": "&pi;",
        "q": "&theta;", "r": "&rho;", "s": "&sigma;", "t": "&tau;",
        "": "&upsilon;", "v": "&#935;", "w": "&omega;", "x": "&xi;",
        "y": "&psi;", "z": "&zeta;"
    }
    
    def __init__(self, writer):
    
        self.writer = writer
    
    def decode(self, text):
    
        new_text = u""
        for c in str(text):
            new_text += self.charmap.get(ord(c), unicode(c, self.writer.encoding))
        return new_text
    
    def markup(self, text, mathphys = False):
    
        text = text.replace("\r", "\n").replace("\0", "")
        new_text = []
        current = u""
        for char in text:
            if mathphys and char in self.greek:
                if current:
                    new_text.append(current)
                new_text.append(self.greek[char])
                current = u""
            elif ord(char) in self.charmap:
                if current:
                    new_text.append(current)
                new_text.append(self.charmap[ord(char)])
                current = u""
            else:
                current += unicode(char, self.writer.encoding)
        
        if current:
            new_text.append(current)
        
        return new_text
    
    def write(self, maths, element):
    
        mrow = MathMLElement(u"mrow")
        self._write(maths.parse(), mrow)
        element.addElement(mrow)
    
    def _write(self, objects, element):
    
        for obj in objects:
        
            if isinstance(obj, Effect):
                if isinstance(obj, Italic):
                    for text in self.markup(obj.text):
                        if not isinstance(text, MathMLElement):
                            text = MI(text, style = u"italic")
                        element.addElement(text)
                elif isinstance(obj, Bold):
                    for text in self.markup(obj.text):
                        if not isinstance(text, MathMLElement):
                            text = MI(text, style = u"bold")
                        element.addElement(text)
                elif isinstance(obj, MathPhys):
                    for text in self.markup(obj.text, mathphys = True):
                        if not isinstance(text, MathMLElement):
                            text = MI(text, style = u"italic")
                        element.addElement(text)
                else:
                    for text in self.markup(obj.text):
                        if not isinstance(text, MathMLElement):
                            text = MN(text)
                        element.addElement(text)
            
            elif isinstance(obj, MathsObject):
            
                if isinstance(obj, Sqrt):
                    msqrt = MathMLElement(u"msqrt")
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[:1], mrow)
                    msqrt.addElement(mrow)
                    element.addElement(msqrt)
                
                elif isinstance(obj, Group):
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[:1], mrow)
                    element.addElement(mrow)
                
                elif isinstance(obj, Division):
                    mfrac = MathMLElement(u"mfrac")
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[:1], mrow)
                    mfrac.addElement(mrow)
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[1:2], mrow)
                    mfrac.addElement(mrow)
                    element.addElement(mfrac)
                
                elif isinstance(obj, InlineText):
                    mtext = MTEXT(self.markup(obj.arguments[0]))
                    element.addElement(mtext)
                
                elif isinstance(obj, Subscript):
                    msub = MathMLElement(u"msub")
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[:1], mrow)
                    msub.addElement(mrow)
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[1:2], mrow)
                    msub.addElement(mrow)
                    element.addElement(msub)
                
                elif isinstance(obj, Superscript):
                    msup = MathMLElement(u"msup")
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[:1], mrow)
                    msup.addElement(mrow)
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[1:2], mrow)
                    msup.addElement(mrow)
                    element.addElement(msup)
                
                elif isinstance(obj, SubAndSuperscript):
                    msub = MathMLElement(u"msub")
                    msup = MathMLElement(u"msup")
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[:1], mrow)
                    msup.addElement(mrow)
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[1:2], mrow)
                    msup.addElement(mrow)
                    msub.addElement(msup)
                    mrow = MathMLElement(u"mrow")
                    self._write(obj.arguments[2:3], mrow)
                    msub.addElement(mrow)
                    element.addElement(msub)
            else:
                self._write(obj, element)


class OpenDocumentWriter:

    paragraph_styles = (StyleInfo.Document, StyleInfo.Chapter, StyleInfo.Section)
    
    def __init__(self, document):
    
        self.document = document
        self.opendocument = OpenDocumentText()
        self.encoding = "iso8859-1"
        self.writers = {}
    
    def write(self, output_path):
    
        self.styles = {}
        self.outline_level = 1
        self.add_styles()
        self.add_structure(self.document.document_structure)
        self.opendocument.save(output_path)
    
    def add_structure(self, structure):
    
        if isinstance(structure, Maths):
        
            writer = self.writers.setdefault(Maths, OOMathsWriter(self))
            paragraph = odf.text.P(stylename = self.styles[structure.style.name])
            frame = odf.draw.Frame(relwidth = u"scalemin", relheight = u"scalemin",
                                   anchortype = u"paragraph", stylename = self.styles[u"__equation__"])
            obj = odf.draw.Object()
            element = odf.math.Math()
            writer.write(structure, element)
            obj.addElement(element)
            frame.addElement(obj)
            paragraph.addElement(frame)
            self.opendocument.text.addElement(paragraph)
        
        if isinstance(structure, Text):
        
            writer = self.writers.setdefault(Text, OOTextWriter(self))
            element = odf.text.P(stylename = self.styles[structure.style.name])
            writer.write(structure, element)
            self.opendocument.text.addElement(element)
        
        elif isinstance(structure, TitledStructure):
        
            # Show the first element inside the structure using the structure's
            # own style.
            try:
                heading = structure.objects[0]
                if isinstance(heading, Text):
                    writer = self.writers.setdefault(Text, OOTextWriter(self))
                    element = H(outlinelevel = self.outline_level,
                                stylename = self.styles[structure.style.name])
                    writer.write(heading, element)
                    self.opendocument.text.addElement(element)
                else:
                    print ("Unexpected structure (%s) in place of text "
                           "heading at %x") % (heading, structure.location)
                
                # Descend into the structure.
                self.outline_level += 1
                for obj in structure.objects[1:]:
                    self.add_structure(obj)
                self.outline_level -= 1
            
            except IndexError:
                print "Incomplete/empty structure at %x" % structure.location
        
        elif isinstance(structure, Structure):
        
            # Descend into the structure, if appropriate.
            for obj in structure.objects:
                self.add_structure(obj)
    
    def add_styles(self):
    
        for style_data in self.document.definitions:
        
            if not isinstance(style_data, StyleData):
                continue
            
            info = style_data.info()
            
            if style_data.type in self.paragraph_styles:
                style = odf.style.Style(name = style_data.id(), family = u"paragraph")
            else:
                style = odf.style.Style(name = style_data.id(), family = u"text")
            
            self.styles[style_data.id()] = style
            
            attributes = {}
            
            if info.get("bold", False) or "Bold" in info.get("font_name", ""):
                attributes[u"fontweight"] = u"bold"
            
            if info.get("italic", False) or "Italic" in info.get("font_name", ""):
                attributes[u"fontstyle"] = u"italic"
            
            style.addElement(odf.style.TextProperties(attributes = attributes))
            if style_data.name == style_data.id():
                self.opendocument.styles.addElement(style)
            else:
                self.opendocument.automaticstyles.addElement(style)
        
        style = odf.style.Style(name = u"__equation__", family = "graphic")
        style.addElement(odf.style.GraphicProperties(
            attributes = {u"wrap": u"none"}))
        self.opendocument.styles.addElement(style)
        self.styles[u"__equation__"] = style
