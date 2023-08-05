#!/usr/bin/env python

"""
DOM events support.

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

class EventException(Exception):

    UNSPECIFIED_EVENT_TYPE_ERR = 0
    DISPATCH_REQUEST_ERR = 1

class Event:

    CAPTURING_PHASE = 1
    AT_TARGET = 2
    BUBBLING_PHASE = 3

    def __init__(self):
        type
        target
        currentTarget
        eventPhase
        bubbles
        cancelable
        timeStamp
        namespaceURI
        defaultPrevented

    def initEvent(self, eventTypeArg, canBubbleArg, cancelableArg):
        pass

    def initEvent(self, eventTypeArg, canBubbleArg, cancelableArg):
        pass

    def initEventNS(self, namespaceURIArg, eventTypeArg, canBubbleArg, cancelableArg):
        pass

    def preventDefault(self):
        pass

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
        # NOTE: Dispatch on namespaceURI, type...

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
