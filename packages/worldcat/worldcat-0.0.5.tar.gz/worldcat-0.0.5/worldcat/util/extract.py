# Copyright (C) 2008 Mark A. Matienzo
# 
# This file is part of worldcat, the Python WorldCat API module.
# 
# worldcat is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# worldcat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with worldcat.  If not, see <http://www.gnu.org/licenses/>.

# util/srumarc.py - Parse SRU response XML into pymarc objects

from cStringIO import StringIO

try:
    import xml.etree.ElementTree as ET  # builtin in Python 2.5
except ImportError:
    import elementtree.ElementTree as ET

import pymarc

from worldcat.exceptions import ExtractError

def extract_elements(xml, element='{http://www.loc.gov/MARC21/slim}record'):
    """worldcat.util.ns_extract: extract elements based on namespace
    
    This function will probably prove useful to anyone using SRURequests.
    """
    tree = ET.fromstring(xml)
    return tree.getiterator(element)

def pymarc_extract(xml):
    """worldcat.util.pymarc_extract: extract records to pymarc Record objects
    
    Requires pymarc >= 1.2. StringIO is used since xml.sax.XMLReader's
    parse objects (which pymarc.marcxml.parse_xml uses) expect a filename, a
    file-like object, or an InputSource object. 
    """
    pymarc_records = []
    records = extract_elements(xml)
    handler = pymarc.XmlHandler()
    for record in records:
        pymarc.parse_xml(StringIO(ET.tostring(record)), handler)
        pymarc_records.extend(handler.records)
    return pymarc_records