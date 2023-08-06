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
    Bare-bones HTTP/1.1 client support for zanshin. Should probably be
    replaced by C{twisted.web2.client} once that has been designed and
    implemented.
    
    HTTP Client State:
    ==================
    
    The following constants track the state of L{HTTPClient} instances:
    
    @var INITIALIZED: Instance initialized, not yet connected to the server.
    @type INITIALIZED: C{int}
    @var CONNECTED: Connected to server; request data not yet written.
    @type CONNECTED: C{int}
    @var WAITING: Request data written, waiting for the server's response (status line).
    @type WAITING: C{int}
    @var READING_HEADERS: Status line has been received, HTTP headers are being read.
    @type READING_HEADERS: C{int}
    @var READING_BODY: End of HTTP headers has been encountered, reading the request body.
    @type READING_BODY: C{int}
    @var DISCONNECTED: No longer connected to the server.
    @type DISCONNECTED: C{int}


    """


from twisted.web import http
from twisted.protocols import basic, policies
from twisted.internet import defer, protocol, reactor, base
from twisted.python.failure import Failure
from twisted.internet.error import TimeoutError
from twisted.python import log

import urlparse

import zanshin.error as error

import base64
import re
import logging

def _getSchemeAndNetloc(host, port, useSSL):
    if useSSL:
        scheme = 'https'
        defaultPort = 443
    else:
        scheme = 'http'
        defaultPort = 80
            
    if port != defaultPort:
        netloc = '%s:%d' % (host, port)
    else:
        netloc = host
        
    return scheme, netloc

                


class ETag(object):
    """
    This is a lame-o substitute for twisted.web2.http_headers.ETag until
    the latter is released (or we change Chandler builds to include
    twisted.web2)
    """
    @classmethod
    def parse(cls, value):
        if not value:
            return None
    
        value = value.strip()
        
        etag = cls()
        
        etag.weak = (value[:2] == "W/")
        
        if etag.weak:
            etag.tag = value[2:]
        else:
            etag.tag = value
            
        return etag
            
    def __init__(self):
        super(ETag, self).__init__()
        self.tag = None
        self.weak = False
    
class Headers(object):
    """
    This is a lame-o substitute for twisted.web2.http_headers until
    the latter is released (or we change Chandler builds to include
    twisted.web2)
    """
    
    # For parsing comma-separated header values
    _SPLITTER = re.compile(',\s*')
    
    def __init__(self):
        super(Headers, self).__init__()
        self._headers = {}
        
    def addRawHeader(self, key, value):
        key = key.lower()
        value = unicode(value).encode('utf-8')
        rawValues = [value] + self._headers.get(key, [])
        self._headers[key] = rawValues
        
    def hasHeader(self, key):
        return self._headers.has_key(key.lower())
        
    def getRawHeaders(self, key):
        return self._headers.get(key.lower(), None)
    
    def getHeader(self, key):
        key = key.lower()
        result = None
        
        rawValues = self._headers.get(key, None)
        result = rawValues
        
        if rawValues is not None:
            if key in ['allow', 'dav', 'transfer-encoding']:
                result = []
                for value in rawValues:
                    result.extend(self._SPLITTER.split(value))
            elif key in ['connection', 'content-length']:
                result = rawValues[-1]
            elif key == 'etag':
                result = ETag.parse(rawValues[-1])
                     
        return result
        
        
    def getAllRawHeaders(self):
        return self._headers.iteritems()
        
class Response(object):
    """
    C{Response} objects encapsulate a server response to a single
    http request.
    
        @type status: C{int}
        @ivar status: The HTTP status code returned by the server.
        
        @type version: C{str}
        @ivar version: The version the server reported in the status line
        
        @type message: C{str}
        @ivar message: The message the server reported in the status line
        
        @type headers: C{Headers}
        @ivar headers: The headers sent back from the server

        @type body: C{str}
        @ivar body: The content of the HTTP response 
    """
    
    def __init__(self, status, version, message):
        self.status = status
        self.version = version
        self.message = message
        
        self.headers = Headers()
        
        self.body = None
    

INITIALIZED      = 0
CONNECTED        = 1
WAITING          = 2
READING_HEADERS  = 3
READING_BODY     = 4
DISCONNECTED     = -1

class Request(object):
    """
    Encapsulates a single HTTP request.
    
    @type method: C{str}
    @ivar method: The HTTP method (PUT, GET, OPTIONS, etc)
    
    @type path: C{str}
    @ivar path: The path part of the URL we want to fetch.
    
    @type extraHeaders: C{dict}
    @ivar extraHeaders: Additional headers you want sent as part of the
        http request. String values are sent as-is, but if you pass in
        a non-string iterable value (e.g. C{tuple} or C{list}), multiple
        headers will be sent.

    @type body: C{str}
    @ivar body: The data associated with this request. This value can be None.
    
    @type deferred: C{deferred}
    @ivar deferred: The C{deferred} that will fire when this
                    request is done. Its result will be a
                    L{Response<zanshin.http.Response>}
    @ivar response: The C{Response} to this request. This only
        becomes non-C{None} once the status line comes back from the
        server.
    @type response: L{Response<zanshin.http.Response>}

    @ivar timeout: The timeout value, in seconds for this request from
        the time it is enqueued.
    @type timeout: C{int} or C{float}
    
    @ivar responseClass: The class to use when creating responses to this
        request. 
    @type responseClass: C{class}
    """
    timeout = 30
    responseClass = Response
    
    def __init__(self, method, path, extraHeaders, body):

        self.method = method
        self.path = path
        self.extraHeaders = extraHeaders
        self.body = body
        self.retries = None

        if isinstance(self.body, unicode):
            # @@@ [grant] Need to change charset for text/ types
            self.body = self.body.encode('utf-8')
        
        self.deferred = defer.Deferred()
        
        # This little trick prevents our deferred from firing
        # twice in the case of, say, a user cancellation or
        # a timeout
        def clearDeferred(self, result):
            self.reset()
            return result

        deferredFn = lambda result: clearDeferred(self, result)
        
        self.deferred.addCallbacks(deferredFn, deferredFn)
        
    def reset(self):
        self.deferred = None
    
    @staticmethod
    def basicAuth(client, username, password, header="Authorization"):
        if username:
            # i.e. if it's not None, or empty
            if password is None:
                password = ""
            
            basicValue = base64.encodestring("%s:%s" % (
                                             username, password)).strip()
            client.sendHeader(header, "Basic %s" % (basicValue,))
        
    def sendAuth(self, client):
        """
        Authorization (only Basic is supported for now).
        L{WebDAVClient<zanshin.http.HTTPClient>}
        overrides this to use WebDAV ticket-based
        authorization where appropriate.
        
        @param client: The client
            instance that's handling our communication with the
            server.
        @type client: L{HTTPClient<zanshin.http.HTTPClient>}
        
        @return: Ignored
        @rtype:
        """
        self.basicAuth(client, client.factory.username, client.factory.password)
        

        
class IDecoder(object):
    """
    This is the interface classes that handle different Transfer-Encoding:
    headers must adopt.
    
    At the moment, there are only 2 such classes:
    C{RawDecoder} (dealing with no Transfer-Encoding: header), and
    C{ChunkedDecoder} (dealing with the 'chunked' TE). These are hard-coded
    inside the HTTPClient class for now, but eventually there could be some
    kind of subclass registration mechanism.
    """

    def start(self, client):
        """
        This is called at the start of streaming any response data.
        
        @param client: The C{HTTPClient} instance this decoder is reading
                       data for.
        @type client: L{HTTPClient}
        @return: Ignored
        @rtype:
        """
        pass
        
    def update(self, client, data):
        """
        This is called in response to data being received by the
        HTTPClient.
        
        @param client: The client instance this decoder is reading
                       data for.
        @type client: L{HTTPClient}
        @param data: The bytes received
        @type data: C{str}
        @return: Ignored
        @rtype:
        """
        pass
        
    def isDone(self, connectionWasClosed):
        """
        This is called by the client, to determine if the decoder is
        done reading data.
        
        @param connectionWasClosed: Indicates that this method was
            called as a result of the connection to the HTTP server
            being closed.
        @type connectionWasClosed: C{boolean}
        
        @return: Return C{True} if your decoder has received all the
            expected data.
        @rtype: C{boolean}
        """
        pass
        


class RawDecoder(IDecoder):
    """
    C{IDecoder} subclass that reads unencoded response data.
    
    @ivar length: The total number of bytes to read, as
                  specified by the C{Content-Length} header.
                  May be C{None} if the HTTP response has no
                  C{Content-Length}.
                  
    @type length: C{int}
    
    @ivar bytesRead: The total number of bytes read so far.
    @type bytesRead: C{int}
    """

    length = None
    bytesRead = 0

    def start(self, client):
        contentLength = client.response.headers.getHeader("Content-Length")
        
        if contentLength is not None:
            try:
                self.length = int(contentLength)
            except ValueError:
                client._protocolError(
                    "Invalid Content-Length, not a number: %s!" %
                      (contentLength))
                return
            
            if contentLength < 0:
                client._protocolError(
                    "Invalid Content-Length, cannot be negative: %s!" %
                        (contentLength))
                return

        client.setRawMode()

    def update(self, client, data):
        datalen = len(data)
        
        if self.length is None or datalen + self.bytesRead < self.length:
            responsePart = data
            extraBytes = None
        else:
            responsePart = data[:self.length - self.bytesRead]
            extraBytes = data[self.length - self.bytesRead:]
            
        self.bytesRead += len(responsePart)
        client.handleResponsePart(responsePart)
        
        if extraBytes is not None:
            client.setLineMode(extraBytes)
        
    def isDone(self, connectionWasClosed):
        if connectionWasClosed:
            return self.length is None or self.bytesRead == self.length
        else:
            return self.length is not None and self.bytesRead == self.length
        

class ChunkedDecoder(IDecoder):
    remainingChunkLength = -1
    wantBlank = False

    def start(self, client):
        pass

    def update(self, client, data):
        if self.wantBlank:
            # Expecting the blank line after a chunk of data
            if len(data) != 0:
                client._protocolError("Blank line expected after chunk")
                return
            client.setLineMode()
            self.wantBlank = False
        elif self.remainingChunkLength < 0:
            # Waiting for a line with the next chunk size

            chunksize = data.split(';', 1)[0]
            try:
                self.remainingChunkLength = int(chunksize, 16)
            except ValueError:
                client._protocolError(
                    "Invalid chunk size, not a hex number: %s!" % (chunksize))
                return

            if self.remainingChunkLength < 0:
                client._protocolError("Invalid chunk size, negative.")
                return
                
            if self.remainingChunkLength > 0:
                client.setRawMode()
            else:
                self.wantBlank = True
            
        else:
            datalen = len(data)
            
            if datalen < self.remainingChunkLength:
                self.remainingChunkLength -= datalen
                client.handleResponsePart(data)
                extraData = ""
            else:
                client.handleResponsePart(data[:self.remainingChunkLength])
                extraData = data[self.remainingChunkLength:]
                self.remainingChunkLength = -1

                self.wantBlank = True
                client.setLineMode(extraData)
    
    def isDone(self, connectionWasClosed):
        return self.remainingChunkLength == 0 and not self.wantBlank


class HTTPClient(basic.LineReceiver, policies.TimeoutMixin):
    """
    HTTP/1.1 twisted client implementation.
    
    @note: To customize the handling of particular HTTP response codes, you
           can implement the method C{handleStatus_nnn()}, where C{nnn}
           is the response code. For example, 
           L{WebDAVProtocol<zanshin.webdav.WebDAVProtocol>} does this
           to perform redirects.
    
    @ivar request: The C{Request} object currently being
        handled by this client. None until we receive
        the connectionMade() or connectionLost() callbacks.
    @type request: L{Request<zanshin.http.Request>}

    @ivar response: The C{Response} object corresponding to
        self.request. C{None} until we receive the status line
        back from the server.
    @type response: L{Response<zanshin.http.Response>}
    
    @ivar state: The state of this client. One of the module constants
          C{INITIALIZED}, C{CONNECTED}, C{WAITING}, C{READING_HEADERS},
          C{READING_BODY} or C{DISCONNECTED}.
    @type state: C{int}
    
    @ivar factory: This client's factory.
    @type factory: L{HTTPClientFactory<zanshin.http.HTTPClientFactory>}
    
    @ivar partialHeader: While parsing HTTP headers that extend over multiple
        lines, this stores the most recent (and possibly incomplete) header
        line.
    @type partialHeader: C{str}

    """

    request = None
    response = None
    state    = INITIALIZED
    factory = None
    partialHeader = None
    
    __writeBuffer = None
    _numProcessed = 0
    _decoder = None
    __timeoutSeconds = None

    def setTimeout(self, timeout):
        if timeout is not None or self.__timeoutSeconds is not None:
            self.__timeoutSeconds = timeout
            policies.TimeoutMixin.setTimeout(self, timeout)
    
    def sendRequest(self, request):
        """
        Sends the HTTP data corresponding to C{request} to the server.
        Stores C{request} in the C{self}'s
        L{request<zanshin.http.HTTPClient.request>}
        instance variable while it's being processed.
        
        Once this method finishes, C{self}'s
        L{state<zanshin.http.HTTPClient.state>} will be
        L{WAITING<zanshin.http.WAITING>} until response
        data is received from the server (or an error
        occurs).
        
        @param request: The HTTP request we want to send.
        @type request: L{Request<zanshin.http.Request>}
        
        @return: Ignored
        @rtype:
        
        @note:
        
          - This method calls individual methods like
            L{sendHeader()<zanshin.http.HTTPClient.sendHeader>},
            L{request.sendAuth()<zanshin.http.Request.sendAuth>} and
            L{endHeaders()<zanshin.http.HTTPClient.endHeaders>}.
            However, in order to avoid many C{write} calls, the
            data "written" in these methods is buffered.
          
          - This method will automatically generate the
            C{Content-Length} and C{Host} HTTP headers if
            needed.
        """

        self.__writeBuffer = ""

        self.request = request

        # Now, send the data. Start with the method...
        command = self.factory.makeCommand(request.method, request.path)      
        self.factory._doLog(logging.INFO, "[Sent] %s", command)
        self.__writeBuffer = "%s\r\n" % (command,)
        
        # Automatically generated headers:
        #
        # Host...
        self.sendHeader("Host", self.factory.getNetLocation())

        # Authorization ...
        self.factory.sendAuthorization(self, request)

        # Content-Length    
        if self.request.body:
            contentLength = str(len(self.request.body))
        else:
            contentLength = "0"
        self.sendHeader("Content-Length", contentLength)
        
        # Send custom headers, if any
        def sendCustomHeader(key, value):
            if isinstance(value, basestring):
                self.sendHeader(key, value)
            else:
                try:
                    iterValue = iter(value)
                except TypeError:
                    self.sendHeader(key, value)
                else:
                    for subValue in iterValue:
                        self.sendHeader(key, subValue)

        if request.extraHeaders is not None:
            for (key, value) in self.request.extraHeaders.iteritems():
                sendCustomHeader(key, value)
            
        for (key, value) in self.factory.extraHeaders.iteritems():
            sendCustomHeader(key, value)
        
        self.endHeaders()
        
        # Lastly, if there's a body, send that.
        if self.request.body:
            self.factory._doLog(logging.INFO, "[Sent] body (%d byte(s))",
                                len(self.request.body))

            self.transport.write(self.request.body)
            
    def _dealWithFailure(self, failure):
        #
        # Depending on timing, some servers may close the connection
        # while we're busy sending the next request. In this case,
        # we don't want to ding the current request's retry count.
        #
        lastRequestClosed = (self.state > INITIALIZED and \
           self.state <= WAITING and \
           self._numProcessed > 0)
        
        self.setTimeout(None)

        haveRequest = self.request is not None
           
        if haveRequest and not lastRequestClosed:
            self.request.retries -= 1
       
        if haveRequest and lastRequestClosed and self.request.retries > 0:
            # Put this request back in the front of the queue
            self.factory.waitingRequests[:0] = [self.request]
        else:
            # OK, buddy, you're outta here!
            if haveRequest and self.request.deferred is not None:
                # @@@ [grant] What about IncompleteResponse()?
                self.request.deferred.errback(failure)
    
    def _protocolError(self, msg):
        self._dealWithFailure(Failure(exc_value=ProtocolError(msg)))
        self.transport.loseConnection()
        
    def timeoutConnection(self):
        self._dealWithFailure(Failure(exc_value=TimeoutError()))
        policies.TimeoutMixin.timeoutConnection(self)

    def connectionLost(self, reason=None):
        self.setTimeout(None)
        self.factory._doLog(logging.INFO, "[Disconnected] %s", reason)

        # Were we still dealing with a request? If so,
        # we need to figure out whether or not we processed
        # a complete response or not.

        requestCompleted = False

        if self.request is not None:
            
            requestCompleted = self.response is not None and \
                               self._decoder is not None and \
                               self._decoder.isDone(True)

            # The server closed the connection, but we have 
            # a request still being processed.
            if not requestCompleted:
                self._dealWithFailure(reason)

        # Set our state to disconnected
        self.state = DISCONNECTED
        
        if requestCompleted:
            self._endResponse()


    def connectionMade(self):
        self.factory._doLog(logging.INFO, "[Connected]")

        self.state = CONNECTED
        self._decoder = None

        if self.request is None:
            # No pending requests, so disconnect
            self.state = DISCONNECTED
            self.transport.loseConnection()
        else:
            self.sendRequest(self.request)


    def sendHeader(self, key, value):
        """
        Sends a single header to the server.
        
        @param key: The header key, whose C{str()} value will be sent.
        @type key: C{object}
        
        @param value:
        @type value: Any
        
        @return: None
        @rtype:
        """
        
        if (self.factory.logLevel > logging.DEBUG and 
            (key.lower() in ("ticket", "authorization"))):
            logValue = len(value) * '*'
        else:
            logValue = value
        self.factory._doLog(logging.INFO, "[Sent] %s: %s", key, logValue)
        
        key = str(key)     # Must be ASCII
        value = str(value) # ?
        self.__writeBuffer += '%s: %s\r\n' % (key, value)

    def endHeaders(self):
        self.factory._doLog(logging.INFO, "[Sent]")
        
        self.__writeBuffer += '\r\n'
        self.transport.write(self.__writeBuffer)

        self.state = WAITING
        self.__writeBuffer = None

    def handleStatus(self, version, status, message):
        """
        Subclass hook; called when the HTTP server returns a status line to a
        request.
        
        @param version: The HTTP version in the status line (e.g. "HTTP/1.1")
        @type version: C{str}
        
        @param status: The HTTP status code of the response (e.g. 200)
        @type status: C{int}
        
        @param message: The message of the response (strictly speaking,
            this is what the HTTP 1.1 spec calls "Reason-Phrase")
        @type message: C{str}
        
        @return: Ignored
        @rtype:
        """
        pass
    
    def handleHeader(self, key, value):
        """
        Subclass hook; called after parsing each full header received from
        the HTTP server.
        
        @param key: The HTTP header key
        @type key: C{str}
        
        @param value: The HTTP header's value
        @type value: C{str}
        
        @return: Ignored
        @rtype:
        """
        pass
        
    def handleResponseEnd(self):
        """
        Subclass hook; called after each response has been completely
        received and parsed.
        
        @return: Ignored
        @rtype:
        """
        
    def handleEndHeaders(self):
        """
        Called after each response's headers have been completely
        read, but before the response body gets read (where needed).
        The HTTPClient implementation will call
        C{self.handleStatus_nnn()}, where C{nnn} is the HTTP
        response code.
        
        @todo: Possibly this should be called elsewhere
        (e.g., in L{handleResponseEnd}).
        
        @return: Ignored
        @rtype:
        """
        
        method = getattr(self, 'handleStatus_'+ str(self.response.status), None)
        if method is not None:
            method()
        
    def handleResponsePart(self, data):
        """
        Called each time a piece of the HTTP response's
        message-body is received from the server. The C{HTTPClient}
        implementation appends the data to its C{response}'s
        L{body<zanshin.http.Response.body>}.
        
        @param data: The transfer-decoded piece of data received.
        @type data: C{str}
        
        @return: Ignored
        @rtype:
        """
        self.factory._doLog(logging.INFO, "[Received Bytes] (%d byte(s))",
                            len(data))
        
        self.response.body += data
    
    def _handleResponseData(self, data):
        isDone = False
        
        if self._decoder is not None:
            isDone = self._decoder.isDone(False)
            if isDone:
                if data:
                    self.factory._doLog(logging.WARNING,
                        "Discarding %d extra byte(s) at the end of response",
                        len(data))
            else:
                self._decoder.update(self, data)
                if self._decoder is not None:
                    isDone = self._decoder.isDone(False)
            
        if isDone: 
            self._endResponse()

    
    def _headerReceived(self, line):
        self.factory._doLog(logging.INFO, "[Received] %s", line)

        keyValueTuple = line.split(':', 1)
        
        if len(keyValueTuple) != 2:
            self._protocolError("Invalid header line '%s'" % line)
            return
        key, value = keyValueTuple
        value = value.lstrip(' \t')

        self.response.headers.addRawHeader(key, value)
        self.handleHeader(key, value)
        
    def _endHeaders(self):
        # Make sure we process the last header
        if self.partialHeader:
            self._headerReceived(self.partialHeader)
        self.partialHeader = ''
        
        self.resetTimeout()
        self.state = READING_BODY
        self.response.body = ""
        self.handleEndHeaders()
        
        if self.response is not None and self.request is not None:
            if self.response.status in http.NO_BODY_CODES or \
               self.request.method == 'HEAD':
               
                self._decoder = None
                # We will fall through to the self._decoder is None
                # case below
                
            else:
                encoding = self.response.headers.getHeader('Transfer-Encoding')
                
                # Set up a chunked Transfer-Encoding reader if necessary
                if encoding and encoding[-1] == "chunked":
                    self._decoder = ChunkedDecoder()
                else:
                    # @@@ [grant] Should fail if it's an unknown T-E
                    self._decoder = RawDecoder()
    
                self._decoder.start(self)
                    
            if self._decoder is None or self._decoder.isDone(False):
                self._decoder = None
                self._endResponse()
        
    def _endResponse(self):
        # @@@ [grant]: Need to make sure the following work:
        #
        #    (1) No Content-Length or Transfer-Encoding, server just closes
        #        the connection when done.
        #
        #    (2) Content-Length: 0
        #
        #    (3) Transfer-Encoding: chunked (no trailers)
        #    
        #    (4) Transfer-Encoding: chunked (with trailers)

        # Log the body of error responses, for debugging porpoises
        try:
            status = self.response.status
            body = self.response.body
        except AttributeError:
            self.factory._doLog(logging.INFO, "[End Response]")
        else:
            if status >= 400:
                self.factory._doLog(logging.WARNING,
                        "[End %d Response]:\n%s\n%s\n%s\n",
                        status,
                        80 * '<', body, 80 * '>')
            else:
                self.factory._doLog(logging.INFO, "[End Response]")


        if self.state != DISCONNECTED:
            self.state = CONNECTED
        self._decoder = None
        
        self.handleResponseEnd()
        
        connection = None
        
        if self.response is not None:
        # assert(self.connection is not None)
            if self.request is not None:
                if self.request.deferred is not None:
                    self.request.deferred.callback(self.response)
                    
            self._numProcessed += 1
            
            connection = self.response.headers.getHeader("Connection")
        
        # Reset state so we can send the next response
        # as needed.
        self.request = None
        self.response = None
        
        # ... if it's a Connection:close response, obey and close.
        if connection and connection.strip().lower() == "close":
            self.factory._doLog(logging.INFO, "[Closing (server request)]")
            self.transport.loseConnection()
            self.state = DISCONNECTED
        else:
            self.setLineMode()
            self.factory.clientCompleted(self)

    
    def lineReceived(self, line):
        self.resetTimeout()

        lineLen = len(line)
        
        if self.state == WAITING:
        
            statusTuple = line.split(None, 2)
            statusTupleLen = len(statusTuple)

            if statusTupleLen > 3 or statusTupleLen < 2:
                self._protocolError("Invalid status line '%s'" % line)
                return

            version = statusTuple[0]
            try:
                status = int(statusTuple[1])
            except ValueError:
                self._protocolError(
                    "Unrecognized status '%s'" % (statusTuple[1]))
                return
                
            try:
                message = statusTuple[2]
            except IndexError:
                message = ""

            self.factory._doLog(logging.INFO, "[Status] %s %s %s", status,
                                version, message)

            self.handleStatus(version, status, message)
            self.state = READING_HEADERS
            self.partialHeader = ''
            self.response = self.request.responseClass(version=version,
                                                       status=status,
                                                       message=message)
        elif self.state == READING_HEADERS:
            if lineLen == 0:
                # Empty line => End of headers
                self._endHeaders()
            elif line[0] in ' \t':
                self.partialHeader += line
            else:
                if self.partialHeader:
                    self._headerReceived(self.partialHeader)
                self.partialHeader = line
        
        elif self.state == READING_BODY:
            self._handleResponseData(line)
        else:
            self._protocolError(
                "Received line unexpectedly (state %d)" % (self.state))
        

    def rawDataReceived(self, data):
        self.resetTimeout()
        #self.factory_doLog(logging.DEBUG, "<<<data: %d byte(s)>>> %s" % (len(data), data[:20]))
        if self.state == READING_BODY:
            self._handleResponseData(data)

class HTTPClientFactory(protocol.ClientFactory):
    """
    C{HTTPClientFactory} supports maintains a queue of C{Request} objects,
    and handles retries for any given request. In
    U{HTTP/1.1<http://www.ietf.org/rfc/rfc2616.txt>}, it's
    possible to have multiple requests handled on a single connection, so
    HTTPClientFactory instances need to hand off requests
    
    @ivar protocol: The twisted Protocol to use to handle HTTP transactions.
    @type protocol: C{class}
    
    @ivar sslContextFactory: Set this to enable SSL.
    @type sslContextFactory: C{twisted.internet.ssl.ContextFactory}
    
    @ivar extraHeaders: Use this to specify HTTP headers you'd like sent
        with every request processed by this factory. For instance, if you
        set this to C{\{'connection':'close'\}}, you could force one
        request per connection. The semantics are the same as for
        setting C{extraHeaders} on an individual C{Request} object.
    @type extraHeaders: C{dict}
    
    @ivar retries: How many times to retry failed HTTP requests.
    @type retries: C{int}
    
    @ivar host: The hostname of the HTTP server we're connecting to
    @type host: C{str}
    
    @ivar port: The IP port of the HTTP server we're connecting to.
    @type port: C{int}
    
    @ivar logLevel: If set (to one of the constants in the python logging
                    modules), enables detailed logging of HTTP traffic (via
                    C{twisted.python.log}. 
    @type logLevel: C{int}
    
    
    @todo:
        - Pipelining (sending request C{n+1} once the HTTP headers for
          request C{n} have been received).
    """
    protocol = HTTPClient
    logLevel = logging.WARNING
    sslContextFactory = None
    extraHeaders = {}
    retries = 3
    port = None
    host = None
    
    def _doLog(self, level, msgFmt, *args):
        if self.logLevel <= level:
            log.msg(msgFmt % args, logLevel=level)

    # Other ivars: self._active tracks the current Port or Request
    # object.
    
    def buildProtocol(self, addr):
        result = protocol.ClientFactory.buildProtocol(self, addr)
        
        if result is not None and len(self.waitingRequests) > 0:
            result.request = self.waitingRequests.pop(0)
            result.setTimeout(result.request.timeout)
                
        self._active = result
        return result
    
    def clientConnectionFailed(self, connector, failure):
        self._active = None
        
        self._doLog(logging.INFO, "[Connection failed]: %s", failure)

        protocol.ClientFactory.clientConnectionFailed(self, connector, failure)
        
        if len(self.waitingRequests) > 0:
            request = self.waitingRequests.pop(0)
            
            request.retries -= 1
            
            # if we're done retrying, errback this request
            if request.retries <= 0:
                connectionError = error.ConnectionError(
                    failure.getErrorMessage())
                try:
                    errback = request.deferred.errback
                except AttributeError:
                    pass
                else:
                    errback(Failure(exc_value=connectionError))
            else:
                # otherwise, try again by inserting
                # this request back in the queue
                self.waitingRequests[:0] = [request]
                
        
        if self._active is None and len(self.waitingRequests) > 0:
            self._makeConnection(request.timeout)

    def clientConnectionLost(self, connector, failure):
        # In this case, there is a protocol object associated
        # with the request. By calling super, the protocol will
        # either errback the request, or insert it back in our waiting
        # queue.

        # @@@ [grant] Does this invalidate everything?
        if self.protocol is not None and self._connectionIsActive():
            self._active.setTimeout(None)

        self._active = None
        
        protocol.ClientFactory.clientConnectionLost(self, connector, failure)

        if self._active is None and len(self.waitingRequests) > 0:
            self._makeConnection(self.waitingRequests[0].timeout)

    def __init__(self):
        self.waitingRequests = []
        self._active = None
        
    def connect(self, host, port, timeout):
        m2wrapper = getattr(self, "m2wrapper", None)
        
        if m2wrapper is not None:
            result = m2wrapper.connectSSL(host, port, self,
                                               self.sslContextFactory,
                                               timeout=timeout)
        elif self.sslContextFactory is not None:
            result = reactor.connectSSL(host, port, self,
                                        self.sslContextFactory,
                                        timeout=timeout)
        else:
            result = reactor.connectTCP(host, port, self,
                                        timeout=timeout)

        self._active = result
        
        return result

    def _makeConnection(self, timeout):
        self._doLog(logging.INFO, "[Connecting to %s:%s]", self.host, self.port)
        return self.connect(self.host, self.port, timeout)

    def addRequest(self, request):
        """
        Adds the given request to our queue of waiting requests, and
        returns a C{deferred} to a C{Reponse} object that will fire when
        the C{Response} is ready.
        
        @param request: The request to queue.
        @type request: L{Request<zanshin.http.Request>}
        
        @return: (Deferred) L{Response<zanshin.http.Response>}
        @rtype: C{deferred}
        """
        if request.retries is None:
            request.retries = self.retries
            
        if request.deferred is None:
            request.deferred = defer.Deferred()
            
        if len(self.waitingRequests) == 0:
            self.waitingRequests = [request]
        else:
            self.waitingRequests.append(request)

        if self._active is None:
            self._makeConnection(self.waitingRequests[0].timeout)
        elif self._connectionIsActive():
            self._doLog(logging.INFO, "[Deferring request %s]", request.method)
        elif self._active.request is None:
            self._active.sendRequest(self.waitingRequests.pop(0))
        
        return request.deferred
        
    def _connectionIsActive(self):
        return base.IConnector.providedBy(self._active)

    def makeCommand(self, command, path):
        command = str(command)
        path = path.encode('utf-8') # URL escape? ascii?

        # Override HTTPClient by making sure the version is 1.1
        return '%s %s HTTP/1.1' % (command, path)
        
    def getNetLocation(self):
        return _getSchemeAndNetloc(self.host, self.port,
                                   self.sslContextFactory is not None)[1]
        

    def sendAuthorization(self, client, request):
        request.sendAuth(client)

    def clientCompleted(self, client):
        if len(self.waitingRequests) > 0 and client.state == CONNECTED:
            client.sendRequest(self.waitingRequests.pop(0))
        elif client.state != DISCONNECTED:
            pass
        elif len(self.waitingRequests) > 0 and self._active is None:
            self._makeConnection(self.waitingRequests[0].timeout)
            
    def stopFactory(self):
        """
        Call this to removing any pending requests, and terminate any
        any disconnected instances.
        
        @return: (Deferred) that fires when we're done disconnecting.
        @rtype: C{deferred}
        
        @note: For HTTP/1.1 servers, it might be nice if we sent a request
            with a 'Connection: close' header, so that they didn't have
            to rely on TCP keep-alives to disconnect.
        """
        if len(self.waitingRequests) > 0:
            self.waitingRequests = []
            
            # @@@ [grant] Should be more specific
        #    map(lambda r: r.errback(Failure()), requests)
        
        if self._connectionIsActive():
            port = self._active
            self._active = None
            return defer.maybeDeferred(port.disconnect)
        elif self._active is not None:
            client = self._active
            self._active = None
            return defer.maybeDeferred(client.transport.loseConnection)

class HTTPProxyClientFactory(HTTPClientFactory):
    """
    C{HTTPClientFactory} that deals with HTTP/1.1 proxies. To use,
    instantiate with the proxy server's host, port, etc (see documentation
    for __init__). Set instance variables host, port to specify the "real"
    host, i.e. the one you want the proxy to contact, and submit requests
    as usual via C{addRequest}.
    """
    
    DEFAULT_OPTS = {
        'host' : None,
        'port' : 80,
        'username' : None,
        'password' : None
    }
    
    def __init__(self, **kw):
        """
        Pass in proxy settings as keyword arguments. Currently supported keys:
        
        host: the hostname of the proxy server
        port: the port of the proxy server (default 80)
        username/password: username and password to use to authenticate on
        the server (default None).
        """
        HTTPClientFactory.__init__(self)
        self.proxySettings = dict(self.DEFAULT_OPTS)
        self.proxySettings.update(kw)
        
    def _makeConnection(self, timeout):
        return self.connect(self.proxySettings['host'],
                            self.proxySettings['port'], timeout)

    def makeCommand(self, command, path):
        url = path
        if url.startswith('/'):
            scheme, netloc = _getSchemeAndNetloc(self.host, self.port,
                                             self.sslContextFactory is not None)
            url = urlparse.urlunparse((scheme, netloc, url, '', '', ''))

        return HTTPClientFactory.makeCommand(self, command, url)

    def sendAuthorization(self, client, request):
        HTTPClientFactory.sendAuthorization(self, client, request)
        request.basicAuth(client, self.proxySettings['username'],
                          self.proxySettings['password'], "Proxy-Authorization")



class HTTPError(error.Error):
    """
    An error associated with an HTTP response.
    
    @ivar status: The HTTP response's status code
    @type status: C{int}
    
    @ivar message: The error's message (the HTTP 1.1 "Reason-Phrase")
    @type message: C{str}
    """
    
    def __init__(self, status=None, message=None):
        error.Error.__init__(self)
        self.status = status
        self.message = message
        
    def __str__(self):
        result = "<" + str(self.__class__)
        
        if self.status is not None:
            result += " (%d)" % self.status
        if self.message is not None:
            result += " " + self.message
        result += ">"
        
        return result
        
ConnectionError = error.ConnectionError


class IncompleteResponse(error.Error):
    def __init__(self, response):
        super(self, IncompleteResponse).__init__()
        
        self.response = response
        
class ProtocolError(error.Error):
    """
    An error indicating that data was received from the server
    that did not conform to the HTTP/1.1 protocol. Examples might
    be: invalid HTTP header lines (e.g. missing ':' after the key),
    or an unparseable status line.
    """
    pass
