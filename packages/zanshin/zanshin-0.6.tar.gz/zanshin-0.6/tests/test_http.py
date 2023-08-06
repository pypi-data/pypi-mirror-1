# Copyright (c) 2005 Open Source Applications Foundation.
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
# http test classes

from twisted.internet import defer, protocol, reactor
from twisted.protocols import basic
from twisted.python.failure import Failure

from twisted.trial import unittest

import twisted.internet.error as error 

"""from twisted.internet.base import DelayedCall
DelayedCall.debug = True"""

from zanshin.http import (HTTPClientFactory, HTTPProxyClientFactory,
                          ProtocolError, Request, Response)

class TestHTTPServerFactory(protocol.ServerFactory):

    statusLine = ""
    headerLines = []
    bodyParts = []
    keepAlive = False

    _activeProtocols = None

    def buildProtocol(self, addr):
        result = protocol.ServerFactory.buildProtocol(self, addr)
        if self._activeProtocols is None: self._activeProtocols = set([])
        self._activeProtocols.add(result)
        return result

    def stopFactory(self):
        result = protocol.ServerFactory.stopFactory(self)
        activeProtocols = self._activeProtocols
        
        if activeProtocols is not None:
            for x in activeProtocols:
                transport = x.transport
                if transport is not None:
                    transport.loseConnection()

        return result

class TestHTTPServerProtocol(basic.LineReceiver):

    def lineReceived(self, line):
    
        if line == "":
    
            response = ""
            response += self.factory.statusLine + '\r\n'
            
            if self.factory.headerLines:
                response += '\r\n'.join(self.factory.headerLines)
                response += '\r\n' # For the last header
            
            response += '\r\n' # To end the headers
            
            self.transport.write(response)
    
            for part in self.factory.bodyParts:
                self.transport.write(part)
            
            if not self.factory.keepAlive:
                self.transport.loseConnection()


class HTTPTestCase(unittest.TestCase):
    port = 9921
    
    def setUpClient(self):
        clientFactory = HTTPClientFactory()
        clientFactory.port = self.port
        clientFactory.host = "localhost"
        clientFactory.username = None
        clientFactory.password = None
        clientFactory.logging = True
        
        return clientFactory
        
    
    def setUp(self):
        # start the server
        if getattr(self, 'serverFactory', None) is None:
            self.serverFactory = TestHTTPServerFactory()
        self.serverFactory.protocol = self.serverProtocol
        
        self._port = reactor.listenTCP(self.port, self.serverFactory)
        self.clientFactory = self.setUpClient()
        
    def tearDown(self):
        d = defer.maybeDeferred(self._port.stopListening)
        shutdownFn = getattr(self.clientFactory, "stopFactory", None)
        if shutdownFn is not None:
            d.addBoth(lambda _: shutdownFn())
        
        return d

class TimeoutTestCase(HTTPTestCase):
    # Use an unsubclassed Protocol instance, since that
    # does nothing in its connectionMade(). This will
    # cause us to time out while waiting for the server's
    # response.
    serverProtocol = protocol.Protocol
    
    def testTimeout(self):
        req = Request("GET", "/", {}, None)
        req.timeout = 1 # Set a short timeout so the test doesn't take forever.
        d = self.clientFactory.addRequest(req)
        
        self.assertFailure(d, error.TimeoutError)
        
        return d

class ResubmitTestCase(HTTPTestCase):
    serverProtocol = TestHTTPServerProtocol
    
    class FirstTimeErrorClientFactory(HTTPClientFactory):
        addedOne = False
        
        def raiseAnError(self, response):
            raise error.SSLError, "Test exception"
        
        def addRequest(self, request):
            result = HTTPClientFactory.addRequest(self, request)
            
            if not self.addedOne:
                self.addedOne = True
                result.addCallback(self.raiseAnError)
            return result
    
    def testResubmit(self):
        self.serverFactory.statusLine = "HTTP/1.1 200 OK"
        self.serverFactory.bodyParts = ["Hello!"]
        self.serverFactory.headerLines = [
            "Content-Length: %d" % (len(self.serverFactory.bodyParts[0]))]
        self.serverFactory.keepAlive = True
        
        self.clientFactory.__class__ = self.FirstTimeErrorClientFactory

        req = Request("GET", "/", {}, None)
        
        def checkResponse(response):
            self.failUnlessEqual(response.status, 200)
            self.failUnlessEqual(response.body, "Hello!")
            return response
        
        def respondToError(failure):
            self.failUnless(failure.check(error.SSLError))
            
            # ... and resubmit it if necessary
            return self.clientFactory.addRequest(req).addCallback(checkResponse)
        
        # Submit the initial request ....
        return self.clientFactory.addRequest(req).addErrback(respondToError)

