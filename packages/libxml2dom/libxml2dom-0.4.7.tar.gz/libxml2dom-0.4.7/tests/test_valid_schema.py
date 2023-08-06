#!/usr/bin/env python

import libxml2dom

schema = libxml2dom.parse("tests/test_valid_schema.xml")
d = libxml2dom.parse("tests/test_valid.xml")
print d.validate(schema)
print d.validateDocument(schema)
print d.getParameter("error-handler")

schema = libxml2dom.parse("tests/test_invalid_schema.xml")
d = libxml2dom.parse("tests/test_invalid.xml")
print d.validate(schema)
print d.validateDocument(schema)
print d.getParameter("error-handler")

# vim: tabstop=4 expandtab shiftwidth=4
