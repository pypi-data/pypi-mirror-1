#  Copyright (C) 2008 by Walter Cruz
#  waltercruz@gmail.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the
#  Free Software Foundation, Inc.,
#  59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Public License can be found at http://www.gnu.org/copyleft/gpl.html

import boo_box
from boo_box.affiliates import submarino
from xml.dom.minidom import parseString, Document
from nose.tools import raises

class TestBooBox(object):
    def test_json(self):
        boo = boo_box.Box(submarino,'173097').get('JSON','livros json')
        assert boo.startswith('jsonBooboxApi')

    def test_xml(self):
        boo = boo_box.Box(submarino,'173097').get('XML','livros xml')
        xmltree = parseString(boo)
        assert isinstance(xmltree,Document)

    def test_object(self):
        boo = boo_box.Box(submarino,'173097').get('object','livros xml')
        assert isinstance(boo,dict)

    @raises(NotImplementedError)
    def test_pdf(self):
        boo = boo_box.Box(submarino,'173097').get('pdf','livros xml')
