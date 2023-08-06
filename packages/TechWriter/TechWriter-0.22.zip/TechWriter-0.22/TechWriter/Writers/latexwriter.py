#!/usr/bin/env python

"""
latexwriter.py - Classes for writing LaTeX representations of TechWriter
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


class LaTeXObject:

    charmap = {}
    
    text_charmap = {
        0x91: r"'",
        0x94: r"``",
        0x95: r"''",
        0x97: r"\textemdash ",
        }
    
    maths_charmap = {
        0x40: r"\cdot ",
        0x91: r"\mp ",
        0x96: r"\infty ",
        0xa7: r"\textsection ",
        0xac: r"\equiv ",
        0xae: r"\cong ",
        0xc6: r"\leq ",
        0xc9: r"\int ",
        0xd7: r"\times ",
        0xdb: r"\nabla ",
        0xe1: r"\tilde ",
        0xee: r"\rightarrow ",
        0xfb: r"\partial "
        }
    
    def __init__(self, writer):
    
        self.writer = writer
    
    def markup(self, text):
    
        #self.write_output("\n% " + text + "\n")
        text = text.replace("\\", "\\\\").replace("&", "\\&")
        text = text.replace("\r", "\n").replace("\0", "")
        text = text.replace("{", "\\{").replace("}", "\\}")
        new_text = ""
        for char in text:
            new_text += self.charmap.get(ord(char), char)
        
        return new_text
    
    def write_output(self, text):
    
        self.writer.output_file.write(text)


class LaTeXTextWriter(LaTeXObject):

    def __init__(self, writer):
    
        LaTeXObject.__init__(self, writer)
        self.charmap = self.text_charmap.copy()
        for key, value in self.maths_charmap.items():
            if key not in self.charmap:
                self.charmap[key] = "$"+value+"$"
    
    def write(self, obj):
    
        self._write(obj.inline_styles())
    
    def _write(self, objects):
    
        for obj in objects:
        
            if isinstance(obj, BaseText):
                self.write_output(self.markup(obj.text))
            
            elif isinstance(obj, Effect):
                if obj.style and hasattr(obj.style, "name"):
                    self.write_output('\n%% %s\n' % obj.style.name)
                self.write_output(self.markup(obj.text))
            
            elif isinstance(obj, Object):
                self.writer.write_structure(obj, inline = True)


class LaTeXMathsWriter(LaTeXObject):

    greek = {
        "A": r"\Alpha ", "B": r"\Beta ", "C": r"\Gamma ", "D": r"\Delta ",
        "E": r"\Epsilon ", "Z": r"\Zeta ", "H": r"\Eta ", "": r"\Theta ",
        "I": r"\Iota ", "K": r"\Kappa ", "L": r"\Lambda ", "M": r"\Mu ",
        "N": r"\Nu ", "X": r"\Xi ", "O": r"\Omicron ", "P": r"\Pi ",
        "R": r"\Rho ", "S": r"\Sigma ", "T": r"\Tau ", "": r"\Upsilon ",
        "V": r"\Phi ", "F": r"\Chi ", "Y": r"\Psi ", "W": r"\Omega ",
        "a": r"\alpha ", "b": r"\beta ", "c": r"\gamma ", "d": r"\delta ",
        "e": r"\epsilon ", "z": r"\zeta ", "g": r"\eta ", "h": r"\theta ",
        "i": r"\iota ", "k": r"\kappa ", "l": r"\lambda ", "m": r"\mu ",
        "n": r"\nu ", "x": r"\xi ", "o": r"\omicron ", "p": r"\pi ",
        "r": r"\rho ", "": r"\sigmaf ", "s": r"\sigma ", "t": r"\tau ",
        "":  r"\upsilon ", "f": r"\phi ", "v": r"\chi ", "y": r"\psi ",
        "w": r"\omega "
    }
    
    mathphys_greek = {
        "A": r"\Alpha ", "B": r"\Beta ", "X": r"\Chi ", "D": r"\Delta ",
        "E": r"\Epsilon ", "F": r"\Phi ", "G": r"\Gamma ", "H": r"\Eta ",
        "I": r"\Iota ", "J": r"\phi ",  "K": r"\Kappa ", "L": r"\Lambda ",
        "M": r"\Mu ",   "N": r"\Nu ",   "O": r"\Omicron ", "P": r"\Pi ",
        "Q": r"\Theta ", "R": r"\Rho ", "S": r"\Sigma ", "T": r"\Tau ",
        "": r"\Upsilon ", "V": r"\Chi ", "W": r"\Omega ", "X": r"\Xi ",
        "Y": r"\Psi ", "Z": r"\Zeta ",
        "a": r"\alpha ", "b": r"\beta ", "c": r"\chi ", "d": r"\delta ",
        "e": r"\epsilon ", "f": r"\phi ", "g": r"\gamma ", "h": r"\eta ",
        "i": r"\iota ", "j": r"\phi ", "k": r"\kappa ", "l": r"\lambda ",
        "m": r"\mu ",   "n": r"\nu ",   "o": r"\omicron ", "p": r"\pi ",
        "q": r"\theta ", "r": r"\rho ", "s": r"\sigma ", "t": r"\tau ",
        "": r"\upsilon ", "v": r"\chi ", "w": r"\omega ", "x": r"\xi ",
        "y": r"\psi ", "z": r"\zeta "
    }
    
    def __init__(self, writer):
    
        LaTeXObject.__init__(self, writer)
        self.charmap = self.maths_charmap.copy()
        for key, value in self.text_charmap.items():
            if key not in self.charmap:
                self.charmap[key] = "\\textrm{"+value+"}"
    
    def decode(self, text):
    
        new_text = ""
        for c in str(text):
            new_text += self.charmap.get(ord(c), c)
        return new_text
    
    def write(self, maths):
    
        self._write(maths.parse())
    
    def _write(self, objects):
    
        for obj in objects:
        
            #self.write_output("\n% " + self.markup(repr(obj)) + "\n")
        
            if isinstance(obj, Effect):
                if isinstance(obj, Italic):
                    self.write_output("{\\it " + self.markup(obj.text) + "}")
                elif isinstance(obj, Bold):
                    self.write_output("{\\bf " + self.markup(obj.text) + "}")
                elif isinstance(obj, MathPhys):
                    self.write_output(self.mathphys_greek.get(obj.text, self.markup(obj.text)))
                else:
                    self.write_output(self.markup(obj.text))
            
            elif isinstance(obj, MathsObject):
            
                if isinstance(obj, Sqrt):
                    self.write_output("\\sqrt{")
                    self._write(obj.arguments[:1])
                    self.write_output("}")
                
                elif isinstance(obj, Group):
                    self._write(obj.arguments[:1])
                
                elif isinstance(obj, Division):
                    self.write_output("\\frac{")
                    self._write(obj.arguments[:1])
                    self.write_output("}{")
                    self._write(obj.arguments[1:2])
                    self.write_output("}")
                
                elif isinstance(obj, InlineText):
                    self.write_output("\\textrm{")
                    self.writer.write_structure(obj.arguments[0])
                    self.write_output("}")
                
                elif isinstance(obj, Subscript):
                    self._write(obj.arguments[:1])
                    self.write_output("_{")
                    self._write(obj.arguments[1:2])
                    self.write_output("}")
                
                elif isinstance(obj, Superscript):
                    self._write(obj.arguments[:1])
                    self.write_output("^{")
                    self._write(obj.arguments[1:2])
                    self.write_output("}")
                
                elif isinstance(obj, SubAndSuperscript):
                    self._write(obj.arguments[:1])
                    self.write_output("^{")
                    self._write(obj.arguments[1:2])
                    self.write_output("}_{")
                    self._write(obj.arguments[2:3])
                    self.write_output("}")
            else:
                self._write(obj)


class LaTeXWriter(LaTeXObject):

    def __init__(self, document):
    
        self.document = document
        self.writers = {}
    
    def write(self, output_path):
    
        self.styles = {}
        
        self.output_file = open(output_path, "w")
        self.write_header()
        self.write_structure(self.document.document_structure)
        self.write_footer()
        self.output_file.close()
    
    def write_header(self):
    
        file_name = os.path.split(self.document.input_path)[1]
        
        self.output_file.write(
            "\\documentclass[a4paper,11pt]{report}\n"
            "\\begin{document}\n"
            "\n"
            )
    
    def write_footer(self):
    
        self.output_file.write(
            "\n"
            "\\end{document}\n"
            )
    
    def quote(self, text):
    
        new_text = ""
        for char in text:
            if char not in string.letters:
                new_text += "_"
            else:
                new_text += char
        return new_text
    
    def write_structure(self, structure, level = 0, inline = False):
    
        if isinstance(structure, Maths):
        
            if structure.parse() != []:
            
                writer = self.writers.setdefault(Maths, LaTeXMathsWriter(self))
                if inline:
                    command = "$"
                else:
                    command = "$$"
                
                self.output_file.write("\n" + command + "\n")
                writer.write(structure)
                self.output_file.write("\n" + command + "\n")
        
        elif isinstance(structure, Text):
        
            writer = self.writers.setdefault(Text, LaTeXTextWriter(self))
            self.output_file.write('%% %s\n' % self.quote(structure.style.name))
            writer.write(structure)
            self.output_file.write("\n")
        
        elif isinstance(structure, TitledStructure):
        
            # Show the first element inside the structure using the structure's
            # own style.
            if isinstance(structure, Chapter):
                self.output_file.write("\\chapter{")
            elif isinstance(structure, Section):
                self.output_file.write("\\" + ("sub"*min(level, 2)) + "section{")
            
            try:
                heading = structure.objects[0]
                if isinstance(heading, Text):
                    writer = self.writers.setdefault(Text, LaTeXTextWriter(self))
                    self.output_file.write(
                        '\n%% %s\n' % self.quote(structure.style.name)
                        )
                    writer.write(heading)
                    self.output_file.write("}\n")
                else:
                    print ("Unexpected structure (%s) in place of text "
                           "heading at %x") % (heading, structure.location)
                
                # Descend into the structure.
                for obj in structure.objects[1:]:
                    self.write_structure(obj, level + 1, inline)
            
            except IndexError:
                print "Incomplete/empty structure at %x" % structure.location
        
        elif isinstance(structure, Structure):
        
            # Descend into the structure, if appropriate.
            for obj in structure.objects:
                self.write_structure(obj, level + 1, inline)
    
    def write_styles(self, styles_file):
    
        for style in self.document.styles:
        
            styles_file.write(
                ".%s {\n" % self.quote(style.name) +
                "}\n\n"
                )