class KeepAliveTimeoutTestCase(HTTPTestCase):
    serverProtocol = TestHTTPServerProtocol
    
    def testKeepAlive(self):
        """Test that a connection that's kept alive is correctly
           closed after the timeout expired."""
           
        self.serverFactory.statusLine = "HTTP/1.1 200 OK"
        self.serverFactory.bodyParts = ["Hello!"]
        self.serverFactory.headerLines = [
            "Content-Length: %d" % (len(self.serverFactory.bodyParts[0]))]
        self.serverFactory.keepAlive = True

        req = Request("GET", "/", {}, None)
        req.timeout = 0.1 # Set a short timeout so the test doesn't take forever.
        
        def failIfActive():
            try:
                self.failIf(self.clientFactory._active is not None,
                            "%s is still active" % (self.clientFactory))
                self.__deferred.callback(None)
            except:
                self.__deferred.errback(Failure())
            
        
        def waitForTimeout(result):
            self.__deferred = defer.Deferred()
            reactor.callLater(2.0 * req.timeout, failIfActive)
            return self.__deferred
        
        return self.clientFactory.addRequest(req).addCallback(waitForTimeout)
        

class ReadTimeoutTestCase(HTTPTestCase):
    serverProtocol = TestHTTPServerProtocol
    
    def setUp(self):
        super(ReadTimeoutTestCase, self).setUp()
        self.serverFactory.statusLine = "HTTP/1.1 200 OK"
        self.serverFactory.headerLines = ["Content-Length: 1024"]
        self.serverFactory.bodyParts = ["Lost in translation"]
        self.serverFactory.keepAlive = True
        
    def testTimeout(self):
        req = Request("GET", "/", {}, None)
        req.timeout = 0.15 # Set a short timeout so the test doesn't take forever.
        d = self.clientFactory.addRequest(req)
        
        self.assertFailure(d, error.TimeoutError)
        
        return d

class DisconnectTestCase(HTTPTestCase):

    class DisconnectProtocol(protocol.Protocol):
        def connectionMade(self):
            self.transport.loseConnection()

    serverProtocol = DisconnectProtocol

    def testImmediateDisconnect(self):
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        self.assertFailure(d, error.ConnectionDone, error.ConnectionLost)

        return d


class StatusTestCase(HTTPTestCase):

    class BogusProtocol(protocol.Protocol):
        def connectionMade(self):
            self.transport.write(self.factory.statusLine + '\r\nContent-Length: 0\r\n\r\n')

    serverProtocol = TestHTTPServerProtocol

    def testBlankStatus(self):
        self.serverFactory.statusLine = ""
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        self.assertFailure(d, ProtocolError)
        
        return d

    def testBadStatus1(self):
        self.serverFactory.statusLine = "djkfjakdjsf"
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        self.assertFailure(d, ProtocolError)
        
        return d

    def testBadStatus2(self):
        self.serverFactory.statusLine = "djkfjakdjsf"
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        self.assertFailure(d, ProtocolError)
        
        return d

    def testBadStatus3(self):
        self.serverFactory.statusLine = "HTTP/1.0 notanint"
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        self.assertFailure(d, ProtocolError)
        
        return d


    def testNoMessage(self):
        self.serverFactory.statusLine = "HTTP/1.1 201"
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnless(
                resp.status==201 and
                resp.version=="HTTP/1.1" and
                resp.message==""))
        
        return d
        
    def testNoMessage_trailingSpace(self):
        self.serverFactory.statusLine = "HTTP/1.1 201 "
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnless(
                resp.status==201 and
                resp.version=="HTTP/1.1" and
                resp.message==""))
        
        return d



    def testBaseline(self):
        self.serverFactory.statusLine = "HTTP/1.0 433 I love the number 433"
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnless(
                resp.status==433 and 
                resp.version=="HTTP/1.0" and
                resp.message=="I love the number 433"))
        
        return d

