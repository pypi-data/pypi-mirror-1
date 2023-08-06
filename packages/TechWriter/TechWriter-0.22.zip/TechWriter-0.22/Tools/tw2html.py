#!/usr/bin/env python

"""
tw2html.py - An HTML writer tool for the TechWriter Python package.

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

import sys

from TechWriter import document
from TechWriter.Writers import htmlwriter

if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.stderr.write("Usage: %s <input file> <output HTML file> <output CSS file>\n" % sys.argv[0])
        sys.exit(1)
    
    else:
        input_file = sys.argv[1]
        output_html_file = sys.argv[2]
        output_css_file = sys.argv[3]
    
    doc = document.Document(input_file)
    writer = htmlwriter.HTMLWriter(doc)
    writer.write(output_html_file, output_css_file)
    sys.exit()
