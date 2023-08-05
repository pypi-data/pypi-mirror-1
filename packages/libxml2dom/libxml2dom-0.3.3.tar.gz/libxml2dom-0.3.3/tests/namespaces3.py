#!/usr/bin/env python

import libxml2dom

document = libxml2dom.createDocument(None, "doc", None)
e = document.xpath("*")[0]
e.setAttributeNS("xxx", "yyy", "zzz")
e.setAttributeNS("xxx", "yyy", "zzz")
e.setAttributeNS("xxx", "x:yyy", "zzz")
e.setAttributeNS("xxx", "x:yyy", "zzz")
print document.toString()

# vim: tabstop=4 expandtab shiftwidth=4