class ResponseTestCase(HTTPTestCase):

    serverProtocol = TestHTTPServerProtocol

    def testNoBody(self):
        self.serverFactory.statusLine = "HTTP/1.1 200"
        self.serverFactory.bodyParts = []
        self.serverFactory.keepAlive = False

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))

        d.addCallback(lambda resp:
            self.failUnless(
                resp.status== 200 and 
                resp.version == "HTTP/1.1" and
                resp.message == "" and
                resp.body == ""))
        return d

    def test_204_response(self):
        self.serverFactory.statusLine = "HTTP/1.1 204 Nothing to see here"
        self.serverFactory.keepAlive = True
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d.addCallback(lambda resp:
            self.failUnless(
                resp.status== 204 and 
                resp.version == "HTTP/1.1" and
                resp.message == "Nothing to see here" and
                resp.body == ""))
                
        return d

    def test_304_response(self):
        self.serverFactory.statusLine = "HTTP/1.1 304 But I have not changed!"
        self.serverFactory.keepAlive = True
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d.addCallback(lambda resp:
            self.failUnless(
                resp.status== 304 and 
                resp.version == "HTTP/1.1" and
                resp.message == "But I have not changed!" and
                resp.body == ""))
        return d

class HeadersTestCase(HTTPTestCase):

    serverProtocol = TestHTTPServerProtocol

    def setUp(self):
        super(HeadersTestCase, self).setUp()
        self.serverFactory.statusLine = "HTTP/1.1 200"
        
    def testNoHeaders(self):
        self.serverFactory.headerLines = []
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))

        d = d.addCallback(lambda resp:
            self.failUnlessEqual(
                [],
                [x for x in resp.headers.getAllRawHeaders()]))
        return d


    def testSimpleHeader(self):
        self.serverFactory.headerLines = [
            "Key: Value"
        ]
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnlessEqual(
                resp.headers.getRawHeaders("key"),
                ["Value"]))
        return d


    def testWeakETagHeader(self):
        self.serverFactory.headerLines = [
            "ETag: W/iamsoweak"
        ]
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnlessEqual(
                resp.headers.getHeader("etag").tag,
                "iamsoweak")
            and
            self.failUnlessEqual(
                resp.headers.getHeader("etag").weak,
                True)
        )
        return d

    def testStrongETagHeader(self):
        self.serverFactory.headerLines = [
            "ETag: mystrengthisstrength"
        ]
        
        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnlessEqual(
                resp.headers.getHeader("etag").tag,
                "mystrengthisstrength")
            and
            self.failUnlessEqual(
                resp.headers.getHeader("etag").weak,
                False)
        )
        return d

    def _checkContinuationHeaders(self, resp):
        self.failUnlessEqual(
            resp.headers.getRawHeaders("Key1"),
            ["Value and then some"])

        self.failUnlessEqual(
            resp.headers.getRawHeaders("Key2"),
            ["Plain Old Value"])

        self.failUnlessEqual(
            len([x for x in resp.headers.getAllRawHeaders()]),
            2)


    def testContinuation(self):
        self.serverFactory.headerLines = [
            "Key1: Value",
            " and then some",
            "Key2: Plain Old Value"
        ]

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))

        d = d.addCallback(self._checkContinuationHeaders)

        return d

