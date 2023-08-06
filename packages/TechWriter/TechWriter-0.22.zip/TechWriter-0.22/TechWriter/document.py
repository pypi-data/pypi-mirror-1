#!/usr/bin/env python

"""
document.py - Classes to read and decode TechWriter documents.

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

import objects
from objects import *


# Internal document objects

class Area:

    """Area
    
    An area containing a lookup table and some definitions or structures.
    """
    def __init__(self, document, start, finish, contains_structures):
    
        self.document = document
        self.start = start
        self.finish = finish
        self.contains_structures = contains_structures
        self.table = []
    
    def read_contents(self):
    
        for entry in range(len(self.table)):
            self.read_entry(entry)
    
    def read_entry(self, entry):
    
        obj = self.table[entry]
        
        if isinstance(obj, InvalidPair):
            return obj
        elif isinstance(obj, ValidPair):
            pair = obj
        else:
            return obj
        
        document = self.document
        document.input_file.seek(pair.start, 0)
        
        obj = document.read_object(
            pair.start, pair.offset, pair.finish, self.contains_structures
            )
        
        if isinstance(obj, Structure):
            document.elements.append(obj)
        elif isinstance(obj, PictureData):
            document.structures["pictures"][entry] = obj
        else:
            document.definitions.append(obj)
        
        self.table[entry] = obj
        document.structures["structures"][pair.start + pair.offset] = obj
        
        return self.table[entry]


class Pair:

    """Pair
    
    An address-offset pair used in lookup tables for areas.
    """
    def __init__(self, address, offset):
    
        self.start = address
        self.offset = offset
        # The finish address should be modified afterwards to refer to
        # either the next valid pair or the end of the area containing the
        # pair.
        self.finish = address

class ValidPair(Pair):

    pass

class InvalidPair(Pair):

    pass


class Document:

    """Document
    
    Represents a TechWriter document and is used to parse existing TechWriter
    files.
    """
    
    def __init__(self, input_path):
    
        self.input_path = input_path
        self.input_file = open(input_path, "rb")
        self.input_file.seek(0, 2)
        self.length = self.input_file.tell()
        self.input_file.seek(0, 0)
        self.structures = {}
        self.data = {}
        self.objects = {}
        
        # Read and parse the file.
        self.read()
    
    def dereference(self, table, table_position, unknown = 0):
    
        start, discard = self.structures["main table"][table]
        area = self.structures["areas"][start]
        obj = area.read_entry(table_position)
        
        return obj
    
    def read_word(self, text = None):
    
        if not text:
            text = self.input_file.read(4)
            return struct.unpack("<I", text)[0], text
        else:
            return struct.unpack("<I", text[:4])[0]
    
    def read(self):
    
        self.read_main_table()
        addresses = self.structures["main table"]
        addresses.sort()
        
        # Read the part before the first area.
        start, discard = addresses[0]
        self.structures["styles"] = self.read_styles_list(start)
        self.styles = self.structures["styles"].values()
        
        # Append the length of the file to the list of area addresses to allow
        # us to read to the end of the file.
        #addresses.append(self.length)
        self.structures["areas"] = {}
        self.structures["structures"] = {}
        self.structures["pictures"] = {}
        self.elements = []
        self.definitions = []
        
        for i in range(len(addresses)-1):
            start, structure = addresses[i]
            finish, discard = addresses[i+1]
            area = self.read_area(start, finish, structure)
            self.structures["areas"][start] = area
        
        # Ensure that all the styles are dereferenced.
        for style in self.styles:
            style.definition = style.definition.dereference()
        
        # Read the contents of all the areas.
        for area in self.structures["areas"].values():
            area.read_contents()
        
        # Examine the last area in the file separately.
        start, discard = addresses[-1]
        area = self.read_reference_area(start, self.length)
        self.structures["areas"][start] = area
    
    def read_main_table(self):
    
        addresses = []
        valid1 = (0x20, 0x24, 0x28, 0x2c)
        valid2 = (0x30, 0x34, 0x38, 0x3c,
                  0x40, 0x44, 0x48, 0x58, 0xc0)
        
        for address in valid1 + valid2:
        
            self.input_file.seek(address, 0)
            pos = self.input_file.tell()
            
            word, text = self.read_word()
            if word != 0 and word <= self.length:
                addresses.append((word, address in valid2))
        
        self.structures["main table"] = addresses
    
    def read_area(self, start, finish, contains_structures = False):
    
        area = Area(self, start, finish, contains_structures)
        
        #print "In area", hex(start), hex(finish)
        
        # Store the table entries so that the contents of the area can be
        # examined when all areas have been scanned.
        area.table = self.read_table(start, finish)
        return area
    
    def read_table(self, start, finish):
    
        # Begin at the start of the area.
        self.input_file.seek(start, 0)
        
        data = ""
        
        # Read the initial length word.
        length, bytes = self.read_word()
        data += bytes
        
        if length % 4 != 0:
        
            data += self.input_file.read(finish - start - 4)
            return []
        
        pairs = []
        previous_valid = None
        for i in range(0, length, 8):
        
            address, bytes = self.read_word()
            data += bytes
            offset, bytes = self.read_word()
            data += bytes
            if address <= finish:
            
                # Store the valid pair in the list.
                pair = ValidPair(address, offset)
                pairs.append(pair)
                
                # If there was a previous pair in the list, add the address of
                # this pair to it so that we know the extent of the structure
                # it represents.
                if previous_valid:
                    previous_valid.finish = address
                
                # This pair is now the previous valid pair.
                previous_valid = pair
            else:
                # Store the invalid pair in the list.
                pairs.append(InvalidPair(address, offset))
        
        # The final valid pair must be given the finishing address of the
        # area, so that the extent of the final structure in the area is
        # fully defined.
        if previous_valid:
            previous_valid.finish = finish
        
        #print "table", hex(start), hex(start + length)
        return pairs
    
    def read_object(self, start, offset, finish, structure):
    
        if structure:
            obj = self.read_structure(start, offset, finish)
        else:
            obj = self.read_definition(start, offset, finish)
        
        return obj
        
    def read_definition(self, start, offset, finish):
    
        # Create targets for this definition in the HTML output.
        
        self.input_file.seek(start, 0)
        data = self.input_file.read(11)
        
        # The first word is different for different kinds of definitions,
        # though this may just be a coincidence.
        
        word = self.read_word(data[:4])
        identifier = word >> 16
        
        if identifier in self.structures["styles"]:
        
            # Text
            style = self.structures["styles"][identifier]
        
        else:
        
            style = self.dereference(identifier & 0xff, identifier >> 8, 0)
        
        if True:
        
            if isinstance(style, Style):
                name, others = style.name, style.others
            
            length = self.input_file.read(3)
            content_id = self.input_file.read(2)
            
            length = self.read_word(length + "\x00")
            content_id = self.read_word(content_id + "\x00\x00")
            
            data_start = 16
            
            # Read the data between the start of the data and the offset.
            # If the length is less than the total data available, it means
            # that the text is preceded by some information about style
            # changes within the body of the text.
            
            inline_length = max(0, offset - data_start - length)
            if inline_length > 0:
            
                inline_style_data = self.input_file.read(inline_length)
                
                # For some inline style information, the data contains fields of bytes
                # of the form 3-3-5, where the first three bytes correspond to an
                # offset* in the text (also appearing in the metadata that follows the
                # text), the length of the text effect, and a reference to the effect
                # information.
                # The effect may be an inline expression, in which case
                # the 5 bytes are broken up into a 1-2-2 sequence where the first
                # pair of bytes refer to the area in the main table (or a block in the
                # reference area) and the second pair refers to an entry in the area
                # (or block's) table. The address found this way is that of an equation
                # structure.
                # Pure text effects appear to involve 1-1-3 sequences where the first
                # two bytes are both 01, and the 3 byte sequence contains a value
                # surrounded by two zero bytes. In some documents, italic is 12 and
                # bold is 13. Although one draft chapter (Petschek) uses 14, the full
                # thesis document (Final2) uses 17 at the same place, and the
                # PostScript file shows plain text in one place, and italic in the
                # caption for a table.
                #
                # * Such offsets refer to offsets in the text where a style change or
                # line break occurs.
                
            
            else:
                inline_style_data = ""
            
            text = self.input_file.read(offset - data_start - inline_length)
            #print repr(data)
            
            # Read the metadata after the offset.
            metadata = self.input_file.read(finish - start - offset)
            
            if metadata:
                # The first half word appears to be the number of pieces (not
                # necessarily just lines) used to display the text.
                lines = self.read_word(metadata[:2] + "\x00\x00")
            
            # From examining an internal data dump for an unrelated document,
            # it seems that the type of structure is defined in the associated
            # style. This means we can avoid having to guess about the
            # type using the content ID which, according to a brief comparison
            # between the data dump and my own documents, is apparently the
            # language in use.
            
            if style.type == style.Maths:
                definition = Maths(self, style, text, metadata, start)
            elif style.type == style.Picture:
                definition = Picture(self, style, length, metadata, start)
            elif style.type == style.Matrix:
                definition = Matrix(self, style, inline_style_data, text, metadata, start)
            elif style.type == style.Table:
                definition = Table(self, style, inline_style_data, text, metadata, start)
            else:
                definition = Text(self, style, inline_style_data, text, metadata, start)
        
        else: # We should never encounter style definitions where content
              # definitions are expected.
        
            # Style definition
            
            length = self.input_file.read(1)
            
            length = ord(length)
            
            definition = self.read_style_definition(start, length, offset, finish)
        
        # Store the location of the object in the objects dictionary.
        self.objects[start + offset] = definition
        definition.extent = finish - start - offset
        
        #else:
        #    self.data[(start, start)] = Note("Definition (%x)" % start, 3)
        #    data += self.input_file.read(offset - 11)
        #    self.data[(start, start + offset)] = data
        #    self.data[(start + offset, finish)] = self.input_file.read(finish - start - offset)
        #    return
        
        #if offset - data_start != length:
        #    print "Offset (%x) does not refer to point after data beginning at %x" % (start + offset, start)
        #print hex(start), hex(start + offset)
        
        #xpos = self.read_word(data[4:6])
        #ypos = self.read_word(data[6:8])
        #print hex(start + offset), hex(address2)
        
        return definition
    
    def read_style_definition(self, start, length, offset, finish):
    
        identifier = self.input_file.read(1)
        identifier = ord(identifier)
        data_start = 13
        
        # Read the data between the start of the data and the offset.
        text = self.input_file.read(offset - data_start)
        
        name = text[:length]
        
        # The data after the name appears to refer to an identifier that
        # may be used elsewhere in the document. Not all style definitions
        # have this identifier, however.
        
        ###
        
        for style in self.structures["styles"].values():
            if style.pair == (length, identifier) and name == style.name:
                # The definition contains information about this style.
                #print name, style.name
                break
        
        # Read the metadata after the offset.
        metadata = self.input_file.read(finish - start - offset)
        
        # Looking at the definitions with the same identifiers and examining
        # an internal data dump for an unrelated document, it appears that
        # the identifier is actually the type of the structure defined by
        # each definition.
        
        definition = StyleData(name, identifier, text, metadata, start)
        # The third byte looks like a marker that also appears after the
        # font string.
        #marker = data[2]
        
        # Start at the next word boundary.
        #i = 4 - ((start + offset) % 4)
        
        # The first two bytes are the length of a font string, if present.
        #length = self.read_word(data[i:i+2] + "\x00\x00")
        
        ###
        return definition
    
    def read_structure(self, start, offset, finish):
    
        self.input_file.seek(start, 0)
        data = self.input_file.read(12)
        
        # The first word may refer to an existing structure style, indicating
        # that the data is a document structure (chapter, section, figure, etc.)
        # that is formatted using that style.
        
        word = self.read_word(data[:4])
        
        # The first two bytes correspond to the number of elements held by a
        # structure; the second two are used to identify the structure style
        # in use.
        identifier = word >> 16
        
        if identifier in self.structures["styles"]:
        
            # Structure
            structure_type = ord(data[11])
            
            # Read the rest of the first sixteen bytes.
            data += self.input_file.read(4)
            
            style = self.structures["styles"][identifier]
            name, others = style.name, style.others
            
            data_start = 16
            
            # Read the data between the start of the data and the offset.
            # The first part of the data is a series of references to
            # information via areas stored in the main table.
            
            inline_length = max(0, offset - data_start)
            if inline_length > 0:
            
                inline_data = self.input_file.read(inline_length)
            
            # Read the metadata after the offset.
            metadata = self.input_file.read(finish - start - offset)
            
            StructureClass = ObjectFactory(structure_type)
            definition = StructureClass(style, metadata, start)
            
            if metadata:
            
                # The first half word appears to be the number of structures.
                pieces = self.read_word(metadata[:2] + "\x00\x00")
                
                # Work backwards from the end of the inline data to retrieve references to
                # structures. Each three bytes (possibly three pairs of bytes) refers to a
                # structure: the first is the number of an entry in the main table which is
                # used to obtain the address of an area, the second is the number of an
                # entry in the area's table, and the third has an unknown purpose.
                
                objects = []
                i = len(inline_data)
                while pieces > 0:
                    i -= 2
                    unknown = self.read_word(inline_data[i:i+2] + "\x00\x00")
                    i -= 2
                    table_position = self.read_word(inline_data[i:i+2] + "\x00\x00")
                    i -= 2
                    table = self.read_word(inline_data[i:i+2] + "\x00\x00")
                    objects.append(self.dereference(table, table_position, unknown))
                    pieces -= 1
                
                objects.reverse()
                for obj in objects:
                    definition.add_object(obj)
            
            else:
            
                # Some documents (such as the Alfven document) contain structures
                # without metadata.
                pass
        
        elif data[8:12] == "Draw":
        
            # Draw file
            definition = DrawFile(data[8:12] + self.input_file.read(finish - start - 12), start)
        
        else:
        
            # Style definition
            
            length = ord(data[11])
            
            definition = self.read_style_definition(start, length, offset, finish)
        
        if definition:
        
            # Store the location of the object in the objects dictionary.
            self.objects[start + offset] = definition
            definition.extent = finish - start - offset
        
        return definition

    def read_reference_area(self, start, finish):
    
        self.input_file.seek(start, 0)
        initial_data = self.input_file.read(0x88)
        
        # In the initial data, there are a number of measurements that appear
        # to correspond to page size and margins.
        top_left_offset = (self.read_word(initial_data[0x44:0x48]),
                           self.read_word(initial_data[0x48:0x4c]))
        bottom_right_offset = (self.read_word(initial_data[0x4c:0x50]),
                               self.read_word(initial_data[0x50:0x54]))
        printable_dimensions = (self.read_word(initial_data[0x6c:0x70]),
                                self.read_word(initial_data[0x70:0x74]))
        crop_offsets = (self.read_word(initial_data[0x74:0x78]),
                        self.read_word(initial_data[0x78:0x7c]))
        paper_dimensions = (self.read_word(initial_data[0x7c:0x80]),
                                self.read_word(initial_data[0x80:0x84]))
        
        # Assume that there is a table 0x88 bytes into this area.
        data = ""
        first, bytes = self.read_word()
        data += bytes
        addresses = [first]
        previous_valid = False
        document_block = None
        
        while self.input_file.tell() < first:
        
            word, bytes = self.read_word()
            data += bytes
            if start <= word <= finish:
                addresses.append(word)
                previous_valid = True
            else:
                # The fifth address appears to refer to the block whose first
                # entry itself refers to the document structure definition.
                # It appears to be followed by a zero word, so we'll use that
                # to mark any preceding valid address as the block containing
                # this reference.
                if word == 0 and previous_valid:
                    document_block = addresses[-1]
                previous_valid = False
        
        area = Area(self, start, finish, True)
        area.table = addresses
        area.references = []
        
        # The data at each address referred to in the table itself begins with
        # a length word and is followed by address-length pairs, where the
        # length for each address is the length of the data it refers to.
        
        # We could use the length word to check that the addresses in this
        # table are consistent with the data they refer to but, for now, we'll
        # just assume that they're all valid.
        
        # The last address in the list should be the extent of the file.
        
        for address in addresses[:-1]:
        
            self.input_file.seek(address, 0)
            data = ""
            length, bytes = self.read_word()
            data += bytes
            
            found = []
            missing = []
            
            for i in range(0, length, 8):
            
                location, bytes = self.read_word()
                data += bytes
                data_length, bytes = self.read_word()
                data += bytes
                if data_length == 0:
                    continue
                
                if location in self.objects and data_length == self.objects[location].extent:
                    found.append(location)
                else:
                    missing.append(location)
            
            position = self.input_file.tell()
            if found:
                area.references.append(found)
            
            if address == document_block:
            
                structures = map(lambda found_addr:
                    self.structures["structures"][found_addr], found)
                documents = filter(lambda structure:
                    isinstance(structure, objects.Document), structures)
                
                if len(documents) != 0:
                    self.document_structure = documents[-1]
        
        area.read_contents()
        return area
    
    def read_styles_list(self, top):
    
        self.input_file.seek(0, 0)
        data = self.input_file.read(top)
        
        position = top - 1
        styles = {}
        number = 0
        name = ""
        while position > 0:
        
            if data[position] != "\x00":
                name = data[position] + name
                position -= 1
                continue
            
            # The current byte is a zero byte. It is preceded by two
            # identifier bytes.
            identifier = self.read_word(data[position-2:position] + "\x00\x00")
            
            # The identifier can be used to access the style definition via
            # the main table in the same way as document structure definitions.
            reference = Reference(self, identifier & 0xff, identifier >> 8, 0)
            
            # Before these are three unknown bytes.
            unknown1 = data[position-4:position-2]
            # Before this is another unknown byte, usually found with the
            # string length byte.
            # According to information in an internal data dump, this is the
            # type of structure that the style definition describes.
            structure_type = ord(data[position-5:position-4])
            # Before this is a byte containing the length of the string.
            length = ord(data[position-6:position-5])
            styles[identifier] = Style(name, length, structure_type, position - 6, reference, others = (unknown1,))
            
            name = ""
            
            # Move to the end of the previous definition, or to the start of
            # the table.
            position -= 7
            
            if data[position] == "\x00":
            
                # The beginning of the table (assuming that only 255 styles
                # can be defined).
                number = ord(data[position-1:position])
                break
        
        return styles
    
    def close(self):
    
        self.input_file.close()
    
    def show_structure(self, indent = 0, parent = None):
    
        if parent is None:
            try:
                parent = self.document_structure
            except AttributeError:
                return
        
        print indent * "  ", parent, parent.style.name
        
        for obj in parent:
        
            if isinstance(obj, Structure):
                self.show_structure(indent + 1, obj)
            else:
                if hasattr(obj, "style"):
                    if isinstance(obj.style, Reference):
                        style = "[unnamed style at %x]" % obj.style.dereference().location
                    else:
                        style = obj.style.name
                else:
                    style = ""
                print (indent + 1) * "  ", obj, style
