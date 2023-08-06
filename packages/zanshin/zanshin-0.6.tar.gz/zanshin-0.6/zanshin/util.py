# Copyright (c) 2005-2008 Open Source Applications Foundation.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions: 
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
__doc__ = """
Utility functions for zanshin.

@var DAV_NAMESPACE: The namespace for XML elements defined by the
                    WebDAV spec (RFC 2518).
"""

__all__ = (
    'blockUntil',
    'parseConfigFromUrl',
    'DAV_NAMESPACE',
    'PackElement',
    'UnpackElement',
    'ElementTree',
)

import sys
from twisted.internet import reactor
from Queue import Queue
from twisted.python.failure import Failure
from twisted.internet.defer import maybeDeferred
from twisted.python import threadable

from  urlparse import urlsplit
import re


try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from elementtree import cElementTree as ElementTree



def parseConfigFromUrl(configUrl):
    """
    Extracts various constituent parts out of a URL.
    
    B{Example:}
    
    >>> parseConfigFromUrl('https://moi:secret@www.example.com:1443')
    (True, 'moi', 'secret', 'www.example.com', 1443, '/')

    @param configUrl: The input URL.
    @type configUrl: C{str} or C{unicode}
    @rtype: C{tuple}
    @return: The following 6 elements:
    
      - C{useSSL}:   (bool) True if the scheme is https, False if http    
      - C{username}: (string) [Default: ""]           These are ...
      - C{password}: (string) [Default: ""]           ... parsed out of...
      - C{host}:     (string) [Default: "localhost"]  ... the "netloc" part ...
      - C{port}:     (int)    [Default: 80/443]       .... of the URL
      - C{path}:     (string) The path part of the URL
            
    
    """
    
    try:
        scheme, netloc, path = urlsplit(configUrl)[:3]
    except Exception, exception:
        raise ValueError, \
            "Unexpected error %s trying to parse '%s' as a url" % (
                exception, configUrl), \
            sys.exc_info()[2]
    
    if path == "":
        path = "/"
    
    # Figure out the default port, and whether or not to use SSL
    scheme = scheme.lower()
    if scheme == "http":
        useSSL = False
        port = 80
    elif scheme == "https":
        useSSL = True
        port = 443
    elif not scheme:
        useSSL = None
        port = None
        host = None
    else:
        raise Exception, \
              "Unexpected scheme '%s' in URL '%s'" % (scheme, configUrl)
              
    # Set default username & password
    username = ""
    password = ""
              
    try:
    
        # split into at most 2 components
        atIndex = netloc.rfind("@")
        if atIndex == -1:
            hostAndPort = netloc
        else:
            hostAndPort = netloc[atIndex + 1:]
            
            # Split the remainder into at most 2 parts
            splitUserAndPass = netloc[:atIndex].split(":", 1)
            if 2 == len(splitUserAndPass):
                username, password = splitUserAndPass
            else:
                username = splitUserAndPass[0]

        splitHostAndPort = hostAndPort.split(":", 1)
        if 2 == len(splitHostAndPort):
            host = splitHostAndPort[0]
            port = int(splitHostAndPort[1])
        else:
            host = hostAndPort

    except Exception, exception:
        raise ValueError, \
              "Unexpected error %s trying to parse netloc '%s'" % (
                  exception, netloc), \
              sys.exc_info()[2]
        
    return (useSSL, username, password, host, port, path)
    

__firstTime = False

def blockUntil(function, *args, **keywords):
    """
    This is a little wrapper function around Twisted C{Deferred} objects,
    for use in unit/doc tests.
    
    It calls C{function}, and if that returns something other than a
    C{deferred} (or raises an exception), it returns or raises immediately.
    If C{function} does return a C{deferred}, it waits for it to fire, and
    returns a result or raises if the C{deferred} generates a C{Failure}.
    
    B{Examples:}
    
    >>> from twisted.internet import reactor
    >>> import sys, time
    >>> blockUntil(reactor.callInThread, time.sleep, 1)
    >>>
    
    >>> from twisted.web.client import getPage
    >>> blockUntil(getPage, 'http://bogus/')
    Traceback (most recent call last):
    ...
    DNSLookupError: ...: address 'bogus' not found: (...).
    >>>
    
    
    This function will currently only run reliably if the twisted reactor
    is running in a different thread from the calling thread, or if it isn't
    running at all. In the latter case, this function will start up the
    twisted reactor in a separate thread.
    
    @param function: The callable to invoke
    @type function: C{callable}
    
    @param args:
    @param keywords:
    
    @return: The result of the C{Deferred}
    @rtype: Arbitrary
    """

    queue = Queue(1)

    def _doit():

        try:
        
            deferred = maybeDeferred(function, *args, **keywords)
            deferred.addBoth(queue.put)
            
        except:
            queue.put(Failure(exc_tb=sys.exc_info()[2]))
    
    
    if threadable.isInIOThread():
        raise RuntimeError, "Can't use blockUntil in twisted thread!"
        
    reactor.callFromThread(_doit)
    
    res = queue.get(block=True)
    
    if isinstance(res, Failure):
        res.raiseException()
    else:
        return res

# Helpers for elementtree

DAV_NAMESPACE = "DAV:"

def PackElement(name, namespace=DAV_NAMESPACE):
    """
    Given an element name and optional namespace URI, return
    a string suitable for creating elements in the elementtree
    API (i.e. of the form "{namespace-uri}element-name")

    B{Examples:}
    
    >>> PackElement('propfind')
    '{DAV:}propfind'
    >>> PackElement('prop', 'http://example.com/dav')
    '{http://example.com/dav}prop'
    >>> PackElement('x', None)
    'x'
    >>> PackElement('y', '')
    'y'

    
    @param name: The element name
    @type name: C{str}
    
    @param namespace:The element namespace URI
    @type namespace: C{str}
    
    @return: If namespace is C{None} or the empty string, returns
             C{name}. Else, combines namespace and name in the
             above form.
    @rtype: C{str}
    """
    if namespace:
        return '{%s}%s' % (namespace, name)
    else:
        return name

UNPACK_RE = re.compile('^{(.*)}(.*$)')

def UnpackElement(qname):
    """
    Performs the reverse of C{PackElement}: Given an element tag, decomposes
    it into a 2-element tuple of name and namespace.

    B{Examples:}
    
    >>> UnpackElement('propfind')
    ('propfind', None)
    >>> UnpackElement('{http://example.com/dav}prop')
    ('prop', 'http://example.com/dav')
    >>> UnpackElement('{urn:ietf:params:xml:ns:caldav}limit-freebusy-set')
    ('limit-freebusy-set', 'urn:ietf:params:xml:ns:caldav')
    
    @param qname: An XML element tag, as reported by ElementTree.
    @type qname: C{str}
    
    @return: The element name and namespace.
    @rtype: C{tuple}
    """
    
    try:
        return tuple(reversed(UNPACK_RE.match(qname).groups()))
    except:
        return (qname, None)
    
    
    