class BodyTestCase(HTTPTestCase):
    serverProtocol = TestHTTPServerProtocol
    
    def setUp(self):
        super(BodyTestCase, self).setUp()
        self.serverFactory.statusLine = "HTTP/1.1 200"
        self.serverFactory.headerLines = []


    def testSimpleBody(self):
        body = "Isn't this\nJust grand?"
        
        self.serverFactory.bodyParts = [body]
        self.serverFactory.headerLines = \
            ["Content-Length: %d" % len(body)] + \
            self.serverFactory.headerLines

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnlessEqual(
                resp.body,
                body))

        return d
    
    def testSimpleBodyExtraBytes(self):
        body = "Isn't this\nJust grand?"
        self.serverFactory.bodyParts = [body + "bogus\r\n"]
        self.serverFactory.headerLines = \
            ["Content-Length: %d" % len(body)] + \
            self.serverFactory.headerLines

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnlessEqual(
                resp.body,
                body))

        return d

    def testChunkedBody(self):
        body1 = "Isn't this\nJust grand?"
        body2 = "Isn't this also\nJust grand?"
        
        self.serverFactory.headerLines = \
            ["Transfer-Encoding: chunked"] + \
            self.serverFactory.headerLines

        self.serverFactory.bodyParts = [
            "%x\r\n" % len(body1) +
            body1 +
            "\r\n%x\r\n" % len(body2) +
            body2 +
            "\r\n0\r\n\r\n"
            ]

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnlessEqual(
                resp.body,
                body1 + body2))

        return d

    def testBadlyChunkedBody(self):
        body1 = "Isn't this\nJust grand?"
        
        self.serverFactory.headerLines = \
            ["Transfer-Encoding: chunked"] + \
            self.serverFactory.headerLines

        self.serverFactory.bodyParts = [
            "%x\r\n" % len(body1) +
            body1 +
            "0\r\n\r\n"
            ]

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        self.assertFailure(d, ProtocolError)
        
        return d
        
    def testBadChunkSize(self):
        body1 = "Isn't this\nJust grand?"
        
        self.serverFactory.headerLines = \
            ["Transfer-Encoding: chunked"] + \
            self.serverFactory.headerLines

        self.serverFactory.bodyParts = [
            "oooo%s\r\n" % len(body1) +
            body1 +
            "0\r\n\r\n"
            ]

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        self.assertFailure(d, ProtocolError)
        
        return d

    def testEmptyChunkedBody(self):
        self.serverFactory.headerLines = \
            ["Transfer-Encoding: chunked"] + \
            self.serverFactory.headerLines

        self.serverFactory.bodyParts = [
            "0\r\n\r\n"
            ]

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnlessEqual(resp.body, ""))
        
        return d

    def testStuffAfterChunkSize(self):
        body1 = "Isn't this\nJust grand?"
        
        self.serverFactory.headerLines = \
            ["Transfer-Encoding: chunked"] + \
            self.serverFactory.headerLines

        self.serverFactory.bodyParts = [
            "%x; scooby-dooby-doo\r\n" % len(body1) +
            body1 +
            "\r\n0\r\n\r\n"
            ]

        d = self.clientFactory.addRequest(Request("GET", "/", {}, None))
        
        d = d.addCallback(lambda resp:
            self.failUnlessEqual(
                resp.body,
                body1))

        return d
    
class KeepAliveTestCase(HTTPTestCase):

    class ConnectionCountingFactory(TestHTTPServerFactory):
        numConnections = 0
        numRequests = 0
        bytesToWrite = ""
        
        def buildProtocol(self,addr):
            self.numConnections += 1
            return TestHTTPServerFactory.buildProtocol(self, addr) 
        
    class VerySimpleProtocol(basic.LineReceiver):
        done = False
        
        def lineReceived(self, line):
            if not line:
                self.transport.write(self.factory.bytesToWrite)
                self.factory.numRequests += 1
                
                
    def setUp(self):

        self.serverFactory = self.ConnectionCountingFactory()
        self.serverProtocol = self.VerySimpleProtocol
        return super(KeepAliveTestCase, self).setUp()
    
    def _addRequest(self, *args):
        return self.clientFactory.addRequest(Request("GET", "/", {}, None))

    def testCloseConnection(self):
        body = "Hello\n"
        self.serverFactory.bytesToWrite = "\r\n".join([
            "HTTP/1.1 200 OK",
            "Content-Length: %d" % (len(body)),
            "Connection: close",
            "",
            ""]) + body
        
        d = self._addRequest()
        d = d.addCallback(self._addRequest)
        
        def checkCount(_):
            self.failUnlessEqual(2, self.serverFactory.numConnections)
            self.failUnlessEqual(2, self.serverFactory.numRequests)

        d = d.addCallback(checkCount)
        
        return d


    def testSeparateRequests(self):
        body = "Hello\n"
        self.serverFactory.bytesToWrite = "\r\n".join([
            "HTTP/1.1 200 OK",
            "Content-Length: %d" % (len(body)),
            "",
            ""]) + body
        
        d = self._addRequest()
        d = d.addCallback(self._addRequest)
        
        def checkCount(_):
            self.failUnlessEqual(1, self.serverFactory.numConnections)
            self.failUnlessEqual(2, self.serverFactory.numRequests)
            
        d = d.addCallback(checkCount)
        
        return d
    
    def testKeepConnectionAlive(self):
        body = "Hello\n"
        self.serverFactory.bytesToWrite = "\r\n".join([
            "HTTP/1.1 200 OK",
            "Content-Length: %d" % (len(body)),
            "",
            ""]) + body
        
        def checkCounts(_):
            self.failUnlessEqual(1, self.serverFactory.numConnections)
            self.failUnlessEqual(2, self.serverFactory.numRequests)
            
        d = defer.DeferredList([self._addRequest(), self._addRequest()])
        d = d.addCallback(checkCounts)
        
        return d
        
    def testTimeout(self):
        """Test that a connection that's kept alive doesn't close
        prematurely."""
        
        self.numSent = 0         # How many requests we've sent
        self.numRequests = 3     # The total to send
        self.interval = 0.1      # How long to wait between sends
        self.timeout = 0.15      # The timeout for each request
        
        def fireTimer(response):

            def waitInterval(result):
                # Return a deferred that fires after self.interval seconds
                deferred = defer.Deferred()
                reactor.callLater(self.interval, deferred.callback, result)
                return deferred
        
            if self.numSent < self.numRequests:
                self.numSent += 1
    
                req = Request("GET", "/", {}, None)
                req.timeout = self.timeout
                
                result = self.clientFactory.addRequest(req)
                
                # Once the request is complete, wait for self.interval
                # seconds....
                result.addCallback(waitInterval)
                # ... and once that's done, send another request.
                result.addCallback(fireTimer)
                
                return result
            else:
                # End of the test (all requests sent).
                # Make sure we never had to reconnect
                self.failUnlessEqual(1, self.serverFactory.numConnections)
                # ... and that the server received all requests
                self.failUnlessEqual(self.numRequests,
                                     self.serverFactory.numRequests)
                
                
        body = "Hello\n"
        self.serverFactory.bytesToWrite = "\r\n".join([
            "HTTP/1.1 200 OK",
            "Content-Length: %d" % (len(body)),
            "",
            ""]) + body
        
        
        return fireTimer(None)

