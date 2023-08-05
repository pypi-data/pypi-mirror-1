#!/usr/bin/env python

"""
SVG-specific document support. See: 
http://www.w3.org/TR/SVGMobile12/python-binding.html

Copyright (C) 2007 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import libxml2dom
from libxml2dom.macrolib import *
from libxml2dom.macrolib import \
    createDocument as Node_createDocument, \
    parseString as Node_parseString, parseURI as Node_parseURI, \
    parseFile as Node_parseFile, \
    toString as Node_toString, toStream as Node_toStream, \
    toFile as Node_toFile

SVG_NAMESPACE = "http://www.w3.org/2000/svg"

class SVGImplementation(libxml2dom.Implementation):

    "Contains an SVG-specific implementation."

    # Wrapping of documents.

    def adoptDocument(self, node):
        return SVGDocument(node, self)

    # Factory functions.

    def get_node(self, _node, context_node):
        if Node_nodeType(_node) == context_node.ELEMENT_NODE and \
            Node_namespaceURI(_node) == SVG_NAMESPACE:

            if Node_localName(_node) == "svg":
                return SVGSVGElement(_node, self, context_node.ownerDocument)
            else:
                return SVGElement(_node, self, context_node.ownerDocument)
        else:
            return libxml2dom.Implementation.get_node(self, _node, context_node)

class SVGElement(libxml2dom.Node): # Element, EventTarget, TraitAccess, ElementTraversal

    "An SVG-specific element."

    def _id(self):
        return self.getAttribute("id")

    def _setId(self, value):
        self.setAttribute("id", value)

    id = property(_id, _setId)

class SVGLocatable:

    "A locatable interface."

class SVGLocatableElement(SVGElement, SVGLocatable):

    "A locatable element."

class SVGSVGElement(SVGLocatableElement): # SVGTimedElement

    "An SVG-specific top-level element."

    NAV_AUTO = 1
    NAV_NEXT = 2
    NAV_PREV = 3
    NAV_UP = 4
    NAV_UP_RIGHT = 5
    NAV_RIGHT = 6
    NAV_DOWN_RIGHT = 7
    NAV_DOWN = 8
    NAV_DOWN_LEFT = 9
    NAV_LEFT = 10
    NAV_UP_LEFT = 11

class SVGDocument(libxml2dom.Document):

    "An SVG-specific document node."

    # NOTE: Define global (SVGGlobal).

# Convenience functions.

def parse(stream_or_string, html=0, htmlencoding=None):
    return libxml2dom.parse(stream_or_string, html, htmlencoding, default_impl)

def parseFile(filename, html=0, htmlencoding=None):
    return libxml2dom.parseFile(filename, html, htmlencoding, default_impl)

def parseString(s, html=0, htmlencoding=None):
    return libxml2dom.parseString(s, html, htmlencoding, default_impl)

def parseURI(uri, html=0, htmlencoding=None):
    return libxml2dom.parseURI(uri, html, htmlencoding, default_impl)

# Single instance of the implementation.

default_impl = SVGImplementation()

# vim: tabstop=4 expandtab shiftwidth=4
