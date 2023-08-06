# Copyright (c) 2005-2007 Open Source Applications Foundation.
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
WEBDAV API OVERVIEW
===================
    
    Since zanshin is a Twisted-based API, most of zanshin's methods return
    twisted C{deferred} objects. To avoid having a bunch of callbacks/errbacks
    in this document's example code, we're going to make use of a utility 
    function in zanshin that waits for Deferred objects to return.

     >>> from zanshin.util import blockUntil

    To start with, we need a server to test against. For testing purposes,
    zanshin comes preconfigured with a test WebDAV server, so let's start that
    up:
    
    >>> import zanshin.webdav_server as server
    >>> from twisted.internet import reactor
    >>> listenPort = blockUntil(reactor.listenTCP, 8081, server.getTestSite())
    
    The ServerHandle is what replaces the typical misleading terminology
    of "connection" in protocol libraries.  Normally a protocol library 
    does work directly with connections, but in HTTP connections may be
    dropped at the whim of the server, so instead we work with server handles.

    >>> from zanshin.webdav import ServerHandle

    A L{ServerHandle} object is instantiated with the host and port of
    a HTTP server. (The constructor has other parameterized arguments to specify
    username and password, and whether to enable TLS, but these don't apply
    for our simple server):

    >>> serverHandle = ServerHandle(host="localhost", port=8081)

    There's not a lot you want to do with a raw L{ServerHandle}. Without a
    specific resource to query, the only recommended action is to ping
    the server to see if it's there and supports HTTP.

    >>> blockUntil(serverHandle.ping)
    True

    >>> bogusServer = ServerHandle("bogushost")
    >>> blockUntil(bogusServer.ping)
    Traceback (most recent call last):
      ...
    ConnectionError: ...: address 'bogushost' not found: (...).

    

    RESOURCES
    ---------
        Besides being able to send and process HTTP requests, a L{ServerHandle}
        also maintains a cache of L{Resource} objects. The C{getResource} method
        enables you to get the resource for a given URI (or path).
         
        >>> root = serverHandle.getResource("/")
        >>> root.path
        '/'
        
        Note that C{getResource} doesn't talk to the server, it just returns
        a local object. However, a L{Resource} can be queried as to what
        features it supports:
        
        >>> blockUntil(root.supportsWebDAV)
        False

        In the default configuration, our test WebDAV server (like some
        others) does not support WebDAV functionality on the root folder.
        However, it does have a more interesting L{Resource}:
        
        >>> resource = serverHandle.getResource("/folder/")
        >>> blockUntil(resource.supportsWebDAV)
        True
        
        We can do a simple existence check:
        
        >>> blockUntil(resource.exists)
        True
        >>> blockUntil(serverHandle.getResource("/not-here").exists)
        False
        
        
        WebDAV resources have other properties we can ask about:
        
        >>> blockUntil(resource.supportsAcl)
        False
        >>> blockUntil(resource.supportsLocking)
        False
        
        As you can see, our basic server doesn't support much in the way
        of advanced WebDAV features!
        
        WebDAV also added concept of a *collection*, which like a directory
        in a filesystem (rather than a simple file). We can ask a given
        L{Resource} if it's a collection:
        
        >>> blockUntil(resource.isCollection)
        True
        
        and we can query a collection resource for its children:
        
        >>> blockUntil(resource.getAllChildren, includeParent=False)
        []

        In the case where we have write access to the server, we
        can go ahead and make a child collection:
        
        >>> child = blockUntil(resource.createCollection, "cake")
        >>> blockUntil(resource.getAllChildren, includeParent=False)
        [<Resource at 0x... (/folder/cake/)>]
        
        Of course, you can also create ordinary files:
        
        >>> f = blockUntil(child.createFile, "file", "Use this to escape!")
        >>> f.path
        '/folder/cake/file'
        >>> blockUntil(f.get).body
        'Use this to escape!'
        
        Collections or files can also be removed from the server:
        
        >>> blockUntil(child.delete)
        <zanshin.http.Response object at 0x...>
        >>> blockUntil(child.exists)
        False
        >>> blockUntil(f.exists)
        False
        
        Note that deleting a non-empty collection deletes all its subresources
        implicitly. (WebDAV has special ways to report the errors when some
        subresources can't be deleted for some reason).

    RAW METHOD REQUESTS
    -------------------
    
    It's possible to issue raw HTTP requests via L{ServerHandle}'s
    C{addRequest} method. This returns a C{Deferred} that will fire
    once the C{Request} has been processed.
    
    >>> from zanshin.http import Request
    >>> request = Request('GET', '/not-here', {}, None)
    >>> blockUntil(serverHandle.addRequest, request).status
    404
    >>> request = Request('GET', '/aFile', {}, None)
    >>> blockUntil(serverHandle.addRequest, request).body
    'Hello, world!\\n'
    
    Cleanup
    -------
    Lastly, we clean up our ServerHandle instance:
    
    >>> blockUntil(serverHandle.factory.stopFactory)
    >>> factory = listenPort.factory
    >>> blockUntil(listenPort.stopListening)
    >>> blockUntil(factory.stopFactory)
    [(True, None)]

@var CALDAV_NAMESPACE: The namespace URI used by the CalDAV specification.
@type CALDAV_NAMESPACE: C{str}

@var DEFAULT_RETRIES: By default, the number of retries a given L{ServerHandle}
                      will try any given HTTP request.
@type DEFAULT_RETRIES: C{int}

@var XML_CONTENT_TYPE: The value of the Content-Type: header sent with requests
                       containing XML bodies.
@type XML_CONTENT_TYPE: C{str}

"""

from twisted.web import http
from twisted.internet import defer

import zanshin.http
import zanshin.util
import zanshin.error
import zanshin.acl as acl
from zanshin.ticket import Ticket, getTicketInfoNodes

import urlparse
import urllib
import re
import mimetypes

DEFAULT_RETRIES = 3

try:
    from elementtree import ElementTree
except ImportError:
    from xml.etree import ElementTree

XML_CONTENT_TYPE = 'text/xml; charset="utf-8"'

CALDAV_NAMESPACE = "urn:ietf:params:xml:ns:caldav"

def quote(url):
    """
    A helper function that addresses the fact that Python's
    C{urllib} module doesn't deal well with unicode URIs.
    
    @param url: The URL to be quoted (%-escaped). Non-ASCII characters
                will be encoded using UTF-8.
    @type url: C{str}
    
    @return: The %-escaped URL.
    @rtype: C{str}
    """
    return urllib.quote(url.encode('utf-8'))
    
def unquote(url):
    """
    A helper function that addresses the fact that Python's
    C{urllib} module doesn't deal well with unicode URIs.
    
    @param url: The %-escaped URL to be unquoted. Non-ASCII characters
                will be decoded using UTF-8.
    @type url: C{str}
    
    @return: The %-unescaped URL.
    @rtype: C{str}
    """
    return urllib.unquote(url).decode('utf-8')


class PropfindRequest(zanshin.http.Request):
    """
    Subclass of L{zanshin.http.Request} that handles WebDAV PROPFIND
    requests.
    
    @cvar DEFAULT_PROPFIND_IDS: A list of property IDs we will always query
        for when issuing PROPFIND requests. This allows the webdav layer
        to reduce the number of requests it makes; for example, if a client
        makes a request for a resource's DAV:displayname, and subsequently
        its DAV:getetag, only one request to the server will be sent.
    @type DEFAULT_PROPFIND_IDS: C{list}
    """

    DEFAULT_PROPFIND_IDS = [zanshin.util.PackElement(x)
                            for x in "getetag", "resourcetype", "displayname"]

    def __init__(self, path, depth, props, extraHeaders):
        
        if props is None:
            props = []
        
        for prop in self.DEFAULT_PROPFIND_IDS:
            if not prop in props:
                props.append(prop)
        
        # Since we're going to be adding http headers of our
        # own, make a copy of extraHeaders if it was passed in.
        if extraHeaders is not None:
            extraHeaders = extraHeaders.copy()
        else:
            extraHeaders = {}

        # Content-Type: header ...
        extraHeaders['Content-Type'] = XML_CONTENT_TYPE
        
        # Depth: header ...
        if depth is None:
            depth = 0
        extraHeaders['Depth'] = str(depth)
        
        # @@@ [grant] Should we generate Accepts: for PROPFIND?
        #if not extraHeaders.has_key('Accepts'):
        #    extraHeaders['Accepts'] = "text/xml, application/xml"

        # & request body.
        
        propfindElement = ElementTree.Element(zanshin.util.PackElement("propfind"))

        propElement = ElementTree.SubElement(propfindElement,
                                             zanshin.util.PackElement("prop"))
        
        for thisProp in props:
            ElementTree.SubElement(propElement, thisProp)
            
        body = ElementTree.tostring(propfindElement, 'UTF-8')
        
        super(PropfindRequest, self).__init__('PROPFIND', path, extraHeaders,
                                              body)
    

class Resource(object):
    """ 
    A C{Resource} caches information about a  resource on the server.
    
        @type path: str
        @ivar path: The path part of the given resource's URI.
        
        @type serverHandle: ${ServerHandle}
        @ivar serverHandle: The owning ${ServerHandle} of this resource.
        
        @type davFeatures: C{list}
        @ivar davFeatures: The list of values returned in the DAV: header for
                       this resource

        @type allowedMethods: C{list}
        @ivar allowedMethods: The list of values returned in the Allow: header
                              for this resource 

        @type etag: C{str}
        @ivar etag: The value of the given resource's entity tag
        
        @ivar ticketId: The ticket (lightweight, insecure access control)
                        associated with this resource. For more information,
                        see the L{zanshin.ticket} module.
        @type ticketId: C{str}
    """
    
    ticketId = None
    
    _collection = None
    _calendar = None
    _displayName = None
    
    #
    # The pattern for Resource methods that need to send a request to the server
    # is:
    #
    # def doSomething(self, ...):
    #
    #   def handleX(response):
    #       ... update self's state, and return a
    #       ... value (possibly response, or something
    #       ... calculated)
    #
    #   request = zanshin.http.Request('X', self.path, ...)
    #   return self._addRequest(request).addCallback(handleX)
    #

    def __init__(self, serverHandle, path):
        self.path = path
        self.serverHandle = serverHandle
        self.davFeatures = []
        self.allowedMethods = []
        self.etag = None
        
        self._optionsResponse = None
        self._serverId = "unknown"

    def __repr__(self):
        res = u"<%s at 0x%x (%s)>" % (type(self).__name__, id(self), self.path)
        return res.encode('unicode_escape')

    def exists(self):
        """
        Sends one or more requests to determine whether the
        Resource is actually present on the server.
        
        @return: (deferred) True iff the resource exists
        @rtype: C{deferred}
        """
        
        path = quote(self.path)
        
        #
        # The logic here is kind of tricky:
        #
        # 1. If the server supports WebDAV and PROPFIND, we just send a
        #     PROPFIND request.
        #
        #     If that succeeds (i.e. returns a parse-able multistatus),
        #     we return True. Other cases:
        #
        #        404 Not Found => return False
        #        HTTP error => Fall back to case 2
        #
        #     we return False. All other HTTP statuses are treated
        #     as errors.
        #
        # 2. If PROPFIND doesn't work, or isn't supported, we
        #    just HEAD the resource, returning True on
        #    success, False on 404, and treating other codes
        #    as errors.
        #

        def handleHead(response):
            if response.status in (http.OK, http.NO_CONTENT):
                self._collection = False
                self._calendar = False
                self._displayName = ""
                self._extractETag(response)
                return True
            elif response.status == http.UNAUTHORIZED:
                raise PermissionsError(self.serverHandle.factory.username)
            else:
                return False
            
        def sendHeadRequest():
            result = self._addRequest(zanshin.http.Request('HEAD', path, {},
                                      None))
                
            result.addCallback(handleHead)
                
            return result
            
        def handlePropfindError(failure):
            if failure.check(zanshin.http.HTTPError):
               if http.NOT_FOUND == failure.value.status:
                   return False
               else:
                   return sendHeadRequest()
            return failure
            
        def handleOptions(response):
            if response.status == http.NOT_FOUND:
                return False
            if self.allowedMethods is not None and \
               'PROPFIND' in self.allowedMethods:
                result = self.propfind(depth=0)
                result.addCallbacks(lambda _:True, handlePropfindError)
            else:
                result = sendHeadRequest()
            return result
            
        def handleOptionsError(failure):
            if failure.check(zanshin.http.HTTPError):
                return handleOptions(failure.value)
            return failure

        result = self.options().addCallbacks(handleOptions, handleOptionsError)

        
        return result

    def _supportsDAVFeature(self, requestedFeature):
        callback = (lambda response:
            self.davFeatures is not None and
            requestedFeature in self.davFeatures)
        return self.options().addCallback(callback)

    def supportsWebDAV(self):
        return self._supportsDAVFeature("1")

    def supportsLocking(self):
        return self._supportsDAVFeature("2")

    def supportsAcl(self):
        return self._supportsDAVFeature("access-control")
        
    def supportsTickets(self):
        callback = (lambda _: "MKTICKET" in self.allowedMethods 
                        or "ticket" in self.davFeatures)
        return self.options().addCallback(callback)
        
    def supportsCalDAV(self):
        return self._supportsDAVFeature("calendar-access")
        
    def supportsCreateCalendar(self):
        return self.options().addCallback(
                lambda _: "MKCALENDAR" in self.allowedMethods)

    def _extractETag(self, response):
        if response.headers is not None:
            self._setETagObject(response.headers.getHeader('ETag'))
        return response

    def get(self):
        request = zanshin.http.Request('GET', quote(self.path), {}, None)
        
        result = self._addRequest(request).addCallback(self._extractETag)
        
        return result
    
    def __makeNewChildPath(self, bindingName, collection=False):
        newPath = ""
        newPath += self.path
        
        if newPath and newPath[-1] != "/":
            newPath += "/"
        newPath += bindingName

        # In WebDAV, collection names end in '/'
        if collection and newPath and newPath[-1] != "/":
            newPath += "/"
            
        return (newPath, quote(newPath))

    def __propagateSettings(self, child):
        ticketId = self.ticketId
        
        if ticketId is not None:
            child.ticketId = ticketId


    def createFile(self, bindingName, body="", type="text/plain",
                   extraHeaders=None):
        
        newPath, quotedNewPath = self.__makeNewChildPath(bindingName)
        
        # This is the callback that makes sure we can construct the
        # new resource from the response to the PUT request
        def handlePutResponse(response):
            if response.status in (http.OK,
                                   http.CREATED,
                                   http.NO_CONTENT):
                newResource = self.serverHandle.getResource(newPath)
                # @@@ [grant] Other fields (Last-Modified?) here
                newResource._extractETag(response)
                self.__propagateSettings(newResource)
                
                if newResource.etag is None:
                    deferred = newResource.propfind(depth=0)
                    
                    # Extract the first (and hopefully only) resource
                    # from the PROPFIND
                    deferred.addCallback(lambda resources: resources[0])
                    # Returning a deferred from a callback "chain"s
                    # it so that the next callback only gets called
                    # when the new deferred fires.
                    return deferred
                else:
                    return newResource
            else:
                # @@@ [grant] Are there other, non-error cases here?
                raise zanshin.http.HTTPError(status=response.status)
            
        
        if extraHeaders is None:
            extraHeaders = {}
            
        if not extraHeaders.has_key('content-type'):
            extraHeaders['content-type'] = type

        # We always send If-None-Match:, since this API
        # is used to create new files, not update existing
        # ones.
        extraHeaders ['if-none-match'] = '*'

        request = zanshin.http.Request('PUT', quotedNewPath,
                                       extraHeaders, body)

        return self._addRequest(request).addCallback(handlePutResponse)
        
    def put(self, body, checkETag=True, contentType=None, extraHeaders=None):
    
        def handlePutResponse(response):
            if response.status in (http.OK,
                                   http.CREATED,
                                   http.NO_CONTENT):
                self.etag = None
                self._extractETag(response)
                
                if self.etag is None:
                    d = self.propfind(depth=0)
                    d.addBoth(lambda _:None)
                    return d
            else:
                raise zanshin.http.HTTPError(status=response.status)
        
        extraExtraHeaders = {}
        if extraHeaders is not None:
            extraExtraHeaders.update(extraHeaders)
        
        if checkETag:
            etag = self.etag
            
            if not etag: etag = '*'

            extraExtraHeaders['if-match'] = etag
            

        path = quote(self.path)
        request = self.serverHandle._putRequest(path, body, contentType,
                                                None, extraExtraHeaders)
        result = self._addRequest(request)
        result.addCallback(handlePutResponse)
        return result
        
    def getUrl(self):
        """
        @return: A URI for the given Resource, taking into account its
                 L{ServerHandle}'s host, port and scheme.
        @rtype: C{str}
        """
        
        factory = self.serverHandle.factory
        
        host = factory.host
        port = factory.port
        
        if getattr(factory, 'startTLS', False):
            schema = 'https'
            defaultPort = 443
        else:
            schema = 'http'
            defaultPort = 80

        if port and port != defaultPort:
            host = u"%s:%d" % (host, port)
            
        path = quote(self.path.strip(u"/"))
        
        if self.ticketId is not None:
            path = u"%s?ticket=%s" % (path, self.ticketId)
        
        if self.path and self.path[-1] == '/':
            path = u'%s/' % (path,)
        
        return u"%s://%s/%s" % (schema, host, path)
        

    def createCollection(self, bindingName):
    
        newPath, quotedNewPath = \
            self.__makeNewChildPath(bindingName, collection=True)

        def handleMkcol(response):
            if http.CREATED == response.status:
                newResource = self.serverHandle.getResource(newPath)
                newResource._collection = True
                self.__propagateSettings(newResource)
                return newResource
            else:
                raise zanshin.http.HTTPError(status=response.status)

        request = zanshin.http.Request('MKCOL', quotedNewPath, {}, None)
        
        return self._addRequest(request).addCallback(handleMkcol)

    def isCollection(self):

        def _isCollection(self):
            if self._collection is None:
                raise zanshin.error.Error, \
                "PROPFIND for %s failed to return resourcetype" % (self.path)
            return self._collection
            
        def _fetchResourceType(self, result):

            if result: # i.e. we support WebDAV
                if ("PROPFIND" not in self.allowedMethods): 
                    raise zanshin.error.Error, \
                          "WebDAV resource %s does not show PROPFIND support" \
                          % (self)
                # Here, we return a new deferred: a PROPFIND request
                result = self.propfind(depth=0)
                # When it's done, we check to see if our resourcetype matches
                result = result.addCallback(lambda _: _isCollection(self))
                
            return result

        if self._collection is not None:
            # If we have the result cached, return
            # a fired deferred.
            result = defer.succeed(self._collection)
        else:
            # Make sure we support WebDAV (i.e. by sending options)
            result = self.supportsWebDAV()
        
            # Once that's done, fetch the resource type
            callback = lambda result: _fetchResourceType(self, result)
            result = result.addCallback(callback)
            
        return result
        
    
    def createCalendar(self, bindingName, displayName=None, timezone=None):
        """Create a CalDAV calendar collection.
        
        @param bindingName: The name of the resource for URLs
        @type  bindingName: C{str}
        
        @param displayName: An optional displayName.
        @type  displayName: C{str}

        @param timezone: An optional iCalendar object containing one VTIMEZONE
                         to be applied to the new calendar
        @type  timezone: C{str}
        
        @return:
        @rtype: C{deferred}
        
        """
        PackElement = zanshin.util.PackElement
        SubElement  = ElementTree.SubElement
        
        if displayName is not None or timezone is not None:
            # Set up CALDAV:mkcalendar body
            mkcal = ElementTree.Element(PackElement("mkcalendar", 
                                                    CALDAV_NAMESPACE))
            
            setElement  = SubElement(mkcal,      PackElement("set"))
            props       = SubElement(setElement, PackElement("prop"))
            
            if displayName is not False:
                nameElement = SubElement(props,  PackElement("displayname"))            
                nameElement.text = displayName
                        
            if timezone is not None:
                tz = SubElement(props, PackElement("calendar-timezone",
                                                   CALDAV_NAMESPACE))
                tz.text = "<![CDATA[" + timezone + "]]>"

            # ElementTree encodes the CDATA block with entities, decode them                
            body = ElementTree.tostring(mkcal, 'UTF-8').replace(
                      '&lt;![CDATA', '<![CDATA').replace(']]&gt;', ']]>')
        else:
            body = None

            
        newPath, quotedNewPath = \
            self.__makeNewChildPath(bindingName, collection=True)
        
        def handleMkCalendar(response):
            if response.status in (http.CREATED, http.OK):
                resource = self.serverHandle.getResource(newPath)
                resource._collection = True
                resource._calendar = True
                self.__propagateSettings(resource)
                return resource
            else:
                raise zanshin.http.HTTPError(status=response.status)
        
        request = zanshin.http.Request('MKCALENDAR', quotedNewPath, {}, body)
        return self._addRequest(request).addCallback(handleMkCalendar)

    def isCalendar(self):
        if self._calendar is not None:
            result = defer.succeed(self._calendar)
        else:
            # Piggy-back off of self.isCollection(), which checks that
            # PROPFIND is supported, etc.
            result = self.isCollection().addCallback(lambda _: self._calendar)
        return result
        
    def getFreebusy(self, start, end, depth=1, extraHeaders=None):
        """
        Issue a CalDAV:free-busy-query REPORT.
        
        @param depth: The depth to issue the report for. Valid values
                      are 0, 1, 'infinity' and None
        @type depth: C{int}
        
        @param start: The start datetime to get free-busy info for
        @type start: C{datetime}

        @param end: The start datetime to get free-busy info for
        @type end: C{datetime}
        
        @return:
        @rtype: C{deferred}
        """
        
        def caldavDateFormat(dt):

            zulu = ""
            offset = dt.utcoffset() # A datetime.timedelta
            
            if offset is not None: # Convert to UTC (Zulu) if possible
                dt = dt - offset
                zulu = "Z"
                
            result = "%d%02d%02dT%02d%02d%02d%s" % (
                        dt.year, dt.month, dt.day,
                        dt.hour, dt.minute, dt.second, zulu)
            
            return result
            
        
        def handleReportResponse(resp):
            if resp.status == http.OK:
                return resp
            else:
                raise zanshin.http.HTTPError(status=resp.status,
                                             message=resp.message)

        query = ElementTree.Element(zanshin.util.PackElement("free-busy-query",
                                                             CALDAV_NAMESPACE))

        timeRange = ElementTree.SubElement(
                        query,
                        zanshin.util.PackElement("time-range", 
                                                 CALDAV_NAMESPACE),
                        attrib = {"start": caldavDateFormat(start),
                                  "end": caldavDateFormat(end)})
        
        body = ElementTree.tostring(query, 'UTF-8')
        
        if extraHeaders is not None:
            extraHeaders = extraHeaders.copy()
        else:
            extraHeaders = {}

        # Content-Type: header ...
        extraHeaders['Content-Type'] = XML_CONTENT_TYPE

        if depth is not None:
            extraHeaders['Depth'] = str(depth)
        
        request = zanshin.http.Request('REPORT', quote(self.path),
                                       extraHeaders, body)
                                       
        d = self._addRequest(request)
        d.addCallback(handleReportResponse)
        
        return d

    def getPrivileges(self, extraHeaders=None):
        """
        Issue a PROPFIND for CalDAV:current-user-privilege-set and
        ticketdiscovery, merging the results together into one 
        CurrentUserPrivilegeSet.
                
        @return: An acl.CurrentUserPrivilegeSet
        @rtype: C{deferred}
        """

        cupsId = zanshin.util.PackElement('current-user-privilege-set')
        ticketDiscId = zanshin.util.PackElement("ticketdiscovery",
                                                Ticket.TICKET_NAMESPACE)

        result = self._addRequest(
                    PropfindRequest(quote(self.path), 0, [cupsId, ticketDiscId],
                             extraHeaders))

        def handlePropfindResponse(resp):
            if resp.status == http.MULTI_STATUS:
                try:
                    cups = acl.CurrentUserPrivilegeSet.parse(resp.body)
                except ValueError:
                    # Some servers ignore the CUPS request, which is illegal,
                    # but tolerate it and just return an empty privilege set
                    cups = acl.CurrentUserPrivilegeSet()
                    
                for node in getTicketInfoNodes(resp.body):
                    ticket = Ticket.parse(node)
                    for privName, value in ticket.privileges.iteritems():
                        # the ticket privileges dictionary currently doesn't
                        # have the flexibility to handle namespaces, that should
                        # probably be added.
                        if value and (privName, "DAV:") not in cups.privileges:
                            cups.privileges.append((privName, "DAV:"))
                
                return cups
            else:
                raise zanshin.http.HTTPError(status=resp.status,
                                             message=resp.message)
                
        result.addCallback(handlePropfindResponse)
        
        return result

    def __headerValues(self, response, key):
        result = None
        values = response.headers.getRawHeaders(key)

        if values is not None:
        
            for headerValue in response.headers.getRawHeaders(key):
        
                splitter = re.compile(',\s*')
                    
                if result is None:
                    result = []
                result.extend(splitter.split(headerValue))

        return result

    def getAllChildren(self, includeParent=True):
        """
        This method will build a list of Resources. For faster
        synching and identification of new resources, we get the etag and
        getlastmodified properties of all the children. This method only
        works if the server supports PROPFIND but eventually we might be
        able to make it work for HTTP as well by groveling through HTML for
        relative URLs.
    
        @param includeParent: Whether or not to include the receiver in
            the returned list.
        @type includeParent: C{boolean}
        
        @return: (deferred) C{list} of child resources
        @rtype: C{deferred}
        """
        return self.propfind(depth=1, includeParent=includeParent)

    def options(self):

        def handleOptionsResponse(response):
            self._optionsResponse = response
            if (self._optionsResponse.status == http.UNAUTHORIZED):
                raise PermissionsError(self.serverHandle.factory.username)
    
            self._serverId = self._optionsResponse.headers.getHeader("Server")
    
    
            self.davFeatures = self.__headerValues(self._optionsResponse, "DAV")
            self.allowedMethods = \
                self._optionsResponse.headers.getHeader("Allow")
            return self._optionsResponse

        if self._optionsResponse is None:
            request = zanshin.http.Request('OPTIONS', quote(self.path), {},
                                           None)

            result = self._addRequest(request)
            result = result.addCallback(handleOptionsResponse)
        else:
            result = defer.succeed(self._optionsResponse)
            
        return result
    
    def setDisplayName(self, displayName):
        """
        Set the display name of this resource, by patching the
        DAV:displayname property from the server.
        
        @param displayName: The new display name (unicode is fine).
        @type displayName: C{str}
        
        @return: (Deferred) None
        @rtype: C{deferred}
        
        """
        def handleProppatch(results):
            # If the server really did change DAV:displayname,
            # go ahead and modify self._displayName, to reflect
            # the current knowledge the property value on the
            # server..
            result = results.get(zanshin.util.PackElement("displayname"), None)
            
            status = None
            
            # result should be of the form 'HTTP/1.1 200 OK'
            # We want to extract the int value of the 2nd
            # field, if possible,
            if result is not None:
                try:
                    status = int(result.split()[1])
                except (TypeError, IndexError):
                    # IndexError: no spaces in result
                    # TypeError: field wasn't an int
                    pass
                
            if status in (http.CREATED, http.OK):
                self._displayName = displayName
        
        propstopatch = { zanshin.util.PackElement("displayname"): displayName }
        
        deferred = self.proppatch(propstopatch)
        
        return deferred.addCallback(handleProppatch)
    
    def getDisplayName(self):
        """
        Return the display name of this resource, by fetching the
        DAV:displayname property from the server.
        
        @return: (Deferred) The C{unicode} display name of the resource.
        @rtype: C{deferred}
        
        """
        
        def handlePropfind(__):
            
            result = self._displayName
            
            if not result:
                # i.e. didn't manage to fetch it (None), or
                # not defined on server ("")
                
                path = self.path.strip("/")
                
                try:
                    result = path.split("/")[-1]
                except IndexError:
                    result = ""
                    
            return result
            
        if self._displayName is None: # Haven't fetched it yet
            deferred = self.propfind(depth=0).addCallback(handlePropfind)
        else:
            deferred = defer.succeed(handlePropfind(None))
            
        return deferred

    def delete(self, extraHeaders=None):
        """
        Removes the given resource from the server. Note that
        WebDAV semantics mean that non-empty collection resources
        can be deleted. If successful, removes any cached information
        from the given resource.
        
        @param extraHeaders: Any extra HTTP headers you would like to accompany
                             the DELETE request.
        @type extraHeaders: C{dict}
        
        @return: A deferred C{Response} object.
        @rtype: C{deferred}
        """

        def handleDeleteResponse(response):
            if response.status == http.NO_CONTENT:
                self._optionsResponse = None
                self._serverId = None
                self.davFeatures = None
                self.allowedMethods = None
                self._collection = None
                self._calendar = None
                self._displayName = None
            return response

        request = zanshin.http.Request('DELETE', quote(self.path), extraHeaders,
                                       None)

        # On success, invalidate the OPTIONS cache
        # for this resource.
        return self._addRequest(request).addCallback(handleDeleteResponse)
        
    def _setETagObject(self, etagObject):
        # @@@ [grant] This basically ignores the "W/" part of
        # the etag.
        if etagObject is not None:
            self.etag = etagObject.tag.encode('utf-8')
        else:
            self.etag = None
        
    def propfind(self, props=None, depth=None, extraHeaders=None,
                 includeParent = True):
    
        def handleHeadResponse(response):
            if http.OK == response.status:
                self._setETagObject(response.headers.getHeader('ETag'))
                self._collection = False
                self._calendar = False
                self._displayName = None
                
                return self
            else:
                raise zanshin.http.HTTPError(status=response.status)
        
        def handlePropfind(response):
            if response.status in (http.UNAUTHORIZED, http.FORBIDDEN,
                                   http.NOT_ALLOWED) and \
                self.path[-1] != '/':
                request = zanshin.http.Request('HEAD', quote(self.path), {},
                                               None)
                return self._addRequest(request).addCallback(handleHeadResponse)
            
            if response.status != http.MULTI_STATUS:
                raise zanshin.http.HTTPError(status=response.status)
            
            if getattr(response, 'body', None) is None:
                # @@@ [grant] Raise some kind of error
                pass
            
            # Now, parse the multistatus response and fills the resource cache
            # with resource objects.
            resources = []

            rootElement = ElementTree.XML(response.body)
            foundSelf = False
            
            for rsrc, props in self._iterPropfindElement(rootElement):
            
                if rsrc is self:
                    foundSelf = True
                
                etagObject = None
                collection = False
                calendar = False
                displayName = ""
            
                for prop in props:

                    propName = prop.tag
                    
                    if zanshin.util.PackElement("getetag") == propName:
                        etagObject = zanshin.http.ETag.parse(prop.text)
                    elif zanshin.util.PackElement("resourcetype") ==  propName:
                        collection, calendar = self._extractResourceType(prop)
                    elif zanshin.util.PackElement("displayname") == propName:
                        displayName = prop.text
                        
                rsrc._setETagObject(etagObject)
                rsrc._collection = collection
                rsrc._calendar = calendar
                rsrc._displayName = displayName
            
                if includeParent or rsrc is not self:
                    self.__propagateSettings(rsrc)
                    resources.append(rsrc)
                        
            # Return the list of resource objects
            if not foundSelf:
                # Bug 4977: We raise a 404 in the case where
                # self's URI was not included in the returned
                # multistatus
                raise zanshin.http.HTTPError(status=http.NOT_FOUND)

            return resources

        request = PropfindRequest(quote(self.path), depth, props, extraHeaders)
        return self._addRequest(request).addCallback(handlePropfind)


    def _iterPropfindElement(self, propfind):
        #
        # A generator for the Resource & property values in a multistatus
        # xml document.
        #
        # Input: propfind, an ElementTree.Element
        #
        # Yields: (resource, propNodes), where resource is a
        #         zanshin.webdav.Resource, and propNodes is a
        #         (possibly empty) list of zanshin.util.xmlNode
        #         objects.
        
        def iterMatches(parent, tag):
            # Helper to iterate over children of a node that
            # match a certain xml namespace & name.
            for child in parent:
                if tag == child.tag:
                    yield child

        for responseNode in iterMatches(propfind, zanshin.util.PackElement("response")):
            url = None
            props = []
            
            # We remember the resourcetype element, because if it
            # indicates we have a collection, we might need to
            # append a '/' to url.
            resTypeNode = None
    
            for child in responseNode:
                    
                if zanshin.util.PackElement("href") == child.tag:
                    url = child.text # @@@: [grant] URL canonicalization/quoting
                elif zanshin.util.PackElement("propstat") == child.tag:
                    
                    for propNode in iterMatches(child, zanshin.util.PackElement("prop")):
                        
                        for propChild in propNode:
                            props.append(propChild)
                        
                            if zanshin.util.PackElement("resourcetype") == propChild.tag:
                                resTypeNode = propChild
        
            ### NB -- self.path is unquoted, so self.path in Request objects
            ### must be quoted
            if url is not None:
                if (resTypeNode is not None and
                    (url == "" or url[-1:] != "/") and
                    self._extractResourceType(resTypeNode)[0]):
                
                        url += "/"
                resource = self.serverHandle.getResource(unquote(url))
                    
                yield (resource, props)


    def _extractResourceType(self, resourcetypeNode):
        collection = calendar = False
        
        for child in resourcetypeNode:
            tag = child.tag
            if zanshin.util.PackElement("collection") == tag:
                collection = True
            if zanshin.util.PackElement("calendar", CALDAV_NAMESPACE) == tag:
                calendar = True

        return (collection, calendar)
        
    def proppatch(self, propValues, extraHeaders={}):
        """
        Send a PROPPATCH request for this resource to modify or delete
        one or more WebDAV properties.
        
        @param propValues: The values to set/remove for this resource.
        @type propValues: C{dict}. Keys are strings (qnames), values
            can be C{None} (if you want to remove the property),
            C{str}/C{unicode} objects, or objects implementing
            C{serialize()}.
            
        @param extraHeaders: Any extra HTTP headers you would like to
            accompany the PROPPATCH request.
        @type extraHeaders: C{dict}
            
        @return: A dictionary whose keys are PackElement strings, and
                 values are status strings, like "HTTP/1.1 200 OK".
        @rtype: C{dict}
        """
        
        def handleProppatchResponse(response):
            # Set up the returned dictionary
            results = {}

            if response.status in (http.OK, http.CREATED):
                for key in propValues.keys():
                    results[key] = "HTTP/1.1 200 OK"
                return results
                
            if response.status != http.MULTI_STATUS:
                raise zanshin.http.HTTPError(status=response.status)
            
            rootElement = ElementTree.XML(response.body)

            if zanshin.util.PackElement("multistatus") != \
                rootElement.tag:
                raise ValueError, \
                "Expected PROPPATCH response to be a DAV:multistatus, got %s" \
                     % (rootElement.tag, )
                    
            responseElt = None
                    
            for child in rootElement:
                if zanshin.util.PackElement("response") == child.tag:
                    responseElt = child
                    break
                
            if responseElt is None:
                raise ValueError, \
                "Expected PROPPATCH response to contain DAV:response"
                
            for child in responseElt:
                if zanshin.util.PackElement("propstat") == child.tag:
                    
                    props = []
                    stat = None
                    
                    for psChild in child:
                        if zanshin.util.PackElement("prop") == psChild.tag:
                            props.extend(propChild.tag for propChild in psChild)
                        elif zanshin.util.PackElement("status") == psChild.tag:
                            stat = psChild.text

                    if stat is not None:
                        for p in props:
                            results[p] = stat

            return results

        
        propupdateElement = ElementTree.Element(zanshin.util.PackElement("propertyupdate"))
        setElement = None
        removeElement = None
        
        for prop, value in propValues.iteritems():

            if value is None: # property deletion case
                if removeElement is None:
                    removeElement = ElementTree.SubElement(propupdateElement,
                                                           zanshin.util.PackElement("remove"))
                propElement = ElementTree.SubElement(removeElement,
                                                     zanshin.util.PackElement("prop"))
                ElementTree.SubElement(propElement, prop)
            else:
                if setElement is None:
                    setElement = ElementTree.SubElement(propupdateElement,
                                                        zanshin.util.PackElement("set"))
                
                propElement = ElementTree.SubElement(setElement,
                                                     zanshin.util.PackElement("prop"))
                
                valueElement = ElementTree.SubElement(propElement,prop)
                
                if isinstance(value, (str, unicode)):
                    valueElement.text = value
                else:
                    value.serialize(valueElement)

        body = ElementTree.tostring(propupdateElement, 'UTF-8')

        
        request = zanshin.http.Request('PROPPATCH', quote(self.path),
                                       extraHeaders, body)
                                       
        d = self._addRequest(request)
        d.addCallback(handleProppatchResponse)
        
        return d

    
    def getAcl(self, depth=0, extraHeaders=None):
        """
        Get the ACL associated with the given resource.
        
        @param depth: cf. PropfindRequest
        @type depth: C{int}
        
        @param extraHeaders: Any extra HTTP headers to be sent
            with the C{Request} that fetches the ACL.
        @type extraHeaders: C{dict}
        
        @return: The (deferred) L{webdav.acl.ACL} representing the ACL
                 returned by the server.
        @rtype: C{deferred}
        """
       
        aclPropId = zanshin.util.PackElement('acl')

        result = self._addRequest(
                    PropfindRequest(quote(self.path), depth, [aclPropId],
                             extraHeaders))
        
        # Turn the C{HTTPResponse} object we get
        # back from the deferred into an ACL object:
        result.addCallback(lambda response: acl.ACL.parse(response.body))
        
        return result

    def _addRequest(self, request):
        ticketId = getattr(self, 'ticketId', None)
        if ticketId is not None:
            def ticketAuth(client):
                client.sendHeader('Ticket', ticketId)
            request.sendAuth = ticketAuth

        return self.serverHandle.addRequest(request)
        
    def __sendXmlRequest(self, method, body, extraHeaders):
        if extraHeaders is not None:
            headers = extraHeaders.copy()
        else:
            headers = {}
        headers['Content-Type'] = XML_CONTENT_TYPE
        
        if isinstance(body, unicode):
            body = body.encode('utf-8')
        
        request = zanshin.http.Request(method, quote(self.path), headers, body)
        return self._addRequest(request)


    def setAcl(self, newAcl, extraHeaders=None):
        """
            Set the ACL associated with the given resource.
            
            @param extraHeaders: Any extra HTTP headers to be sent
                with the ACL C{Request}
            @type extraHeaders: dict
            
            @param newAcl: The ACL object you want to set
                        for this resource (currently, an XML string would
                        work, too, but this isn't guaranteed to be the
                        case in the future).
            @type newAcl: L{webdav.acl.ACL}
                        
            @return: (Deferred) to the L{zanshin.http.Response} to the
                     ACL request.
            @rtype: C{deferred}
        """
        return self.__sendXmlRequest('ACL', unicode(newAcl), extraHeaders)

    def createTicket(self, read=True, write=False, extraHeaders=None, **kwargs):
        """
        Creates a ticket for the given resource on the server.
        
        @param read: Whether to allow reads
        @type read: bool

        @param write: Whether to allow writes
        @type write: bool
        
        @param extraHeaders: Any extra HTTP headers to be sent
            with the MKTICKET C{Request}
        @type extraHeaders: dict
        
        @return: A C{Deferred} to the created L{zanshin.ticket.Ticket} object.
        @rtype: C{Deferred}

        Additional keyword arguments will be treated as additional privileges to
        set.
        
        """

        def handleTicketResponse(response):
            if not response.status in (http.OK, http.CREATED):
                raise zanshin.http.HTTPError(
                    status=response.status, message=response.message)
            
            ticketIds = response.headers.getHeader("Ticket")
                
            if not ticketIds:
                raise zanshin.http.HTTPError(message = "Missing Ticket header")
                    
            ticketId = ticketIds[0]
                
            for child in getTicketInfoNodes(response.body):
                try:
                    ticket = Ticket.parse(child)
                    if ticket.ticketId == ticketId:
                        return ticket
                except ValueError:
                    # Strangely formed XML
                    pass
                    
            raise ValueError, \
                "No ticket with id %s found in server's response" % (
                   ticketId)
            
    
        requestTicket = Ticket(read, write, **kwargs)
        
        result = self.__sendXmlRequest('MKTICKET', unicode(requestTicket),
                                       extraHeaders)

        result.addCallback(handleTicketResponse)

        return result

    def deleteTicket(self, ticketOrName, extraHeaders=None):
        """
        Deletes a ticket for the given resource on the server.
        
        @param ticketOrName: The ticket to destroy
        @type ticketOrName: C{str}, C{unicode} or C{zanshin.ticket.Ticket}
        
        @param extraHeaders: Any extra HTTP headers to be sent
            with the DELTICKET C{Request}
        @type extraHeaders: dict
        
        @return: None
        @rtype: C{deferred}
        """
        if isinstance(ticketOrName, Ticket):
            ticketName = ticketOrName.ticketId
        elif isinstance(ticketOrName, str):
            ticketName = ticketOrName
        elif isinstance(ticketOrName, unicode):
            ticketName = ticketOrName.encode('utf-8')
        else:
            raise TypeError, "Unrecognized ticketOrName parameter"
            
        if not ticketName:
            raise ValueError, "Invalid ticket id '%s'" % (ticketName)
        
        if extraHeaders is not None:
            headers = extraHeaders.copy()
        else:
            headers = {}
        headers['Ticket'] = ticketName
        
        request = zanshin.http.Request('DELTICKET', quote(self.path), headers,
                                       None)
        
        result = self._addRequest(request)
        
        def handleDelTicket(response):
            if response.status == http.NO_CONTENT:
                return None
            
            # An unexpected response, raise the appropriate
            # error
            raise zanshin.http.HTTPError(
                    status=response.status, message=response.message)

        
        result.addCallback(handleDelTicket)
        
        return result
        
    def getTickets(self):
        """
        Fetches the tickets for the given resource on the server.
        
        @return: (Deferred) The (possibly empty) C{list} of
                 L{zanshin.ticket.Ticket} objects.
        @rtype: C{deferred}
        """

        def handlePropfind(response):
            if response.status != http.MULTI_STATUS:
                raise zanshin.http.HTTPError(
                    status=response.status, message=response.message)
            
            tickets = []
            
            for child in getTicketInfoNodes(response.body):
                try:
                    ticket = Ticket.parse(child)
                    if ticket is not None:
                        tickets.append(ticket)
                except ValueError:
                    # Strangely formed XML
                    pass

            return tickets
            

        props = [zanshin.util.PackElement("ticketdiscovery", Ticket.TICKET_NAMESPACE)]
        request = PropfindRequest(quote(self.path), 0, props, {})
        
        result = self._addRequest(request)

        result.addCallback(handlePropfind)

        return result



class ServerHandle(object):
    """
    @ivar resourceFactory: The class of resource to return when asked by
        C{getResource}
    @type resourceFactory: C{class}
    
    @ivar resourcesByPath: The ServerHandle's cache of L{Resource} objects.
    @type resourcesByPath: C{dict}
    """
    
    resourceFactory = Resource
    clientFactory = zanshin.http.HTTPClientFactory

    def __init__(self,
                 host="localhost",
                 port=80,
                 username=None,
                 password=None,
                 useSSL=False,
                 retries=DEFAULT_RETRIES):
        
        self.resourcesByPath = {}   # Caches resources indexed by path

        self.factory = self.clientFactory()
        self.factory.protocol = WebDAVProtocol
        self.factory.host = host
        self.factory.port = port
        self.factory.startTLS = useSSL
        self.factory.username = username
        self.factory.password = password
        self.factory.retries = retries
        
        if useSSL:
            
            contextFactory = None
            
            try:
                from twisted.internet import ssl
            except ImportError:
                ssl = None
                
            if ssl is not None and ssl.supported:
                contextFactory = ssl.ClientContextFactory()
            
            if contextFactory is not None:
                self.factory.sslContextFactory = contextFactory
            else:
                try:
                    import M2Crypto.SSL.TwistedProtocolWrapper as m2wrapper
                except ImportError:
                    m2wrapper = None
                
                if m2wrapper is not None:
                    self.factory.m2wrapper = m2wrapper
                    
                    class ContextFactory:
                        isClient = 1
                        method = 'sslv3'
                        
                        def getContext(self):
                            import M2Crypto.SSL.Context as Context
                            return Context(self.method)
                            
                    self.factory.sslContextFactory = ContextFactory()
                else:
                    # @@@ [grant] Some intelligible message here
                    raise
                
            

        
        #self.factory.extraHeaders = { 'Connection' : "close" }
        self.factory.logLevel = zanshin.http.logging.INFO
        
    def ping(self):
        return self.options().addCallback(lambda options: options is not None)
        
    def getResource(self, url):
        lookupPath = urlparse.urlparse(url)[2]
        
        resource = self.resourcesByPath.get(lookupPath, None)
        
        if resource is None:
            resource = self.resourceFactory(self, lookupPath)
            self.resourcesByPath[lookupPath] = resource
        
        return resource
        
    def addRequest(self, request):
        """
        Basic method for dispatching and reading a C{Request} to the
        server. You can override this to implement performance monitoring,
        or customize error handling, for example.
        
        @param request: The request to send to the server
        @type request: L{zanshin.http.Request}
        
        @return: (Deferred) The server's L{zanshin.http.Response} to C{request}
        @rtype: C{deferred}
        """
        
        self.factory.addRequest(request)
        
        return request.deferred

    def options(self, path='*', extraHeaders=None):
        return self.addRequest(zanshin.http.Request('OPTIONS', path,
                                                    extraHeaders, None))
        
    def get(self, path, extraHeaders=None):
        return self.addRequest(zanshin.http.Request('GET', path, extraHeaders,
                                                    None))
                                                    
    def _putRequest(self, path, body, contentType, contentEncoding,
                    extraHeaders):

        if not contentType:
            contentType, contentEncoding = mimetypes.guess_type(path)

        if contentType:
            extraHeaders['Content-Type'] = contentType

        if contentEncoding:
            extraHeaders['Content-Encoding'] = contentEncoding
            
        return zanshin.http.Request('PUT', path, extraHeaders, body)

    def put(self, path, body, contentType=None, contentEncoding=None,
     extraHeaders=None):
        if extraHeaders:
            extraHeaders = extraHeaders.copy()
        else:
            extraHeaders = {}

        return self.addRequest(self._putRequest(path, body, contentType,
                                                contentEncoding, extraHeaders))
    
    def head(self, path, extraHeaders=None):
        return self.addRequest(zanshin.http.Request('HEAD', path, extraHeaders,
                                                    None))
        

    def mkcol(self, path, extraHeaders=None):
        return self.addRequest(zanshin.http.Request('MKCOL', path, extraHeaders,
                                                    None))
        
    def delete(self, path, extraHeaders=None):
        return self.addRequest(zanshin.http.Request('DELETE', path,
                                                    extraHeaders, None))

    def __str__(self):
        return "ServerHandle instance for host %s:%s, username=%s" % \
            (self.factory.host, self.factory.port, self.factory.username)
            

WebDAVError = zanshin.http.HTTPError
ConnectionError = zanshin.error.ConnectionError

class PermissionsError(zanshin.http.HTTPError):
    """
    Error raised when an HTTP request unexpectedly returns
    a "401 Unauthorized" response.
    """
    def __init__(self, username, message = None):
        if message is None:
            message = ""
        message += "(username = %s)" % username
        zanshin.http.HTTPError.__init__(self,
                    status=http.UNAUTHORIZED, message=message)
        
class WebDAVProtocol(zanshin.http.HTTPClient):
    """
    Subclass of L{zanshin.http.HTTPClient} that deals with
    redirects to the same host.
    
    @todo: Needs unit tests.
    """

    def handleStatus_301(self):
        locationValues = self.response.headers.getHeader("Location")
        
        if locationValues:
            location = locationValues[-1]
            
            useSSL, username, password, host, port, path = \
                zanshin.util.parseConfigFromUrl(location)
                
            if ( (not host and not port)
               or (self.factory.host == host and \
                   self.factory.port == port and \
                   getattr(self.factory, 'startTLS', False) == useSSL) ):
               
                factory = self.factory
                
            else: # Should raise an illegal redirect here
                if not username:
                    username = None
                if not password:
                    password = None
                factory = ServerHandle(host=host, port=port, username=username,
                 password=password, useSSL=useSSL).factory
            
            # OK, make a new request, matching the previous one
            # in everything but path
            newRequest = zanshin.http.Request(self.request.method, path,
                                              self.request.extraHeaders,
                                              self.request.body)
                                              
            # ... queue it ...
            factory.addRequest(newRequest)
            
            # ... make sure it will fire our current request's callbacks
            newRequest.deferred.chainDeferred(self.request.deferred)
            
            # ... and remove our current request's deferred, so that
            # it won't fire before newRequest is handled
            self.request.deferred = None

    # Needed for tomcat/slide?
    handleStatus_302 = handleStatus_301