class RecordingServerProtocol(TestHTTPServerProtocol):
    linesByInstance = {}
    
    def lineReceived(self, line):
        lines = self.linesByInstance.setdefault(self, [])
        lines.append(line)

        return TestHTTPServerProtocol.lineReceived(self, line)
        

class ProxyTestCase(HTTPTestCase):
    serverProtocol = RecordingServerProtocol
        
    def tearDown(self):
        RecordingServerProtocol.linesByInstance = {}
        HTTPTestCase.tearDown(self)
        
    def setUp(self):
        HTTPTestCase.setUp(self)
        self.serverFactory.statusLine = "HTTP/1.1 200 OK"
        self.serverFactory.bodyParts = ["Hello!"]
        self.serverFactory.headerLines = (
            "Content-Length: %d" % (sum(map(len, self.serverFactory.headerLines))),
        )
        
    def setUpClient(self):
        clientFactory = HTTPProxyClientFactory(host="localhost", port=self.port,
                                               username=None, password=None)
        clientFactory.username = None
        clientFactory.password = None
        clientFactory.logging = True
        
        return clientFactory
        
    def setupProxyToClient(self, **kw):
        for key, value in (
            ('username', None),
            ('password', None)
        ):
            kw.setdefault(key, value)

        for attr, value in kw.iteritems():
            setattr(self.clientFactory, attr, value)
            
    def testProxy(self):

        self.setupProxyToClient(host='chandlerproject.org', port=80)
        req = Request("GET", "/", {}, None)
        
        def checkReq(response):
            self.failUnlessEqual(len(RecordingServerProtocol.linesByInstance), 1)
            lines = RecordingServerProtocol.linesByInstance.values()[0]
            
            self.failUnlessEqual(lines[0],
                                 "GET http://chandlerproject.org/ HTTP/1.1")
            self.failUnless('Host: chandlerproject.org' in lines)

        d = self.clientFactory.addRequest(req).addCallback(checkReq)
        return d
        
    def testFunkyPort(self):
        self.setupProxyToClient(host='example.com', port=8080)
        req = Request("GET", "/index.html", {}, None)

        def checkReq(response):
            self.failUnlessEqual(len(RecordingServerProtocol.linesByInstance), 1)
            lines = RecordingServerProtocol.linesByInstance.values()[0]
            
            self.failUnlessEqual(
                lines[0],
                "GET http://example.com:8080/index.html HTTP/1.1"
            )
            self.failUnless('Host: example.com:8080' in lines)

        d = self.clientFactory.addRequest(req).addCallback(checkReq)
        return d
        
    def testClientAuth(self):
        
        self.setupProxyToClient(host='example.com', port=80, username='wally')
        req = Request("PUT", "/index.html", {}, "")
        
        def checkReq(response):
            self.failUnlessEqual(len(RecordingServerProtocol.linesByInstance), 1)
            lines = RecordingServerProtocol.linesByInstance.values()[0]
            
            self.failUnlessEqual(
                lines[0],
                "PUT http://example.com/index.html HTTP/1.1"
            )
            self.failUnless('Host: example.com' in lines)
            self.failUnless('Authorization: Basic d2FsbHk6' in lines)
        
        d = self.clientFactory.addRequest(req).addCallback(checkReq)
        return d

    def testProxyAuth(self):
        
        self.setupProxyToClient(host='example.com', port=80, username='wally')
        self.clientFactory.proxySettings['username'] = 'fred'
        self.clientFactory.proxySettings['password'] = 'rogers'
        req = Request("PUT", "/index.html", {}, "")
        
        def checkReq(response):
            self.failUnlessEqual(len(RecordingServerProtocol.linesByInstance), 1)
            lines = RecordingServerProtocol.linesByInstance.values()[0]
            
            self.failUnlessEqual(
                lines[0],
                "PUT http://example.com/index.html HTTP/1.1"
            )
            self.failUnless('Host: example.com' in lines)
            self.failUnless('Authorization: Basic d2FsbHk6' in lines)
            self.failUnless('Proxy-Authorization: Basic ZnJlZDpyb2dlcnM='
                            in lines)
        
        d = self.clientFactory.addRequest(req).addCallback(checkReq)
        return d
        
