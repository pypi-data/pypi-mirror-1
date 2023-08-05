#!/usr/bin/env python

import libxml2dom.xmpp
import sys

sender = "sender" in sys.argv
receiver = "receiver" in sys.argv
if not (sender or receiver):
    print "Please specify sender or receiver."
    sys.exit(1)

s = libxml2dom.xmpp.Session(("localhost", 5222))
d = s.connect("jeremy")
print "---- 1 ----"
print d.toString()

auth = s.createAuth()
auth.mechanism = "PLAIN"
auth.setCredentials("paulb@jeremy", "paulb", "jabber")
d = s.send(auth)
print "---- 2 ----"
print d.toString()

d = s.connect("jeremy")
print "---- 3 ----"
print d.toString()

iq = s.createIq()
iq.makeBind()
if sender:
    iq.bind.resource = "sender"
else:
    iq.bind.resource = "receiver"
d = s.send(iq)
print "---- 4 ----"
print d.toString()

iq = s.createIq()
iq.makeSession("jeremy")
d = s.send(iq)
print "---- 5 ----"
print d.toString()

if sender:
    message = s.createMessage()
    message.from_ = "paulb@jeremy/sender"
    message.to = "paulb@jeremy/receiver"
    message.type = "chat"
    body = message.ownerDocument.createElement("body")
    message.appendChild(body)
    text = message.ownerDocument.createTextNode("Hello!")
    body.appendChild(text)
    print message.toString()
    d = s.send(message)

# vim: tabstop=4 expandtab shiftwidth=4
