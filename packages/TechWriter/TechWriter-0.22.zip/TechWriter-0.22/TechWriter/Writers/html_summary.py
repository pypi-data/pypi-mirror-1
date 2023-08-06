#!/usr/bin/env python

"""
html_summary.py - Classes for writing HTML summaries to describe the
                  contents of TechWriter documents.

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


from TechWriter.objects import *

class HTMLWriter:

    with_bytes = False
    
    def __init__(self, hex_digits):
    
        self.hex_digits = hex_digits
    
    def html(self, text):
    
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    def write(self, data, output_file, start, finish, digits):
    
        if isinstance(data, Note):
            self.write_note(data, output_file)
        elif isinstance(data, Comment):
            self.write_comment(data, output_file)
        elif isinstance(data, HTMLReference):
            self.write_reference(data, output_file)
        elif isinstance(data, HTMLReferences):
            self.write_references(data, output_file)
        elif isinstance(data, Target):
            self.write_target(data, output_file)
        elif isinstance(data, Maths):
            self.write_equation(data, output_file)
        elif isinstance(data, Reference):
            obj = data.dereference()
            self.write_reference(HTMLReference(repr(obj), ("%%0%ix" % self.hex_digits) % obj.location), output_file)
        else:
            self.write_data_block(data, output_file, start, finish, self.with_bytes, digits)
    
    def write_line(self, data, offset, output_file, number, format, finish, with_bytes = False):
    
        hex_offset = format % offset
        
        bytes = data[:min(number, finish - offset)]
        if not bytes:
            return finish
    
        codes = []
        code = ""
        chars = []
        words = []
        word = ""
        word_styles = ["word-even", "word-odd"]
        for byte in bytes:
            if with_bytes:
                code = code + "%02x" % ord(byte) + "&nbsp;"
            word = "%02x" % ord(byte) + word
            if len(word) == 8:
                if with_bytes:
                    codes.append('<span class="' + word_styles[0] + '">' + code + '</span>')
                    code = ""
                words.append('<span class="' + word_styles[0] + '">' + word + '</span>')
                word_styles.insert(0, word_styles.pop())
                word = ""
            if 32 <= ord(byte) <= 126:
                chars.append(byte)
            else:
                chars.append('<span class="unprintable">?</span>')
        
        if word:
            word = "&nbsp;"*(8 - len(word)) + word
            words.append('<span class="' + word_styles[0] + '">' + word + '</span>')
            if with_bytes and code:
                codes.append('<span class="' + word_styles[0] + '">' + code + '</span>')
            word_styles.insert(0, word_styles.pop())
        
        if len(bytes) < number:
            remaining = ((number >> 2) - len(words))
            while remaining > 0:
                words += ['<span class="' + word_styles[0] + '">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>']
                word_styles.insert(0, word_styles.pop())
                remaining -= 1
            if with_bytes:
                codes += (number - len(bytes)) * ["&nbsp;&nbsp;"]
            chars += (number - len(bytes)) * ["&nbsp;"]
        
        if with_bytes:
            output_file.write('<span class="offset">' + hex_offset + '</span>' + ":&nbsp;"
                            + "&nbsp;".join(words) + "&nbsp;:&nbsp;"
                            + "".join(chars) + "&nbsp;:&nbsp;" + "".join(codes) + "\n")
        else:
            output_file.write('<span class="offset">' + hex_offset + '</span>' + ":&nbsp;"
                            + "&nbsp;".join(words) + "&nbsp;:&nbsp;"
                            + "".join(chars) + "\n")
        
        return offset + len(bytes)
    
    def write_lines(self, data, output_file, number, start, finish, with_bytes, digits):
    
        format = "%%0%dx" % digits
        offset = start
        
        while True:
            new_offset = self.write_line(data, offset, output_file, number, format,
                                         finish, with_bytes)
            data = data[new_offset-offset:]
            if new_offset >= finish:
                break
            offset = new_offset
    
    def write_header(self, path, output_file):
    
        output_file.write(
            "<html>\n"
            "<head>\n"
            "  <title> Hex dump of " + self.html(path) + "</title>\n"
            '  <link rel="stylesheet" type="text/css" href="styles.css" />\n'
            "</head>\n"
            "<body>\n"
            "<h1>" + self.html(path) + "</h1>\n"
            )
    
    def write_footer(self, output_file):
    
        output_file.write(
            "</body>\n"
            "</html>\n"
            )
    
    def write_data_block(self, data, output_file, start, finish, with_bytes, digits):
    
        output_file.write("<pre>\n")
        self.write_lines(data, output_file, 16, start, finish, with_bytes, digits)
        output_file.write("</pre>\n")
    
    def write_note(self, note, output_file):
    
        output_file.write("<h%i>" % note.level)
        output_file.write(self.html(note.text))
        output_file.write("</h%i>" % note.level)
    
    def write_comment(self, comment, output_file):
    
        output_file.write("<p>")
        output_file.write(self.html(comment.text))
        output_file.write("</p>")
    
    def write_equation(self, equation, output_file):
    
        output_file.write("<p>")
        output_file.write(equation.html())
        output_file.write("</p>")
    
    def write_reference(self, reference, output_file):
    
        output_file.write('<a href="#%s">%s</a><br />' % (
            reference.target, self.html(reference.text)))
    
    def write_references(self, references, output_file):
    
        output = []
        
        for ref in references.targets:
            output.append('<a href="#%s">%s</a>' % (ref, self.html(ref)))
        
        output_file.write(references.text + ", ".join(output))
    
    def write_target(self, target, output_file):
    
        output_file.write('<a name="%s" />' % target.name)


class Note:

    def __init__(self, text, level = 2):
    
        self.text = text
        self.level = level


class HTMLReference:

    def __init__(self, text, target):
    
        self.text = text
        self.target = target


class HTMLReferences:

    def __init__(self, text, targets):
    
        self.text = text
        self.targets = targets


class Target:

    def __init__(self, name):
    
        self.name = name


class Comment:

    def __init__(self, text):
    
        self.text = text