class SendHeadersTestCase(HTTPTestCase):
    """
    Tests passing in lists/tuples, as well as strs, as values to request
    and factory extraHeaders generates the intended HTML (i.e. multiple
    lines with the same header key).
    """
    serverProtocol = RecordingServerProtocol
        
    def tearDown(self):
        RecordingServerProtocol.linesByInstance = {}
        HTTPTestCase.tearDown(self)
        
    def setUp(self):
        HTTPTestCase.setUp(self)
        self.serverFactory.statusLine = "HTTP/1.1 200 OK"
        self.serverFactory.bodyParts = ["Hello!"]
        self.serverFactory.headerLines = (
            "Content-Length: %d" % (sum(map(len, self.serverFactory.headerLines))),
        )

    def runTheTest(self, requestHeaders, *expectedLines):
        req = Request("PUT", "/index.html", requestHeaders, "")

        def checkReq(response):
            self.failUnlessEqual(len(RecordingServerProtocol.linesByInstance), 1)
            recordedLines = RecordingServerProtocol.linesByInstance.values()[0]
            self.failUnlessEqual(recordedLines[0], 'PUT /index.html HTTP/1.1')
            
            for line in expectedLines:
                self.failUnless(line in recordedLines,
                                'Missing line in response: <%s>' % (line,))

        return self.clientFactory.addRequest(req).addCallback(checkReq)

    def testSimple(self):
        return self.runTheTest(dict(Blah='Hello'), 'Blah: Hello')

    def testList(self):
        return self.runTheTest(
                    dict(Blah=['Hello', 3]),
                    'Blah: Hello',
                    'Blah: 3')

    def testInt(self):
        return self.runTheTest(
                    { 'X-My-Special-Header': 42 },
                    'X-My-Special-Header: 42')

    def testNoRecursion(self):
        return self.runTheTest(
                    { 'X-A-Header': (12, ['Hi', 'Mom']) },
                    'X-A-Header: 12',
                    "X-A-Header: ['Hi', 'Mom']" # sic -- not a good idea
                )

    def testMultiple(self):
        return self.runTheTest(
                    {'X-Header-One': ['This', 'is', 'so', 'good'],
                     'X-Header-Two': 'pomegranate',
                     'X-Header-Three': ''},
                     'X-Header-One: This',
                     'X-Header-One: is',
                     'X-Header-One: so',
                     'X-Header-One: good',
                     'X-Header-Two: pomegranate',
                     'X-Header-Three: '
               )

    def testClientFactoryHeaders(self):
        self.clientFactory.extraHeaders = { 'Hey': 'Jude' }
        return self.runTheTest({}, 'Hey: Jude')  


    def testClientFactoryMultiple(self):
        self.clientFactory.extraHeaders = { 'Hey': ['Jude', 'Law'] }
        return self.runTheTest(
            { 'Hey': 'You', 'X-Wassup': 'Nothing' },
            'Hey: Jude',
            'Hey: Law',
            'Hey: You',
            'X-Wassup: Nothing'
        )

