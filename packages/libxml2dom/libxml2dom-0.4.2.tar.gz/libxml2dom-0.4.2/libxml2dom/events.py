#!/usr/bin/env python

"""
DOM Level 3 Events support, with SVG Tiny 1.2 implementation additions.
See: http://www.w3.org/TR/DOM-Level-3-Events/events.html

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

import time

XML_EVENTS_NAMESPACE = "http://www.w3.org/2001/xml-events"

class EventException(Exception):

    UNSPECIFIED_EVENT_TYPE_ERR = 0
    DISPATCH_REQUEST_ERR = 1

class DocumentEvent:

    "An event interface supportable by documents."

    def canDispatch(self, namespaceURI, type):
        raise NotImplementedError, "canDispatch"

    def createEvent(self, eventType):
        raise NotImplementedError, "createEvent"

class Event:

    "An event class."

    CAPTURING_PHASE = 1
    AT_TARGET = 2
    BUBBLING_PHASE = 3

    def __init__(self, target, currentTarget):

        "Initialise the event."

        self.target = target
        self.currentTarget = currentTarget
        self.defaultPrevented = 0

        # Initialised later:

        self.type = None
        self.namespaceURI = None

        # DOM Level 3 Events:

        self.bubbles = None
        self.eventPhase = self.CAPTURING_PHASE
        self.timeStamp = time.time()

    def initEvent(self, eventTypeArg, canBubbleArg, cancelableArg):
        self.initEventNS(None, eventTypeArg, canBubbleArg, cancelableArg)

    def initEventNS(self, namespaceURIArg, eventTypeArg, canBubbleArg, cancelableArg):
        self.namespaceURI = namespaceURIArg
        self.type = eventTypeArg
        self.bubbles = canBubbleArg
        self.cancelable = cancelableArg

    def preventDefault(self):
        self.defaultPrevented = 1

    def stopPropagation(self):
        pass

    def stopImmediatePropagation(self):
        pass

class EventTarget:

    "An event target class."

    def __init__(self):
        self.listeners = {}

    def addEventListener(self, type, listener, useCapture):
        self.addEventListenerNS(None, type, listener, useCapture)

    def addEventListenerNS(self, namespaceURI, type, listener, useCapture):
        if not self.listeners.has_key((namespaceURI, type)):
            self.listeners[(namespaceURI, type)] = []
        self.listeners[(namespaceURI, type)].append((listener, useCapture))

    def dispatchEvent(self, evt):
        if not evt.type:
            raise EventException(EventException.UNSPECIFIED_EVENT_TYPE_ERR)
        # Dispatch on namespaceURI, type.
        for listener in self.listeners.get((evt.namespaceURI, evt.type), []):
            listener.handleEvent(evt)
        return evt.defaultPrevented

    def removeEventListener(self, type, listener, useCapture):
        self.removeEventListenerNS(None, type, listener, useCapture)

    def removeEventListenerNS(self, namespaceURI, type, listener, useCapture):
        if self.listeners.has_key((namespaceURI, type)):
            listeners = self.listeners[(namespaceURI, type)]
            try:
                listeners.remove((listener, useCapture))
            except ValueError:
                pass

# vim: tabstop=4 expandtab shiftwidth=4
