#!/usr/bin/env python

"""
objects.py - Classes to describe objects in TechWriter documents.

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

import struct

from TechWriter.maths import *
from TechWriter.text import *

# Document objects

class Object:
    
    def read_word(self, text):
    
        return struct.unpack("<I", text[:4])[0]

    def read_half_word(self, text):
    
        return struct.unpack("<H", text[:4])[0]

class StyleType:

    def __init__(self, name, value):
    
        self.name = name
        self.type = value
    
    def __repr__(self):
    
        return "<StyleType: %s (%i)>" % (self.name, self.type)

class StyleInfo:

    Document = StyleType("Document", 0)
    Chapter = StyleType("Chapter", 1)
    Section = StyleType("Section", 2)
    List = StyleType("List", 3)
    Figure = StyleType("Figure", 4)
    Table = StyleType("Table", 5)
    Maths = StyleType("Maths", 6)
    Picture = StyleType("Picture", 7)
    Text = StyleType("Text", 8)
    Note_Area = StyleType("Note_Area", 23)
    Note = StyleType("Note", 24)
    Matrix = StyleType("Matrix", 25)
    Unknown = StyleType("Unknown", -1)
    
    types = {
        0: Document,
        1: Chapter,
        2: Section,
        3: List,
        4: Figure,
        5: Table,
        6: Maths,
        7: Picture,
        8: Text,
        23: Note_Area,
        24: Note,
        25: Matrix
        }

class Style(StyleInfo):

    def __init__(self, name, length, structure_type, location, reference, others = ()):
    
        self.name = name
        self.pair = (length, structure_type)
        self.length = length
        self.type = self.types.get(structure_type, self.Unknown)
        self.location = location
        self.definition = reference
        self.others = others

unknown_style = Style("[unknown]", -1, -1, -1, ())

class Picture(Object):

    def __init__(self, document, style, length, metadata, location):
    
        self.document = document
        self.style = style
        self.length = length
        self.metadata = metadata
        self.location = location
    
    def picture_data(self):
    
        try:
            # The length of the data (not stored since it appears to be
            # padding) is actually the index into the table of the area
            # containing all the picture data.
            offset = self.length
            return self.document.structures["pictures"][offset]
        
        except IndexError:
            return None

class Text(Object):

    def __init__(self, document, style, inline_style_data, text, metadata, location):
    
        self.document = document
        self.style = style
        self.inline_style_data = inline_style_data
        self.text = text
        self.metadata = metadata
        self.location = location
    
    def inline_styles(self):
    
        styles = []
        prefix = []
        current = 0
        text = ""
        for i in range(0, len(self.inline_style_data), 11):
            piece = self.inline_style_data[i:i + 11]
            if len(piece) < 11:
                prefix.append(piece)
                break
            
            offset = self.read_word(piece[0:3]+"\x00")
            length = self.read_word(piece[3:6]+"\x00")
            table = ord(piece[6]), ord(piece[7])
            entry = ord(piece[8]), ord(piece[9]), ord(piece[10])
            if entry[0] != 0 or entry[2] != 0:
                prefix.append(piece)
                continue
            
            styles.append(BaseText(self.text[current:offset]))
            
            # Use either the first or the second table value, but probably
            # not both, to figure out what the style information means. ###
            
            if table[1] == 1:
                ### In the Petschek document, the effect may be defined as the
                # entry[1] element of the table in the area at 0x7da2 (offset
                # 6 in the main table).
                style_data = Reference(self.document, 6, entry[1], 0).dereference()
                if isinstance(style_data, StyleData):
                    styles.append(Effect(self.text[offset:offset + length], style_data))
                else:
                    ### In the Models document, the first letter in the last
                    # paragraph uses an inline style that we can't find.
                    # This fallback prevents an InvalidPair object from being
                    # used with an Effect and causing problems later.
                    styles.append(BaseText(self.text[offset:offset + length]))
                
                # The last byte of the metadata of the referenced style may
                # contain information about which effect is to be used.
                #styles.append(Effect(self.text[offset:offset + length], entry))
            
            else:
                if table[1] == 2:
                    styles.append(Reference(self.document, table[1], entry[1], 0).dereference())
                elif table[0] == 3:
                    # Looks like a page number.
                    print "Unknown style type (%x) at offset %x in structure at %x" % (table[1], i + 7, self.location)
                else:
                    print "Unknown style type (%x) at offset %x in structure at %x" % (table[1], i + 7, self.location)
                
                styles.append(BaseText(self.text[offset:offset + length]))
            
            current = offset + length
        
        styles.append(BaseText(self.text[current:]))
        return prefix + styles
    
    def formatting(self):
    
        number = self.read_half_word(self.metadata[:2])
        if self.inline_style_data:
            number -= 1
        
        pieces = []
        end = len(self.text)
        i = len(self.metadata) - 4
        while i > 2 and number > 1:
            i -= 3
            length = self.read_word(self.metadata[i:i+3] + "\0")
            i -= 3
            offset = self.read_word(self.metadata[i:i+3] + "\0")
            i -= 12
            data = []
            for j in range(i, i+12, 2):
                data.append(self.read_half_word(self.metadata[j:j+2]))
            ### Offset and length the same in Models ("In 1958 ...") so 0x005c
            ### only appears once.
            ### "Diffusion clearly dominates ..." also breaks the pattern
            ### outlined above.
            pieces.append((offset, length, data, self.text[offset:offset+length]))
            number -= 1
            end = offset
        
        pieces.reverse()
        if end > 0:
            i -= 4
            i -= 3
            length = self.read_word(self.metadata[i:i+3] + "\0")
            pieces.insert(0, (0, length, self.text[:length]))
        
        return pieces

class Maths(Object):

    command = {
        0x05: "group",
        0x06: "division", 0x09: "inline text",
        0x26: "equation alignment",
        0x87: "subscript", 0x47: "superscript",
        0xc1: "sqrt",
        0xc7: "super and subscript"
        }
    
    def __init__(self, document, style, text, metadata, location):
    
        self.document = document
        self.style = style
        self.text = text
        self.metadata = metadata
        self.location = location
    
    def parse(self):
    
        self.current_font = ord(self.text[1])
        self.commands = []
        
        i = 3
        #print "->"
        i, text = self._parse(i)
        #print text
        self.data = text
        return text
    
    def _parse(self, i, remaining = -1):
    
        text = []
        while i < len(self.text) and remaining != 0:
        
            char_type = ord(self.text[i])
            char = self.text[i + 1]
            count = ord(self.text[i + 2])
            #print i, remaining, hex(char_type), repr(char)
            
            if char_type & 0xb == 0xb and char != "\x00":
                # Not sure about the font/count relationship.
                if count >= 5:
                    self.current_font = count
                
                if self.current_font == 5:
                    text.append(BaseText(char))
                elif self.current_font == 6:
                    text.append(Italic(char))
                elif self.current_font == 7:
                    text.append(MathPhys(char))
                elif self.current_font == 8:
                    text.append(BaseText(char))
                elif self.current_font == 9: # May be able to do something with bit combinations.
                    text.append(Bold(char))
                else:
                    text.append(BaseText(char))
                i += 4
            
            elif count == 0:
                # A command with following arguments.
                if char_type & 0x20:
                    # Equation alignment flag is set.
                    char_type = char_type & ~0x20
                
                if char_type == 0xc1:
                    # Square root
                    self.commands.append(self.command[char_type])
                    i, (a1,) = self._parse(i + 4, 1)
                    text.append(Sqrt(a1))
                
                elif char_type == 0x05:
                    # Group
                    self.commands.append(self.command[char_type])
                    i, (a1,) = self._parse(i + 4, 1)
                    text.append(Group(a1))
                
                elif char_type == 0x06:
                    # Division
                    self.commands.append(self.command[char_type])
                    i, (a1, a2) = self._parse(i + 4, 2)
                    text.append(Division(a1, a2))
                
                elif char_type == 0x09:
                    # Inline text
                    self.commands.append(self.command[char_type])
                    # The character contains an index into what appears to be
                    # the first block in the reference area or, alternatively,
                    # an index into the first area in the document.
                    # (It may not always be the first of either, of course.)
                    reference = Reference(self.document, ord(self.text[i+3]),
                                          ord(char), 0)
                    #print reference.table, reference.table_position
                    text.append(InlineText(reference.dereference().text))
                    i += 4
                
                # Note: For subscript and superscript, it may be that, if
                # the first argument (corresponding to the symbol to which
                # the script is attached) has a count of 2 or greater, the
                # second character in the argument is actually placed above
                # or below the symbol.
                
                elif char_type == 0x87:
                    # Subscript
                    self.commands.append(self.command[char_type])
                    i, (a1, a2) = self._parse(i + 4, 2)
                    text.append(Subscript(a1, a2))
                
                elif char_type == 0x47:
                    # Superscript
                    self.commands.append(self.command[char_type])
                    i, (a1, a2) = self._parse(i + 4, 2)
                    text.append(Superscript(a1, a2))
                
                elif char_type == 0xc7:
                    # Superscript and subscript (perhaps could be handled by
                    # checking for the flags used in the previous two cases)
                    self.commands.append(self.command[char_type])
                    i, (a1, a2, a3) = self._parse(i + 4, 3)
                    text.append(SubAndSuperscript(a1, a2, a3))
                
                else:
                    # Unsupported command
                    print "Command %x unknown at %x (offset %x)" % (char_type, self.location, i)
                    self.commands.append(None)
                    i, args = self._parse(i + 4, 2)
                    text += args
                    i += 4
                
                command = self.commands.pop()
            
            else:
                # An argument or argumentless command
                i, new_text = self._parse(i + 4, count)
                #if char_type == 0x0e:
                #    text.append("".join(map(lambda t: t.text, new_text)))
                #else:
                if True:
                    text.append(new_text)
                # The index will have been updated by this call.
            
            if remaining > 0:
                remaining -= 1
        
        return i, text
    

class StyleData(Object, StyleInfo):

    def __init__(self, name, identifier, text, metadata, location):
    
        self.name = name
        self.type = StyleInfo.types.get(identifier, StyleType(name, identifier))
        self.text = text
        self.metadata = metadata
        self.location = location
    
    def id(self):
        return self.name or oct(self.location)
    
    def info(self):
    
        if not self.metadata:
            return {}
        """
        if self.type == 0:
            return self._info_document()
        elif self.type == 1:
            return self._info_chapter()
        elif self.type == 2:
            return self._info_section()
        elif self.type == 3:
            return self._info_list()
        elif self.type == 4:
            return self._info_figure()
        elif self.type == 5:
            return self._info_table()
        elif self.type == 6:
            return self._info_maths()
        elif self.type == 7:
            return self._info_picture()
        elif self.type == 8:
            return self._info_paragraph()
        elif self.type == 23:
            return self._info_note_area()
        elif self.type == 24:
            return self._info_note()
        elif self.type == 25:
            return self._info_matrix()
        """
        if self.type == 1:
            return self._read_font_info()
        elif self.type == 8:
            return self._read_font_info()
        else:
            return {}
    
    def _info_document(self):
    
        alignment = ord(self.metadata[0x33])
        if alignment == 0:
            alignment = "left"
        elif alignment == 1:
            alignment = "centre"
        elif alignment == 2:
            alignment = "right"
        elif alignment == 3:
            alignment = "full justify"
        elif alignment == 5:
            alignment = "force full"
        
        auto_hyphenation = ord(self.metadata[0x3a]) == 1
        auto_indentation = ord(self.metadata[0x3c]) == 1
        
        space_before = ord(self.metadata[0x3d])/10.0 # pt
        space_after = ord(self.metadata[0x3f])/10.0 # pt
        
        fixed_line_height = ord(self.metadata[0x39]) == 1
        line_height = ord(self.metadata[0x31])/10.0 # pt
        custom_line_height = line_height != 0
        
        if ord(self.metadata[7]) & 0x40:
        
            border_info = ord(self.metadata[0x41])
            # 1 top, 2 left, 8 right, 4 bottom, 0x80 shadow
            if border_info & 0x80:
                border_style = "shadow"
            else:
                border_style = "box"
            
            border_sides = {"top": (border_info & 1) != 0,
                            "left": (border_info & 2) != 0,
                            "right": (border_info & 4) != 0,
                            "bottom": (border_info & 8) != 0}
            
            border_merge = (border_info & 0x10) != 0
            
            border_width = self.read_half_word(self.metadata[0x42:0x44])/10000.0 # pt
            
            nested_border = ord(self.metadata[0x45])
            if nested_border == 1:
                # No inner border
                outer_border_width = border_width
            elif nested_border == 2:
                inner_border_width = outer_border_width = border_width
            elif nested_border == 3:
                inner_border_width = border_width * 2
                outer_border_width = border_width
            elif nested_border == 4:
                inner_border_width = border_width
                outer_border_width = border_width * 2
            # Read border definitions.
            # 0x42 - 0x48
            next += 5
        
        # After the font definition.
        next = 0 ###
        heading_position = self.metadata[next + 6]
        if heading_position == 0:
            heading_position = "over text"
        elif heading_position == 1:
            heading_position = "left of text"
        elif heading_position == 2:
            heading_position = "over both columns"
        elif heading_position == 3:
            heading_position = "over left column"
        
        roman_numbers = ord(self.metadata[next + 0x22]) == 1
        
        columns = ord(self.metadata[0x21])
        if columns > 1 or heading_position == "over left column":
        
            column_separation = self.read_half_word(self.metadata[0x1d:0x1f])/625.0 # pt
            column_justify = ord(self.metadata[next + 2]) == 1
            column_border_width = self.read_half_word(self.metadata[next+10:next+12])/10000.0 # pt
            column_balanced = ord(self.metadata(next + 14)) == 1
            column_nested_border = ord(self.metadata(next + 13))
            if column_nested_border == 1:
                # No inner border
                column_outer_border_width = column_border_width
            elif column_nested_border == 2:
                column_inner_border_width = column_outer_border_width = column_border_width
            elif column_nested_border == 3:
                column_inner_border_width = column_border_width * 2
                column_outer_border_width = column_border_width
            elif column_nested_border == 4:
                column_inner_border_width = column_border_width
                column_outer_border_width = column_border_width * 2
        
        # The document style where headings are to the left of the content
        # contains more information after the usual end of the style.
        
        return locals()
    
    def _info_chapter(self):
    
        roman_numbers = ord(self.metadata[0x43]) == 1
        
        next = 0x1a
        if ord(self.metadata[5]) & 0x40:
        
            line_height = ord(self.metadata[next])/10.0 # pt
            fixed_line_height = ord(self.metadata[next + 2]) == 1
            next += 3
        
        auto_hyphenation = ord(self.metadata[next]) == 1
        auto_indentation = ord(self.metadata[next + 1]) == 1
        space_before = ord(self.metadata[next + 2])/10.0 # pt
        space_after = ord(self.metadata[next + 4])/10.0 # pt
        
        if ord(self.metadata[7]) & 0x40:
        
            border_info = ord(self.metadata[next + 2])
            # 1 top, 2 left, 8 right, 4 bottom, 0x80 shadow
            if border_info & 0x80:
                border_style = "shadow"
            else:
                border_style = "box"
            
            border_sides = {"top": (border_info & 1) != 0,
                            "left": (border_info & 2) != 0,
                            "right": (border_info & 4) != 0,
                            "bottom": (border_info & 8) != 0}
            
            border_merge = (border_info & 0x10) != 0
            
            border_width = self.read_half_word(self.metadata[next+3:next+5])/10000.0 # pt
            
            nested_border = ord(self.metadata[next + 6])
            if nested_border == 1:
                # No inner border
                outer_border_width = border_width
            elif nested_border == 2:
                inner_border_width = outer_border_width = border_width
            elif nested_border == 3:
                inner_border_width = border_width * 2
                outer_border_width = border_width
            elif nested_border == 4:
                inner_border_width = border_width
                outer_border_width = border_width * 2
            next += 5
        
        page_alignment = ord(self.metadata[next + 0x19])
        if page_alignment == 0:
            page_alignment = "immediately"
            # 0x37-0x3b == 0xfffffffe
        elif page_alignment == 1:
            if ord(self.metadata[next + 0x1d]) == 0:
                page_alignment = "on next page"
            elif ord(self.metadata[next + 0x1d]) == 1:
                page_alignment = "on right hand page"
            elif self.read_word(self.metadata[next + 0x1d:next + 0x21]) == 0xffffffff:
                page_alignment = "on left hand page"
        
        if ord(self.metadata[6]) & 0x80:
        
            # Multiple columns
            columns = ord(self.metadata[0x15])
            column_separation = self.read_half_word(self.metadata[0x11:0x13])/625.0 # pt
            column_balanced = ord(self.metadata[next + 0x15]) == 1
            column_justify = ord(self.metadata[next + 9]) == 1
            column_border_width = self.read_half_word(self.metadata[next+0x11:next+0x13])/10000.0 # pt
            column_nested_border = ord(self.metadata[next + 0x14])
            if column_nested_border == 1:
                # No inner border
                column_outer_border_width = column_border_width
            elif column_nested_border == 2:
                column_inner_border_width = column_outer_border_width = column_border_width
            elif column_nested_border == 3:
                column_inner_border_width = column_border_width * 2
                column_outer_border_width = column_border_width
            elif column_nested_border == 4:
                column_inner_border_width = column_border_width
                column_outer_border_width = column_border_width * 2
        
        auto_numbering = (ord(self.metadata[next + 7]) & 1) == 1
        
        if auto_numbering:
        
            # The prefix is appended to the style definition.
            pass
        
        return locals()
    
    def _info_section(self):
    
        return locals()
    
    def _info_list(self):
    
        if ord(self.metadata[0x27]) == 0x01:
            item_type = "numbered"
        elif ord(self.metadata[0x27]) == 0x02:
            item_type = "custom"
        else: # 0x8f
            item_type = "bullet"
        
        font_name_length = ord(self.metadata[4])
        
        return locals()
    
    def _info_figure(self):
        return locals()
    
    def _info_table(self):
        return locals()
    
    def _info_maths(self):
        return locals()
    
    def _info_picture(self):
        return locals()
    
    def _info_paragraph(self):
    
        return self._read_font_info()
    
    def _read_font_info(self, start = 12):
    
        if self.type == 1:
            # Chapter
            left_margin = self.read_word(self.metadata[9:12] + "\x00")
            right_margin = self.read_word(self.metadata[13:16] + "\x00")
            next = 0x11
        elif self.type == 8:
            # Paragraph
            next = start
        
        if ord(self.metadata[6]) & 0x80:
        
            # Multiple columns
            columns = ord(self.metadata[next + 4])
            column_separation = self.read_word(self.metadata[next:next+4])/10000.0 # pt
            
            next += 8
        
        style_type = ord(self.metadata[5])
        
        if style_type & 1:
            # Font change
            next += 2 # 14
            font = True
            length = ord(self.metadata[3])
        else:
            font = False
        
        if style_type & 2:
        
            font_height = self.read_half_word(self.metadata[next:next+2])
            font_height /= 16.0
            font_width = self.read_half_word(self.metadata[next+2:next+4])
            font_width /= 16.0
            next += 4 # including a following zero byte
        
        if style_type & 4:
        
            effect = ord(self.metadata[next])
            bold = (effect & 0x04) != 0
            italic = (effect & 0x08) != 0
            auto_kern = (effect & 0x40) != 0
            next += 1
        
        if style_type & 0x10: # Maybe 0x18
        
            upper_case = (ord(self.metadata[next]) & 0x0f) == 1
            lower_case = (ord(self.metadata[next]) & 0x0f) == 2
            initial_caps = (ord(self.metadata[next]) & 0x0f) == 3
            next += 1
        
        if ord(self.metadata[5]) & 0x40:
        
            # Line height information from Chapter styles
            line_height = ord(self.metadata[next])/10.0 # pt
            next += 2
        
        if ord(self.metadata[5]) & 0x20:
        
            # Alignment
            alignment = ord(self.metadata[next])
            if alignment == 0:
                alignment = "left"
            elif alignment == 1:
                alignment = "centre"
            elif alignment == 2:
                alignment = "right"
            elif alignment == 3:
                alignment = "full justify"
            elif alignment == 5:
                alignment = "force full"
            next += 1
        
        if ord(self.metadata[5]) & 0x40:
        
            fixed_line_height = ord(self.metadata[next]) == 1
            next += 1
        
        if (ord(self.metadata[7]) & 0x02) != 0:
        
            auto_hyphenation = ord(self.metadata[next]) == 1
            next += 1
        
        if (ord(self.metadata[7]) & 0x04) != 0:
        
            country = ord(self.metadata[next])
            next += 1
        
        if self.type == 1:
        
            next += 1
            # Chapter styles
            space_before = ord(self.metadata[next])/10.0 # pt
            next += 2
            space_after = ord(self.metadata[next])/10.0 # pt
            next += 2
        
        if ord(self.metadata[7]) & 0x40:
        
            border_info = ord(self.metadata[next])
            # 1 top, 2 left, 8 right, 4 bottom, 0x80 shadow
            if border_info & 0x80:
                border_style = "shadow"
            else:
                border_style = "box"
            
            border_sides = {"top": (border_info & 1) != 0,
                            "left": (border_info & 2) != 0,
                            "right": (border_info & 4) != 0,
                            "bottom": (border_info & 8) != 0}
            
            border_merge = (border_info & 0x10) != 0
            
            border_width = self.read_half_word(self.metadata[next+1:next+3])/10000.0 # pt
            
            nested_border = ord(self.metadata[next + 4])
            if nested_border == 1:
                # No inner border
                outer_border_width = border_width
            elif nested_border == 2:
                inner_border_width = outer_border_width = border_width
            elif nested_border == 3:
                inner_border_width = border_width * 2
                outer_border_width = border_width
            elif nested_border == 4:
                inner_border_width = border_width
                outer_border_width = border_width * 2
            
            next += 5
        
        if (ord(self.metadata[7]) & 0x08) != 0:
        
            red = ord(self.metadata[next + 1])
            green = ord(self.metadata[next + 2])
            blue = ord(self.metadata[next + 3])
            next += 4
        
        if font:
        
            font_name = self.metadata[next:next + length]
            next += length
        
        next += 4
        
        if ord(self.metadata[6]) & 0x80:
        
            column_justified = ord(self.metadata[next]) == 1
            next += 4
            
            heading_position = self.metadata[next]
            if heading_position == 0:
                heading_position = "over text"
            elif heading_position == 1:
                heading_position = "left of text"
            elif heading_position == 2:
                heading_position = "over both columns"
            elif heading_position == 3:
                heading_position = "over left column"
            next += 4
            
            column_border_width = self.read_half_word(self.metadata[next:next+2])/10000.0 # pt
            column_nested_border = ord(self.metadata[next + 3])
            if column_nested_border == 1:
                # No inner border
                column_outer_border_width = column_border_width
            elif column_nested_border == 2:
                column_inner_border_width = column_outer_border_width = column_border_width
            elif column_nested_border == 3:
                column_inner_border_width = column_border_width * 2
                column_outer_border_width = column_border_width
            elif column_nested_border == 4:
                column_inner_border_width = column_border_width
                column_outer_border_width = column_border_width * 2
            next += 4
            
            column_balanced = ord(self.metadata[next]) == 1
            next += 4
        
        if self.type == 1:
        
            # Chapter page alignment
            page_alignment = ord(self.metadata[next])
            if page_alignment == 0:
                page_alignment = "immediately"
                # 0x37-0x3b == 0xfffffffe
            elif page_alignment == 1:
                if ord(self.metadata[next + 4]) == 0:
                    page_alignment = "on next page"
                elif ord(self.metadata[next + 4]) == 1:
                    page_alignment = "on right hand page"
                elif self.read_word(self.metadata[next + 4:next + 8]) == 0xffffffff:
                    page_alignment = "on left hand page"
            
            next += 8
        
        if ord(self.metadata[0]) & 0x02:
        
            # Tab information at the end.
            next += 16
            
            # Looks like a word containing a 3-byte length, two other words
            # containing identifiers or flags, a zero word, then another
            # definition.
        
        return locals()
    
    def _info_note_area(self):
        return locals()
    
    def _info_note(self):
        return locals()
    
    def _info_matrix(self):
        return locals()


# Picture data objects

class PictureData(Object):

    def __init__(self, data, location):
    
        self.data = data
        self.location = location

class DrawFile(PictureData):

    pass


# Structures that are used to hold other objects - chapters, sections,
# tables, etc.

class Structure(Object):

    def __init__(self, style, metadata, location):
    
        self.style = style
        self.metadata = metadata
        self.location = location
        self.objects = []
    
    def add_object(self, obj):
    
        self.objects.append(obj)
    
    def __iter__(self):
    
        return StructureIterator(self, 0)
    
    def __next__(self, position):
    
        """__next__(self, position)
        
        Special method specific to Structure subclasses so that the same
        iterator can be used with all of them, but extended by individual
        classes as required.
        """
        try:
            return self.objects[position], position + 1
        except IndexError:
            raise StopIteration
    
    def __replace__(self, position, item):
    
        """__replace__(self, position, item)
        
        Special method specific to Structure subclasses to allow the same
        iterator to be used to replace items in a structure.
        """
        self.objects[position] = item

class StructureIterator:

    def __init__(self, structure, position):
    
        self.structure = structure
        self.position = position
        self.previous = None
    
    def next(self):
    
        self.previous = self.position
        item, self.position = self.structure.__next__(self.position)
        return item
    
    def replace(self, item):
    
        self.structure.__replace__(self.previous, item)

class Document(Structure):

    pass

class TitledStructure(Structure):

    pass

class Chapter(TitledStructure):

    pass

class Section(TitledStructure):

    pass

class List(Structure):

    pass

class Figure(Structure):

    pass

class Note_Area(Structure):

    pass

class Note(Structure):

    pass

class Matrix(Structure):
    
    def __init__(self, document, style, inline_style_data, text, metadata, location):
    
        self.document = document
        self.style = style
        self.inline_style_data = inline_style_data
        self.text = text
        self.metadata = metadata
        self.location = location
        self.read_data()
    
    def read_data(self):
    
        # The number of rows is found at offset 0x17 and the total number of
        # items is at offset 0x1b. We can also obtain the number of rows from
        # the metadata.
        self.rows = self.read_half_word(self.metadata[:2])
        total = ord(self.inline_style_data[0x1b])
        self.columns = divmod(total, self.rows)[0]
        
        self.objects = []
        row = []
        # Start at offset 0x1f and decode the references that occur every 32
        # bytes.
        for i in range(31, len(self.inline_style_data), 32):
            table = self.read_half_word(self.inline_style_data[i:i+2])
            table_position = self.read_half_word(self.inline_style_data[i+2:i+4])
            unknown = self.read_half_word(self.inline_style_data[i+4:i+6])
            reference = Reference(self.document, table, table_position, unknown)
            row.append(reference)
            if len(row) == self.columns:
                self.objects.append(row)
                row = []
    
    def __iter__(self):
    
        return StructureIterator(self, (0, 0))
    
    def __next__(self, position):
    
        try:
            row, column = position
            items = self.objects[row]
            item = items[column]
            column += 1
            if column == self.columns:
                column = 0
                row += 1
            return item, (row, column)
        except IndexError:
            raise StopIteration
    
    def __replace__(self, position, item):
    
        row, column = position
        self.objects[row][column] = item

class Table(Matrix):

    pass


# Other objects

class Reference:

    def __init__(self, document, table, table_position, unknown):
    
        self.document = document
        self.table = table
        self.table_position = table_position
        self.unknown = unknown
    
    def dereference(self):
    
        return self.document.dereference(self.table, self.table_position, self.unknown)
    
    def __repr__(self):
    
        try:
            text = repr(self.dereference())
            return text[:1] + "Reference to " + text[1:]
        except (KeyError, IndexError):
            return "<Reference %i:%i:%i>" % (self.table, self.table_position, self.unknown)


# Factory objects

def ObjectFactory(object_type):

    types = {
        0: Document,
        1: Chapter,
        2: Section,
        3: List,
        4: Figure,
        5: Table,
        6: Maths,
        7: Picture,
        8: Text,
        23: Note_Area,
        24: Note,
        25: Matrix
        }
    
    return types.get(object_type, Structure)
