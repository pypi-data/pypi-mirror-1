#!/usr/bin/env python

"""
htmlwriter.py - Classes for writing HTML representations of TechWriter
                documents.

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


import os, string

from TechWriter.objects import *
from TechWriter.maths import *
from TechWriter.text import *


class HTMLObject:

    charmap = {
        0x40: "&middot;",
        0x91: "(-+)",
        0x96: "&infin;",
        0xa7: "&sect;",
        0xac: "&equiv;",
        0xae: "&cong;",
        0xc6: "&le;",
        0xc9: "&int;",
        0xdb: "&nabla;",
        0xe1: "&tilde;",
        0xee: "&rArr;",
        0xfb: "&part;"
        }
    
    def __init__(self, writer):
    
        self.writer = writer
    
    def markup(self, text):
    
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class HTMLTextWriter(HTMLObject):

    def write(self, obj):
    
        return self._write(obj.inline_styles())
    
    def _write(self, objects):
    
        text = ""
        for obj in objects:
        
            if isinstance(obj, BaseText):
                text += self.markup(obj.text)
            
            elif isinstance(obj, Effect):
                style_data = obj.style
                text += '<span class="%s">' % style_data.id() + \
                        self.markup(obj.text) + "</span>"
            
            elif isinstance(obj, Object):
                self.writer.output_file.write(text)
                self.writer.write_structure(obj)
                text = ""
        
        return text


class HTMLMathsWriter(HTMLObject):

    greek = {
        "A": "&#913;", "B": "&#914;", "C": "&#915;", "D": "&#916;",
        "E": "&#917;", "Z": "&#918;", "H": "&#919;", "": "&#920;",
        "I": "&#921;", "K": "&#922;", "L": "&#923;", "M": "&#924;",
        "N": "&#925;", "X": "&#926;", "O": "&#927;", "P": "&#928;",
        "R": "&#929;", "S": "&#931;", "T": "&#932;", "": "&#933;",
        "V": "&#934;", "F": "&#935;", "Y": "&#936;", "W": "&#937;",
        "a": "&#945;", "b": "&#946;", "c": "&#947;", "d": "&#948;",
        "e": "&#949;", "z": "&#950;", "g": "&#951;", "h": "&#952;",
        "i": "&#953;", "k": "&#954;", "l": "&#955;", "m": "&#956;",
        "n": "&#957;", "x": "&#958;", "o": "&#959;", "p": "&#960;",
        "r": "&#961;", "": "&#962;", "s": "&#963;", "t": "&#964;",
        "": "&#965;", "f": "&#966;", "v": "&#967;", "y": "&#968;",
        "w": "&#969;"
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
    
        new_text = ""
        for c in str(text):
            new_text += self.charmap.get(ord(c), c)
        return new_text
    
    def write(self, maths):
    
        text = self._write(maths.parse())
        return "".join(map(self.decode, text))
    
    def _write(self, objects):
    
        text = ""
        
        for obj in objects:
        
            if isinstance(obj, Effect):
                if isinstance(obj, Italic):
                    text += "<i>" + self.markup(obj.text) + "</i>"
                elif isinstance(obj, Bold):
                    text += "<b>" + self.markup(obj.text) + "</b>"
                elif isinstance(obj, MathPhys):
                    text += self.mathphys_greek.get(obj.text, obj.text)
                else:
                    text += self.markup(obj.text)
            
            elif isinstance(obj, MathsObject):
            
                if isinstance(obj, Sqrt):
                    text += "&radic;[" + self._write(obj.arguments[:1]) + "]"
                
                elif isinstance(obj, Division):
                    text += "(" + self._write(obj.arguments[:1]) + "/" + \
                            self._write(obj.arguments[1:2]) + ")"
                
                elif isinstance(obj, InlineText):
                    self.writer.output_file.write(text)
                    self.writer.write_structure(obj.arguments[0])
                    text = ""
                
                elif isinstance(obj, Subscript):
                    text += self._write(obj.arguments[:1]) + "<sub>" + \
                            self._write(obj.arguments[1:2]) + "</sub>"
                
                elif isinstance(obj, Superscript):
                    text += self._write(obj.arguments[:1]) + "<sup>" + \
                            self._write(obj.arguments[1:2]) + "</sup>"
                
                elif isinstance(obj, SubAndSuperscript):
                    text += self._write(obj.arguments[:1]) + "<sup>" + \
                            self._write(obj.arguments[1:2]) + "</sup><sub>" + \
                            self._write(obj.arguments[2:3]) + "</sub>"
            else:
                text += self._write(obj)
        
        return text


class HTMLWriter:

    def __init__(self, document):
    
        self.document = document
        self.writers = {}
    
    def write(self, output_path, styles_name):
    
        self.styles = {}
        
        self.output_file = open(output_path, "w")
        self.write_header(styles_name)
        self.write_structure(self.document.document_structure)
        self.write_footer()
        self.output_file.close()
        
        styles_path = os.path.join(os.path.split(output_path)[0], styles_name)
        
        self.write_styles(open(styles_path, "w"))
    
    def write_header(self, styles_name):
    
        file_name = os.path.split(self.document.input_path)[1]
        
        self.output_file.write(
            "<html>\n"
            "<head>\n"
            "  <title>" + self.html(file_name) + "</title>\n"
            '  <link rel="stylesheet" type="text/css" href="' + styles_name + '" />\n'
            "</head>\n"
            "<body>\n"
            )
    
    def write_footer(self):
    
        self.output_file.write(
            "</body>\n"
            "</html>\n"
            )
    
    def html(self, text):
    
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    def quote(self, text):
    
        new_text = ""
        for char in text:
            if char not in string.letters + string.digits:
                new_text += "_"
            else:
                new_text += char
        return new_text
    
    def write_structure(self, structure):
    
        if isinstance(structure, Maths):
        
            writer = self.writers.setdefault(Maths, HTMLMathsWriter(self))
            self.output_file.write(
                "\n<div>\n" + writer.write(structure) + "</div>\n"
                )
        
        elif isinstance(structure, Text):
        
            writer = self.writers.setdefault(Text, HTMLTextWriter(self))
            self.output_file.write(
                '<p class="%s">\n' % self.quote(structure.style.name) + \
                writer.write(structure) + "</p>\n"
                )
        
        elif isinstance(structure, TitledStructure):
        
            # Show the first element inside the structure using the structure's
            # own style.
            try:
                heading = structure.objects[0]
                if isinstance(heading, Text):
                    writer = self.writers.setdefault(Text, HTMLTextWriter(self))
                    self.output_file.write(
                        '<p class="%s">\n' % self.quote(structure.style.name) + \
                        writer.write(heading) + "</p>\n"
                        )
                else:
                    print ("Unexpected structure (%s) in place of text "
                           "heading at %x") % (heading, structure.location)
                
                # Descend into the structure.
                for obj in structure.objects[1:]:
                    self.write_structure(obj)
            
            except IndexError:
                print "Incomplete/empty structure at %x" % structure.location
        
        elif isinstance(structure, Structure):
        
            # Descend into the structure, if appropriate.
            for obj in structure.objects:
                self.write_structure(obj)
    
    def write_styles(self, styles_file):
    
        for style_data in self.document.definitions:
        
            if not isinstance(style_data, StyleData):
                continue
            
            info = style_data.info()
            lines = []
            
            if info.get("bold", False) or "Bold" in info.get("font_name", ""):
                lines.append("font-weight: bold")
            
            if info.get("italic", False) or "Italic" in info.get("font_name", ""):
                lines.append("font-style: italic")
            
            styles_file.write(
                ".%s {\n" % self.quote(style_data.id()) +
                "\n;".join(lines) +
                "\n}\n\n"
                )
