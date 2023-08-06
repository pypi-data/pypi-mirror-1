"""
Copyright (c) 2008-2009 H. Turgut Uyar <uyar@tekir.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import warnings
from imdb.utils import escape4xml

from imdbpykit.app import STATIC_DIR


try:
    from lxml import etree
    from lxml.etree import fromstring, tostring
    from lxml import html
    XSLT_AVAILABLE = True
except ImportError:
    from imdb.parser.http.bsouplxml import etree
    from imdb.parser.http.bsouplxml.etree import fromstring, tostring
    XSLT_AVAILABLE = False


def get_transform(template):
    if not XSLT_AVAILABLE:
        warnings.warn("XSLT transformation is not available")
        return None
    template = template.replace('select="document(\'',
                                'select="document(\'file://%s/' % STATIC_DIR)
    parsed = etree.fromstring(template)
    transform = etree.XSLT(parsed)
    return transform

def apply_transform(transform, text, pretty_print=False):
    if not XSLT_AVAILABLE:
        raise NotImplementedError("XSLT transformation is not available")
    dom = etree.fromstring(text)
    root = transform(dom).getroot()
    return html.tostring(root, pretty_print=pretty_print)

def appendchild(parent, tagname, text=None):
    if XSLT_AVAILABLE:
        child = etree.Element(tagname)
        if text is not None:
            child.text = text
    else:
        dom = parent.findParent('[document]')
        child = etree.Element(dom, tagname)
        if text is not None:
            child.append(escape4xml(text))
    parent.append(child)
    return child

def find_all_elements(root):
    if XSLT_AVAILABLE:
        return root.xpath("//*")
    else:
        return root.findAll(True)
