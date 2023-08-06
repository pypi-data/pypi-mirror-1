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
# Zanshin test classes

from twisted.trial import unittest
from twisted.internet.defer import DeferredList, maybeDeferred
import twisted.internet.reactor as reactor
from zanshin.webdav import ServerHandle, PermissionsError
from zanshin.http import Request, HTTPError
from zanshin.util import parseConfigFromUrl, PackElement
import zanshin.webdav_server as webdav_server
from zanshin.ticket import Ticket
from httplib import OK, UNAUTHORIZED
import test_util

import os

# Global initialization

"""
Set up the globals useSSL, port, protocol, username and password by
reading ZANSHIN_TEST_CONFIG from the environment, and parsing out
the various components of that URL. By default, we use http to localhost
on port 8080, with username and password set to "root". This works with
the default configuration of Slide.
"""

DEFAULT_CONFIG_URL = "http://root:root@localhost:8080/slide/files/"
configUrl=os.environ.get("ZANSHIN_TEST_CONFIG", None)

def isDefaultConfig():
    return (configUrl == DEFAULT_CONFIG_URL)

class TestServerResource(webdav_server.WebDAVResource):
    """
    This helper class is a way to customize our internal testing
    webdav server, to add resources that respond in a given way to
    some HTTP request. To use:
    
       - In a subclass of TestServerResource, implement render_METHOD
         to call self.renderFixedValues() (where METHOD is the method
         you want to implement for testing purposes).
       - Instantiate your subclass, set up its headers, responseCode
         and optionally body instance variables, and add it to
         your site's resource tree somewhere.
       - Now you can run your client test against the internal server.
    """
    
    responseCode = 200
    headers = {}
    
    def renderFixedValues(self, request):
        request.setResponseCode(self.responseCode)
        for (header, value) in self.headers.iteritems():
            request.setHeader(header, value)
        return getattr(self, 'body', '')


class WebDAVTestCase(unittest.TestCase):
    localServer = (configUrl is None)

    def setUp(self):
        super(WebDAVTestCase, self).setUp()
        
        if self.localServer:
            self.useSSL = False
            self.username = None
            self.password = None
            self.host = "localhost"
            self.port = 9922
            self.path = "/folder/"
            
            self.siteFactory = webdav_server.getTestSite()
            self.listenPort = reactor.listenTCP(self.port, self.siteFactory)
        else:
            self.useSSL, self.username, self.password, self.host, self.port, \
                self.path = parseConfigFromUrl(configUrl)
            # Our path is a directory, so we always append a / for correct WebDAV
            # semantics
            if self.path[-1:] != "/": self.path += "/"
            self.siteFactory = None
            self.listenPort = None
        
        self.server = ServerHandle(self.host, self.port, self.username,
                                   self.password, self.useSSL)

    def tearDown(self):
        deferred = maybeDeferred(self.server.factory.stopFactory)
        
        if self.listenPort is not None:
            factory = self.listenPort.factory

            deferred.addBoth(lambda _: self.listenPort.stopListening())
            deferred.addBoth(lambda _: factory.stopFactory())
        return deferred 

class TestOptions(WebDAVTestCase):
    """
    The OPTIONS request defaults to the URL *.  If this is a slide
    installation, then the URL * is handled by Tomcat and shows no
    WebDAV support.
    """

    def __expectedOptions(self, server):
        """
        This is a way to test whether or we're correctly receiving
        the response to "OPTIONS *, based on the value of the 'Server'
        header.
        """
        
        if server == "Apache-Coyote/1.1":
            # Slide (default config)
            return ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS']
        elif server == "Apache/2.0.51 (Fedora)":
            # mod_dav (eg pilikia.osafoundation.org)
            return ['OPTIONS', 'MKCOL', 'PUT' , 'LOCK']
        else:
            return None


    def setUp(self):
        super(TestOptions, self).setUp()
        self.serverNoAuth = ServerHandle(self.host, self.port, useSSL=self.useSSL)
        self.serverAuth = self.server
        
    def tearDown(self):
        return DeferredList([
            maybeDeferred(self.serverNoAuth.factory.stopFactory),
            maybeDeferred(super(TestOptions, self).tearDown)])

    def checkResponse(self, response):
        self.failUnless(response.headers.hasHeader("Date"), "Failed to get Date header")
        if response.status == OK:
            optionsHeader = response.headers.getHeader("Allow")
            self.failIf(optionsHeader == None,
                       "Missing 'Accept' header in OPTIONS response")
            server = response.headers.getHeader("Server")
            expectedOptions = self.__expectedOptions(server)
            if expectedOptions != None:
                self.failUnlessEqual(optionsHeader, expectedOptions)
                if isDefaultConfig():
                    self.failIf(response.headers.hasHeader("DAV"))
        
        elif response.status == UNAUTHORIZED:
            authenticateHeader = response.headers.getRawHeaders("WWW-Authenticate")
            self.failIf(authenticateHeader == None,
                       "Missing 'WWW-Authenticate' header in OPTIONS response")

    def test_options_star(self):
        return self.serverNoAuth.options().addCallback(self.checkResponse)

    def test_no_webdav_support(self):
        if isDefaultConfig():
            resource = self.serverAuth.getResource("/")
            return resource.supportsWebDAV().addCallback(self.failIf)
 
    def test_webdav_support(self):
        #Need permissions for this one
        resource = self.serverAuth.getResource(self.path)
        
        # Succeed if resource supports WebDAV...
        d =  resource.supportsWebDAV().addCallback(self.failUnless)
        
        if configUrl != None:
    
            # ... and if that's ok, check the resource supports locking...
            d = d.addCallback(lambda arg: resource.supportsLocking())
            
            # ... and fail if it doesn't
            d = d.addCallback(self.failUnless)
        
        return d

    def test_bad_permissions(self):
    
        def checkPermissions(self, failure):
            self.failUnless(isinstance(failure.value, PermissionsError))
        
        if isDefaultConfig():
            resource = self.serverNoAuth.getResource(url=self.path)
            
            return resource.supportsWebDAV().addErrback(
                        lambda f:
                            self.failUnless(
                                isinstance(f.value, PermissionsError)))

    ### LMDTODO: Write test that tests redirect of OPTIONS

class TestNoPropfind(WebDAVTestCase):
    TEMP_RSRC_NAME = "rsrc"
    localServer = True
    
    class HTTPResource(TestServerResource):
        def render_PROPFIND(self, request):
            result = self.render_OPTIONS(request)
            request.setResponseCode(405)
            return result
        
        render_GET = TestServerResource.renderFixedValues

    def _getTestResource(self):
        return self.server.getResource("%s%s" % (self.path,
                                                  self.TEMP_RSRC_NAME))
    
    def _setServerResource(self, serverResource):
        # Add the resource to the server's resource tree
        topLevelResource = self.siteFactory.resource.children['folder']
        topLevelResource.putChild(self.TEMP_RSRC_NAME, serverResource)

        

    def testNoPropfind(self):
        # Set up our test resource
        serverResource = self.HTTPResource(exists=True, isLeaf=True)
        serverResource.responseCode = 200
        serverResource.body = "This is a test\n"
        serverResource.headers = {
            'Content-Type': 'text/plain; charset="us-ascii"',
            'Content-Length': str(len(serverResource.body)),
            'ETag': 'the-entity-tag'
        }
        self._setServerResource(serverResource)

        self.siteFactory.options = list(self.siteFactory.options)
        self.siteFactory.options.remove("PROPFIND")
        #        self.siteFactory = webdav_server.getTestSite()
        
        rsrc = self._getTestResource()
        
        def checkETag(returnedResource):
            self.failUnlessEqual(returnedResource, rsrc)
            self.failUnlessEqual(rsrc.etag, 'the-entity-tag')
        
        d = rsrc.propfind(depth=0)
        d.addCallback(checkETag)
        
        return d
    
    def testEmptyPropfind(self):
        # Set up our test resource
        serverResource = self.HTTPResource(exists=True, isLeaf=True)
        serverResource.responseCode = 207
        serverResource.body = """<?xml version="1.0" encoding="utf-8"?>
                              <D:multistatus xmlns:D="DAV:"></D:multistatus>
                              """
        serverResource.headers = {
            'Content-Type': 'application/xml',
            'Content-Length': str(len(serverResource.body))
        }
        self._setServerResource(serverResource)
        serverResource.render_PROPFIND = serverResource.renderFixedValues

        rsrc = self._getTestResource()
        
        d = rsrc.exists()
        # We expect exists() to return False in this case
        d.addCallback(self.failIf)

        return d

class TestPropfind(WebDAVTestCase):
    def setUp(self):
        super(TestPropfind, self).setUp()
        self.collection = self.server.getResource(self.path)
        #collection.createFile("testfile.txt")

    def testIsCollection(self):
        return self.collection.isCollection().addCallback(self.failUnless)
    
    def testGetAllChildren(self):
        return self.collection.getAllChildren()
        # i.e. succeed unless this raises for some reason.
    
class TestGetAllChildren(WebDAVTestCase):
    def setUp(self):
        super(TestGetAllChildren, self).setUp()
        COLLECTION_NAME = "testcoll/"

        self.collection = self.server.getResource(self.path)
        self.testCollection = self.server.getResource(self.collection.path + COLLECTION_NAME)
        
        d = self.testCollection.exists()
        
        d = d.addCallback(
                lambda exists: exists and self.testCollection.delete())
        
        d = d.addCallback(
                lambda _: self.collection.createCollection(COLLECTION_NAME))
                
        
        def createChildren(parent):
            deferreds = []
            
            deferreds.append(parent.createFile(
                "file1.txt",
                body="Hello, cruel world!"))

            deferreds.append(parent.createFile(
                "file2.html",
                body="<html><body>Hello,&#x20;,cruel world!</body></html>",
                type="text/html"))
            
            deferreds.append(parent.createCollection("coll3/"))

            def checkCreatedChildren(resultList):
                for success, result in resultList:
                    self.failUnless(success)
                    self.failIf(result is None)
            
            return DeferredList(deferreds).addCallback(checkCreatedChildren)
        
        d = d.addCallback(createChildren)
        return d
    
    def tearDown(self):
        d = self.testCollection.delete()
        d.addBoth(lambda _: super(TestGetAllChildren, self).tearDown())
        return d
        
    def _checkChildrenCollectionStatus(self, children, resultTuples):
        self.failUnlessEqual(len(children), len(resultTuples), "Internal test error")
        
        for i in xrange(len(children)):
            child = children[i]
            success, result = resultTuples[i]
            
            self.failUnless(success, "Unexpected failure %s in isCollection() for %s" % (result, child))
            
            self.failUnlessEqual(result, (child.path[-1:] == "/"),
                "[%s] WebDAV collection names must end in /" % (child.path))

    
    def _checkTheChildren(self, children):
        self.failUnless(children != None, "Failed to get children")
        self.failUnlessEqual(len(children), 4, "Expected exactly 4 values, got %d" % len(children))
        self.failUnless(self.testCollection in children,
                        "getAllChildren() should contain parent")
        
        expectedChildPaths = set([self.testCollection.path,
                                  self.testCollection.path + "file1.txt",
                                  self.testCollection.path + "file2.html",
                                  self.testCollection.path + "coll3/"])
        actualChildPaths = set()

        childDeferreds = []
        trueChildren = []
                                  
        for child in children:

            actualChildPaths.add(child.path)

            if child != self.testCollection:
                trueChildren.append(child)
                childDeferreds.append(child.isCollection())

        self.failUnlessEqual(expectedChildPaths, actualChildPaths)
        
        d = DeferredList(childDeferreds)
        d.addCallback(lambda resultList:
            self._checkChildrenCollectionStatus(trueChildren, resultList))
            
        return d
    
    def testGetAllChildren(self):
    
        d = self.testCollection.getAllChildren()
        
        d = d.addCallback(self._checkTheChildren)
        
        return d
        
    def testGetAllChildrenNoParent(self):
    
        d = self.testCollection.getAllChildren(includeParent = False)
    
        d.addCallback(lambda l:
            self.failIf(self.testCollection in l))


class TestPut(WebDAVTestCase):
    def setUp(self):
        super(TestPut, self).setUp()
        self.collection = self.server.getResource(self.path)
        
        return self.collection.isCollection().addCallback(self.failUnless)

    def testRawPut(self):

        rawPutPath = self.path + "rawputtest.txt"

        def _checkRawPut(response):
            newfile = self.server.getResource(rawPutPath)
            d = newfile.exists().addCallback(self.failUnless)
            
            bogusfile = self.server.getResource(rawPutPath + "bogus.txt")
            
            d = d.addCallback(lambda x: bogusfile.exists()).addCallback(self.failIf)
            
            return d

        d =  self.server.put(rawPutPath, "rawputtestbody")
        d = d.addCallback(_checkRawPut)
        
        return d
        
    def testPutNonAscii(self):
        path = u"%s%s" % (self.collection.path, u"\u2022 bulleted filename.txt")
        testResource = self.server.getResource(path)
        
        d = testResource.put(body="Hello, world", checkETag=False)
        
        return d


    def testCreateNew(self):
        def _checkCreateNew(result):
            newfile = self.server.getResource(self.path + "testfile.txt")
            self.failUnlessEqual(result, newfile)
            return newfile.exists().addCallback(self.failUnless)

        d = self.collection.createFile("testfile.txt")
        d = d.addCallback(_checkCreateNew)
        return d

    def testCreateNewOverwrite(self):
        """
        Check that creating a given resource twice fails with a
        412 (precondition failed) error.
        """
        def _checkCreateFailure(failure):
            self.failUnless(isinstance(failure.value, HTTPError))
            self.failUnlessEqual(failure.value.status, 412)

        # Try to create the same file twice, make sure we get a 412
        d = self.collection.createFile("testfile.txt")
        d = d.addCallback(lambda res: self.collection.createFile("testfile.txt"))
        
        d = d.addCallbacks(self.fail, _checkCreateFailure)
        
        return d
        
    def testCreateAndUpdate(self):
        # Make sure we can update a newly created file
        def updateContents(resource):
            d = resource.put("New content\n", contentType="text/plain")
            d.addCallback(self.failIf) # Supposed to return None
            return d
        
        d = self.collection.createFile("testfile.txt")
        
        d.addCallback(updateContents)
        
        return d

    def testConflict(self):
        def checkFailure(failure):
            self.failUnless(isinstance(failure.value, HTTPError))
            self.failUnlessEqual(failure.value.status, 412)
            
        def updateContents(resource):
            def updateAgain(__):
                d = resource.put("Newer newer content")
                d.addCallbacks(self.fail, checkFailure)
                return d
        
            # PUT via the server handle so this resource doesn't
            # know things have changed
            d = resource.serverHandle.put(resource.path, "New content\n",
                          contentType="text/plain")
                          
            d.addCallback(updateAgain)
            return d

        d = self.collection.createFile("testfile.txt")
        
        d.addCallback(updateContents)
        
        return d

    def testAvoidConflict(self):
        def updateContents(resource):
            def updateAgain(__):
                d = resource.put("Newer newer content", checkETag=False)
                return d
        
            # PUT via the server handle so this resource doesn't
            # know things have changed
            d = resource.serverHandle.put(resource.path, "New content\n",
                          contentType="text/plain")
                          
            d.addCallback(updateAgain)
            return d

        d = self.collection.createFile("testfile.txt")
        
        d.addCallback(updateContents)
        
        return d
        
    def testIgnorePropfindError(self):
    
        rsrcName = 'testme.txt'
        
        # A resource that doesn't do etags
        class NoETagResource(webdav_server.WebDAVResource):
            def render_PUT(self, request):
                self.exists = True
                
                request.setResponseCode(204)
                return ''
            
            def render_PROPFIND(self, request):
                request.setResponseCode(501)
                request.setHeader('content-type', 'text/html; charset="UTF-8"')
                return "<html><body><p>Don't do PROPIND</p></body></html>"
                
        # Set up our test resource
        serverResource = NoETagResource(exists=False, isLeaf=True)

        # ... and add it to the server's resource tree
        topLevelResource = self.siteFactory.resource.children['folder']
        topLevelResource.putChild(rsrcName, serverResource)


        clientPath = self.collection.path + rsrcName
        clientResource = self.server.getResource(clientPath)
        d = clientResource.put('Hello', checkETag=False)
        
        return d



class TestMkcol(WebDAVTestCase):
    def setUp(self):
        super(TestMkcol, self).setUp()
        self.collection = self.server.getResource(self.path)
        
        d = self.server.factory.addRequest(Request('DELETE', self.path + "testmkcol/", {}, None))
        
        newCollection = self.server.getResource(self.path + "testmkcol/")
        d = d.addCallback(lambda resp: newCollection.exists())
        d = d.addCallback(self.failIf)
        
        return d
            
    def tearDown(self):
        newCollection = self.server.getResource(self.path + "testmkcol/")
        
        d = self.server.factory.addRequest(Request('DELETE', self.path + "testmkcol/", {'Connection' : 'close'}, None))
        d.addBoth(lambda _: super(TestMkcol, self).tearDown())
        return d
            
        
    def testMkcol(self):
        d = self.collection.createCollection("testmkcol/")
        d = d.addCallback(lambda result: result.exists())
        d = d.addCallback(self.failUnless)
        
        return d

class TestDelete(WebDAVTestCase):

    DELETE_FILENAME = "testdelete.txt"

    def setUp(self):
        super(TestDelete, self).setUp()
        self.collection = self.server.getResource(self.path)
        
        d = self.collection.isCollection()
        d = d.addCallback(self.failUnless,
                         '%s is not a collection' % (self.collection))
        
        self.resourceToDelete = self.server.getResource(
                                self.collection.path + self.DELETE_FILENAME)
        
        def checkFileToDelete(rsrc):
            self.failUnlessEqual(rsrc, self.resourceToDelete,
                                 "Failed to create test resource")

        def createIfNecessary(exists):
            if exists:
                d = self.collection.createFile(self.DELETE_FILENAME)
                d = d.addCallback(checkFileToDelete)
                return d
        
        d = d.addCallback(lambda _: self.resourceToDelete.exists())
        
        d = d.addCallback(createIfNecessary)
        
        return d
        

    def testDelete(self):
        d = self.resourceToDelete.delete()
        
        def checkDeleted(response):
            return self.resourceToDelete.exists().addCallback(self.failIf)
        
        d = d.addCallback(checkDeleted)
        
        return d
        

    ### LMDTODO: Test delete failures

class WebDAVTicketTestCase(WebDAVTestCase):

    TEMP_COLLECTION_NAME = "temp-collection"
    localServer = True
    
    class TicketableResource(TestServerResource):
        render_MKTICKET = TestServerResource.renderFixedValues
        render_DELTICKET = TestServerResource.renderFixedValues

    def _getTestCollection(self):
        return self.server.getResource("%s%s/" % (self.path, \
                                             self.TEMP_COLLECTION_NAME))

    def setUp(self):
        
        self.siteFactory = webdav_server.getTestSite()

        super(WebDAVTicketTestCase, self).setUp()
        
        # Set up the resource on the server
        topLevelResource = self.siteFactory.resource.children['folder']
        self.serverResource = self.TicketableResource(exists=True, isLeaf=False)
        topLevelResource.putChild(self.TEMP_COLLECTION_NAME,
                                  self.serverResource)

class SupportsTicketsTestCase(WebDAVTicketTestCase):

    def testSupportsTickets(self):
        # Check zanshin.webdav.Resource.supportsTickets() returns
        # True for a server advertising MKTICKET and DELTICKET
        # in Allow:.
        #
        self.siteFactory.options = list(self.siteFactory.options)
        self.siteFactory.options += ["MKTICKET", "DELTICKET"]
        d = self._getTestCollection().supportsTickets()
        d.addCallback(self.failUnless)
            
        return d

    def testSupportsTicketsViaDAVHeader(self):
        # Check zanshin.webdav.Resource.supportsTickets() returns
        # True for a server advertising 'tickets'
        # in DAV: (Xythos seems to do this).
        #
        self.siteFactory.features = list(self.siteFactory.features)
        self.siteFactory.features += ["ticket"]
        d = self._getTestCollection().supportsTickets()
        d.addCallback(self.failUnless)
            
        return d
    def testDoesntSupportTickets(self):
        # Check zanshin.webdav.Resource.supportsTickets() returns
        # False for a server not advertising MKTICKET.
        d = self._getTestCollection().supportsTickets()
        d.addCallback(self.failIf)
        
        return d
            


class CreateTicketTestCase(WebDAVTicketTestCase):

    def testParseReadonlyTicket(self):
        # Test of parsing a read-only <ticketinfo>.in an XML body from
        # a MKTICKET request
        
        def _checkTicketValues(self, ticket):
            self.failUnless(isinstance(ticket, Ticket),
                "Expected a zanshin.ticket.Ticket, got a %s" % (type(ticket)))
            self.failUnlessEqual(ticket.ticketId, '266dxwmag0')
            self.failUnlessEqual(ticket.visits, None)
            self.failUnlessEqual(ticket.timeoutSeconds, 3600)
            self.failUnlessEqual(ticket.ownerUri, 'http://localhost:8080/principal/bcm')
            self.failIf(ticket.read)
    
        self.serverResource.responseCode = 200
        self.serverResource.headers = {
            'Content-Type': 'text/xml; charset="UTF-8"',
            'Ticket': '266dxwmag0'
        }
        self.serverResource.body = \
          """<?xml version="1.0" encoding="UTF-8"?>
          <D:prop xmlns:D="DAV:"
                  xmlns:ticket="http://www.xythos.com/namespaces/StorageServer">
            <ticket:ticketdiscovery>
              <ticket:ticketinfo>
                <ticket:id>266dxwmag0</ticket:id>
                <D:owner>
                  <D:href>http://localhost:8080/principal/bcm</D:href>
                </D:owner>
                <ticket:timeout>Second-3600</ticket:timeout>
                <ticket:visits>infinity</ticket:visits>
                <D:privilege>
                </D:privilege>
              </ticket:ticketinfo>
            </ticket:ticketdiscovery>
          </D:prop>
        """

        d = self._getTestCollection().createTicket()
        d.addCallback(lambda t: _checkTicketValues(self, t))
        return d

    def testParseReadwriteTicket(self):
        # Test of parsing a read-write <ticketinfo>.in an XML body from
        # a MKTICKET request
        def _checkTicketValues(self, ticket):
            self.failUnless(isinstance(ticket, Ticket),
                "Expected a zanshin.ticket.Ticket, got a %s" % (type(ticket)))
            self.failUnlessEqual(ticket.ticketId, 'ksjk345d_p')
            self.failUnlessEqual(ticket.visits, 120)
            self.failUnlessEqual(ticket.timeoutSeconds, None)
            self.failUnlessEqual(ticket.ownerUri, 'http://localhost:8080/principal/bcm')
            self.failUnless(ticket.read)
    
        self.serverResource.responseCode = 200
        self.serverResource.headers = {
            'Content-Type': 'text/xml; charset="UTF-8"',
            'Ticket': 'ksjk345d_p'
        }
        self.serverResource.body = \
          """<?xml version="1.0" encoding="UTF-8"?>
          <D:prop xmlns:D="DAV:"
                  xmlns:ticket="http://www.xythos.com/namespaces/StorageServer">
            <ticket:ticketdiscovery>
              <ticket:ticketinfo>
                <ticket:id>ksjk345d_p</ticket:id>
                <D:owner>
                  <D:href>http://localhost:8080/principal/bcm</D:href>
                </D:owner>
                <ticket:timeout>Infinite</ticket:timeout>
                <ticket:visits>120</ticket:visits>
                <D:privilege>
                  <D:read />
                  <write />
                </D:privilege>
              </ticket:ticketinfo>
            </ticket:ticketdiscovery>
          </D:prop>
        """
    
        d = self._getTestCollection().createTicket()
        d.addCallback(lambda t: _checkTicketValues(self, t))
        return d
        
    def testMultipleTickets(self):
        # Test of parsing a <ticketinfo>.XML body containing multiple
        # a MKTICKET request
        def _checkTicketValues(self, ticket):
            self.failUnless(isinstance(ticket, Ticket),
                "Expected a zanshin.ticket.Ticket, got a %s" % (type(ticket)))
            self.failUnlessEqual(ticket.ticketId, 'ksjk345d_p')
            self.failUnlessEqual(ticket.visits, 120)
            self.failUnlessEqual(ticket.timeoutSeconds, None)
            self.failUnlessEqual(ticket.ownerUri, 'http://localhost:8080/principal/bcm')
            self.failUnless(ticket.read)
    
        self.serverResource.responseCode = 200
        self.serverResource.headers = {
            'Content-Type': 'text/xml; charset="UTF-8"',
            'Ticket': 'ksjk345d_p'
        }
        self.serverResource.body = \
          """<?xml version="1.0" encoding="UTF-8"?>
          <D:prop xmlns:D="DAV:"
                  xmlns:ticket="http://www.xythos.com/namespaces/StorageServer">
            <ticket:ticketdiscovery>
              <ticket:ticketinfo>
                <ticket:id>askdjfkajdf</ticket:id>
                <D:owner>
                  <D:href>http://www.example.com/who</D:href>
                </D:owner>
                <ticket:timeout>Second-3600</ticket:timeout>
                <ticket:visits>40</ticket:visits>
                <D:privilege>
                  <D:read />
                  <write />
                </D:privilege>
              </ticket:ticketinfo>
              <ticket:ticketinfo>
                <ticket:id>ksjk345d_p</ticket:id>
                <D:owner>
                  <D:href>http://localhost:8080/principal/bcm</D:href>
                </D:owner>
                <ticket:timeout>Infinite</ticket:timeout>
                <ticket:visits>120</ticket:visits>
                <D:privilege>
                  <D:read />
                  <write />
                </D:privilege>
              </ticket:ticketinfo>
            </ticket:ticketdiscovery>
          </D:prop>
        """
    
        d = self._getTestCollection().createTicket()
        d.addCallback(lambda t: _checkTicketValues(self, t))
        return d

    def testNoTicketHeader(self):
        self.serverResource.responseCode = 200
        self.serverResource.headers = {
            'Content-Type': 'text/xml; charset="UTF-8"',
        }
        d = self._getTestCollection().createTicket()

        self.assertFailure(d, HTTPError)

        return d

        
    def testMismatchedTicketHeader(self):
        self.serverResource.responseCode = 200
        self.serverResource.headers = {
            'Content-Type': 'text/xml; charset="UTF-8"',
            'Ticket': '266dxwmag0'
        }
        self.serverResource.body = \
          """<?xml version="1.0" encoding="UTF-8"?>
          <D:prop xmlns:D="DAV:"
                  xmlns:ticket="http://www.xythos.com/namespaces/StorageServer">
            <ticket:ticketdiscovery>
              <ticket:ticketinfo>
                <ticket:id>ksjk345d_p</ticket:id>
                <D:owner>
                  <D:href>http://localhost:8080/principal/bcm</D:href>
                </D:owner>
                <ticket:timeout>Infinite</ticket:timeout>
                <ticket:visits>120</ticket:visits>
                <D:privilege>
                  <D:read />
                  <write />
                </D:privilege>
              </ticket:ticketinfo>
            </ticket:ticketdiscovery>
          </D:prop>
          """
        d = self._getTestCollection().createTicket()

        self.assertFailure(d, ValueError)

        return d
        
    def testMissingProp(self):
        #
        # Test that we raise a ValueError when the XML response
        # received isn't a <DAV:prop> element
        #
        self.serverResource.responseCode = 200
        self.serverResource.headers = {
            'Content-Type': 'text/xml; charset="UTF-8"',
            'Ticket': '266dxwmag0'
        }
        self.serverResource.body = \
          """<?xml version="1.0" encoding="UTF-8"?>
          <D:propstat xmlns:D="DAV:"
                  xmlns:ticket="http://www.xythos.com/namespaces/StorageServer">
            <D:status>HTTP/1.1 200 OK</D:status>
            <D:prop>
              <ticket:ticketinfo>
                <ticket:id>ksjk345d_p</ticket:id>
                <D:owner>
                  <D:href>http://localhost:8080/principal/bcm</D:href>
                </D:owner>
                <ticket:timeout>Infinite</ticket:timeout>
                <ticket:visits>120</ticket:visits>
                <D:privilege>
                  <D:read />
                  <write />
                </D:privilege>
              </ticket:ticketinfo>
            </D:prop>
          </D:propstat>
          """
        d = self._getTestCollection().createTicket()

        self.assertFailure(d, ValueError)

        return d

    def testMissingTicketDiscovery(self):
        #
        # Test that we raise a ValueError when the XML response
        # received doesn't contain a <ticketdiscovery element
        #
        self.serverResource.responseCode = 200
        self.serverResource.headers = {
            'Content-Type': 'text/xml; charset="UTF-8"',
            'Ticket': '266dxwmag0'
        }
        self.serverResource.body = \
          """<?xml version="1.0" encoding="UTF-8"?>
          <D:prop xmlns:D="DAV:"
                  xmlns:ticket="http://www.xythos.com/namespaces/StorageServer">
          <ticket:ticketinfo>
            <ticket:id>ksjk345d_p</ticket:id>
            <D:owner>
              <D:href>http://localhost:8080/principal/bcm</D:href>
            </D:owner>
            <ticket:timeout>Infinite</ticket:timeout>
            <ticket:visits>120</ticket:visits>
            <D:privilege>
              <D:read />
              <write />
            </D:privilege>
          </ticket:ticketinfo>
          </D:prop>
          """
        d = self._getTestCollection().createTicket()

        self.assertFailure(d, ValueError)

        return d
        
class DeleteTicketTestCase(WebDAVTicketTestCase):
    
    def testDeleteTicket(self):
        # Check that Resource.deleteTicket() succeeds (returns a deferred
        # to None) when the server response is 204 (NO_CONTENT)
        self.serverResource.responseCode = 204
        
        ticket = Ticket(False)
        ticket.ticketId = 'that_s_the_ticket'

        d = self._getTestCollection().deleteTicket(ticket)
        
        d.addCallback(lambda res: self. failUnlessEqual(res, None))
        return d

    def testDeleteByTicketId(self):
        # Check that Resource.deleteTicket() succeeds when passing in
        # a ticket id rather than a ticket instance
        self.serverResource.responseCode = 204

        d = self._getTestCollection().deleteTicket('Hello-my-little-ticket')
        
        d.addCallback(lambda res: self. failUnlessEqual(res, None))
        return d

    def testDeleteTicketNoId(self):
        # Check that Resource.deleteTicket() immediately raises
        # a ValueError when passing in a ticket with no id
        self.serverResource.responseCode = 204
        
        ticket = Ticket(False)

        self.failUnlessRaises(
            ValueError,
            self._getTestCollection().deleteTicket,
            ticket)
        
    def testDeleteTicketFailure(self):
        # Check that Resource.deleteTicket() generates an http.HTTPError
        # when the server response is not 204 (NO_CONTENT)
        self.serverResource.responseCode = 200

        d = self._getTestCollection().deleteTicket('not-important')

        self.assertFailure(d, HTTPError)

        return d
        
class GetTicketsTestCase(WebDAVTestCase):
    TEMP_COLLECTION_NAME = "temp-collection"
    localServer = True
    
    class GetTicketResource(TestServerResource):
        render_PROPFIND = TestServerResource.renderFixedValues

    def _getTestCollection(self):
        return self.server.getResource("%s%s/" % (self.path, \
                                             self.TEMP_COLLECTION_NAME))

    def setUp(self):
        
        self.siteFactory = webdav_server.getTestSite()

        super(GetTicketsTestCase, self).setUp()
        
        # Set up the resource on the server
        topLevelResource = self.siteFactory.resource.children['folder']
        self.serverResource = self.GetTicketResource(exists=True, isLeaf=False)
        topLevelResource.putChild(self.TEMP_COLLECTION_NAME,
                                  self.serverResource)
                                  
    def testGetTickets(self):
        self.serverResource.responseCode = 207
        self.serverResource.headers = {
            'content-type': 'application/xml; charset="utf-8"'
        }
        self.serverResource.body = """<D:multistatus xmlns:D="DAV:"><D:response><D:href>http://localhost:8080/home/demo/demo_s_calendar/</D:href><D:propstat><D:prop><ticket:ticketdiscovery xmlns:ticket="http://www.xythos.com/namespaces/StorageServer"><ticket:ticketinfo><ticket:id>v598wihjr1</ticket:id><D:owner><D:href>http://localhost:8080/home/demo/</D:href></D:owner><ticket:timeout>Infinite</ticket:timeout><ticket:visits>infinity</ticket:visits><D:privilege><D:read /><D:write /></D:privilege></ticket:ticketinfo><ticket:ticketinfo><ticket:id>xui8q8hjr0</ticket:id><D:owner><D:href>http://localhost:8080/home/demo/</D:href></D:owner><ticket:timeout>Infinite</ticket:timeout><ticket:visits>infinity</ticket:visits><D:privilege><D:read /></D:privilege></ticket:ticketinfo></ticket:ticketdiscovery></D:prop><D:status>HTTP/1.1 200 OK</D:status></D:propstat></D:response></D:multistatus>"""
        
        def checkTickets(tickets):
        
            self.failUnless(isinstance(tickets, list))
            self.failUnlessEqual(len(tickets), 2)
            
            ticket = tickets[0]
            self.failUnless(isinstance(ticket, Ticket),
                "Expected a zanshin.ticket.Ticket, got a %s" % (type(ticket)))
            self.failUnlessEqual(ticket.ticketId, 'v598wihjr1')
            self.failUnlessEqual(ticket.ownerUri, 'http://localhost:8080/home/demo/')
            self.failUnlessEqual(ticket.timeoutSeconds, None)
            self.failUnlessEqual(ticket.visits, None)
            self.failUnless(ticket.read)
            self.failUnless(ticket.write)

            ticket = tickets[1]
            self.failUnless(isinstance(ticket, Ticket),
                "Expected a zanshin.ticket.Ticket, got a %s" % (type(ticket)))
            self.failUnlessEqual(ticket.ticketId, 'xui8q8hjr0')
            self.failUnlessEqual(ticket.ownerUri, 'http://localhost:8080/home/demo/')
            self.failUnlessEqual(ticket.timeoutSeconds, None)
            self.failUnlessEqual(ticket.visits, None)
            self.failUnless(ticket.read)
            self.failIf(ticket.write)
    
        d = self._getTestCollection().getTickets()
        d.addCallback(checkTickets)
        return d

        

class TicketAuthTestCase(WebDAVTestCase):
    
    localServer = True
    
    def setUp(self):

        class TicketRecordingResource(webdav_server.WebDAVResource):
            def render(rsrc, request):
                # Record the Ticket: header received with each request.
                t = request.getHeader('ticket')
                
                self.siteFactory.receivedTickets.append(t)
                
                return webdav_server.WebDAVResource.render(rsrc, request)
            render_MKCALENDAR = webdav_server.WebDAVResource.render_MKCOL
    

        super(TicketAuthTestCase, self).setUp()
        self.siteFactory.receivedTickets = []
        
        # Set up the resource on the server
        collectionName = "temp-collection"

        topLevelResource = self.siteFactory.resource.children['folder']
        self.serverResource = TicketRecordingResource(exists=True, isLeaf=False)
        topLevelResource.putChild(collectionName, self.serverResource)
        
        self.serverResource.putChild('one child',
                                     webdav_server.WebDAVResource(exists=True, isLeaf=False))
        self.serverResource.putChild('another child',
                                     webdav_server.WebDAVResource(exists=True, isLeaf=True))
                                  
        # The client-side view of the resource
        self.resource = self.server.getResource("%s%s/" % (self.path,
                                                           collectionName))
        self.resource.ticketId = '2374'

    def _checkTickets(self, result):
        ticketSet = set(self.siteFactory.receivedTickets)
        
        self.failIfEqual(len(ticketSet), 0,
                          "Internal test error: no tickets recorded")
        
        self.failIf(None in ticketSet,
                    "Some request(s) missing 'Ticket' header")
        self.failIf(len(ticketSet) > 1,
                    "More than 1 ticket value sent")
        self.failUnlessEqual(ticketSet, set([self.resource.ticketId]))
        

    
    def testOptions(self):
    
        return self.resource.options().addCallback(self._checkTickets)
        
    def testCreateCollection(self):
    
        def checkChildCollection(coll):
            self.failUnlessEqual(coll.ticketId, self.resource.ticketId)
            self._checkTickets(coll)
    
        d = self.resource.createCollection('x')
        return d.addCallback(checkChildCollection)

    def testCreateCalendar(self):
    
        def checkChildCalendar(cal):
            self.failUnlessEqual(cal.ticketId, self.resource.ticketId)
            self._checkTickets(cal)
    
        d = self.resource.createCalendar('x')
        return d.addCallback(checkChildCalendar)

    def testCreateFile(self):
    
        def checkChildFile(f):
            self.failUnlessEqual(f.ticketId, self.resource.ticketId)
            self._checkTickets(f)
    
        d = self.resource.createFile("my file")
        return d.addCallback(checkChildFile)
        
    def testPut(self):
        self.childResource = self.server.getResource(
                                "%s%s" % (self.resource.path, "test-file.txt"))
        self.childResource.ticketId = self.resource.ticketId
        d = self.childResource.put("my file", checkETag=False)
        return d.addCallback(self._checkTickets)

    def testGetAllChildren(self):
    
        def checkChildTickets(children):
            for rsrc in children:
                self.failUnlessEqual(rsrc.ticketId, self.resource.ticketId)
            self._checkTickets(children)
    
        d = self.resource.getAllChildren()
        return d.addCallback(checkChildTickets)
        

class PropfindTestCase(WebDAVTestCase):
    TEST_RESOURCE_NAME = 'test-collection'
    
    class PropfindResource(TestServerResource):
        render_PROPFIND = TestServerResource.renderFixedValues

    def _getTestCollection(self):
        return self.server.getResource("%s%s/" % (self.path, \
                                             self.TEST_RESOURCE_NAME))
    
    def setUp(self):
        self.siteFactory = webdav_server.getTestSite()
        
        super(PropfindTestCase, self).setUp()
        
        # Set up the resource on the server
        
        topLevelResource = self.siteFactory.resource.children['folder']
        self.serverResource = self.PropfindResource(exists=True, isLeaf=False)
        self.serverResource.responseCode = 207 # MULTISTATUS
        self.serverResource.headers = { 'Content-type': 'application/xml' }
        topLevelResource.putChild(self.TEST_RESOURCE_NAME,
                                  self.serverResource)
                                  
    def testUriPercentEscape(self):
        self.serverResource.body = """<?xml version="1.0" encoding="UTF-8"?>
<D:multistatus xmlns:D="DAV:">
     <D:response>
       <D:href>/folder/%74est-collection/</D:href>
       <D:propstat>
         <D:prop>
             <D:getetag>12345</D:getetag>
             <D:resourcetype><D:collection/></D:resourcetype>
         </D:prop>
         <D:status>HTTP/1.1 200 OK</D:status>
       </D:propstat>
     </D:response>
   </D:multistatus>"""
   
        resource = self._getTestCollection()
        
        d = resource.propfind(depth=0)
        
        # Check that we matched the top-level URI
        d = d.addCallback(lambda _:
            self.failUnlessEqual(resource.etag, "12345"))

        return d
        
    def testNonAsciiName(self):
    
        name = u'\2022 Bulleted'

        self.serverResource.body = """<?xml version="1.0" encoding="UTF-8"?>
<D:multistatus xmlns:D="DAV:">
     <D:response>
       <D:href>/folder/%74est-collection/</D:href>
       <D:propstat>
         <D:prop>
             <D:getetag>12345</D:getetag>
             <D:resourcetype><D:collection/></D:resourcetype>
         </D:prop>
         <D:status>HTTP/1.1 200 OK</D:status>
       </D:propstat>
     </D:response>
     <D:response>
       <D:href>/folder/test-collection/%E2%80%A2%20Wonderful/</D:href>
       <D:propstat>
         <D:prop>
             <D:getetag>12345</D:getetag>
             <D:resourcetype><D:collection/></D:resourcetype>
         </D:prop>
         <D:status>HTTP/1.1 200 OK</D:status>
       </D:propstat>
     </D:response>
   </D:multistatus>"""
   
        resource = self._getTestCollection()

        def checkChildren(children):
            self.failUnlessEqual(len(children), 1,
                      "Expected 1 child in %s" % (children,))
            self.failUnlessEqual(children[0].path,
                                 resource.path + u"\u2022 Wonderful/")
   
        
        d = resource.getAllChildren(includeParent=False)
        
        # Check that we matched the top-level URI
        return d.addCallback(checkChildren)
        
class ExistsTestCase(WebDAVTestCase):
    # Tests of the zanshin.webdav.Resource.exists() method
    localServer = True

    def setUp(self):
        self.siteFactory = webdav_server.getTestSite()
        super(ExistsTestCase, self).setUp()
        
    class ExistsTestResource(webdav_server.WebDAVResource):
    
        def __init__(self, test, **keywds):
            webdav_server.WebDAVResource.__init__(self, **keywds)
            
            testResourceName = "test-resource"

            topLevelResource = test.siteFactory.resource.children['folder']
            topLevelResource.putChild(testResourceName, self)
        
            if not self.isLeaf:
                testResourceName += "/"
        
            test.clientResource = \
                test.server.getResource(test.path + testResourceName)
                
            self.deferred = test.clientResource.exists()


        def setUpFailure(self, code, *httpMethods):
        
            def renderFailure(request):
                import twisted.web.error
                page = twisted.web.error.ErrorPage(
                    code,
                    None,
                    "Failing for test purposes.")
                return page.render(request)
            
            if not httpMethods:
                self.render = renderFailure
            else:
                for m in httpMethods:
                    setattr(self, 'render_%s' % (m,), renderFailure)

            
    def testHeadExisting(self):
        "Check that we use HEAD if available, on a rsrc that exists"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        testResource.setUpFailure(501, 'OPTIONS', 'PROPFIND')
        testResource.features = []
        testResource.options = ['GET', 'HEAD', 'OPTIONS', 'PROPFIND']
        
        return testResource.deferred.addCallback(self.failUnless)

    def testHeadNotExisting(self):
        "Check that we use HEAD if available, on a rsrc that doesn't exist"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        testResource.setUpFailure(501, 'PROPFIND')
        testResource.setUpFailure(404, 'HEAD')
        testResource.features = []
        testResource.options = ['GET', 'HEAD', 'OPTIONS', 'PROPFIND']
        
        return testResource.deferred.addCallback(self.failIf)

    def testHeadError(self):
        "Check an access error on HEAD is reported correctly"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        testResource.setUpFailure(501, 'OPTIONS', 'PROPFIND')
        testResource.setUpFailure(401, 'HEAD')
        testResource.features = []
        testResource.options = ['GET', 'HEAD', 'OPTIONS']
        
        deferred = self.resource.exists()
        
        self.assertFailure(deferred, HTTPError)
        
        return deferred


    def testPropfindNoResource(self):
        "Do we use PROPFIND if available, on a rsrc that doesn't exist, if HEAD returns a 405?"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        testResource.setUpFailure(405, 'HEAD', 'GET')
        testResource.setUpFailure(404, 'PROPFIND')
        testResource.features = []
        testResource.options = ['OPTIONS', 'PROPFIND']
        
        return testResource.deferred.addCallback(self.failIf)

    def testPropfindValidResource(self):
        "Do we use PROPFIND if available, on a rsrc that exists, if HEAD returns a 405?"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        testResource.setUpFailure(405, 'HEAD', 'GET')
        testResource.features = []
        testResource.options = ['GET', 'HEAD', 'OPTIONS', 'PROPFIND']
        
        return testResource.deferred.addCallback(self.failUnless)

    def testPropfindNoResourceBadOptions(self):
        "Check that we use PROPFIND if available, on a rsrc that doesn't exist"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        testResource.setUpFailure(501, 'OPTIONS', 'GET')
        testResource.setUpFailure(404, 'PROPFIND')
        testResource.features = []
        testResource.options = ['GET', 'HEAD', 'OPTIONS', 'PROPFIND']
        
        return testResource.deferred.addCallback(self.failIf)

    def testPropfindNoResourceBadOptions(self):
        "Check that we use PROPFIND if available, on a rsrc that exists"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        testResource.setUpFailure(405, 'GET')
        testResource.features = []
        testResource.options = ['GET', 'HEAD', 'OPTIONS', 'PROPFIND']
        
        return testResource.deferred.addCallback(self.failUnless)

        
    def testPropfindError(self):
        "Do we fall back to HEAD if PROPFIND returns an error?"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        
        testResource.setUpFailure(405, 'PROPFIND')
        testResource.features = []
        testResource.options = ['GET', 'HEAD', 'OPTIONS']
        
        return testResource.deferred.addCallback(self.failUnless)

    def testHeadError(self):
        "Do we fall back to PROPFIND if HEAD returns an error?"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)
        
        testResource.setUpFailure(405, 'GET')
        testResource.features = []
        testResource.options = ['PROPFIND', 'OPTIONS']
        
        return testResource.deferred.addCallback(self.failUnless)

    def testPropfindOnlyIfSupported(self):
        "Test that we don't try a PROPFIND for servers that don't support it"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=False)

        # Try to look like a plain old HTTP server
        testResource.features = []
        testResource.options = ['GET', 'HEAD','OPTIONS']

        # Tell the client that the resource doesn't exist if a
        # PROPFIND request is sent..
        testResource.setUpFailure(404, 'PROPFIND')

        # ... and only succeed if the resource exists.
        return testResource.deferred.addCallback(self.failUnless)
        
    def testAllResponsesAre404(self):
        "Test that exists() returns False if all requests return a 404"

        testResource = self.ExistsTestResource(self, exists=True, isLeaf=True)
        testResource.setUpFailure(404)
        
        return testResource.deferred.addCallback(self.failIf)


    def test404PropfindGet(self):
        "Test that exists() returns False if PROPFIND/GET/HEAD return a 404"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=True)
        
        testResource.setUpFailure(404, 'GET', 'PROPFIND')
        
        return testResource.deferred.addCallback(self.failIf)

    def test401All(self):
        "Test that exists() returns an error if PROPFIND/GET return a 401"
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=True)

        testResource.setUpFailure(401, 'GET', 'PROPFIND')
        
        self.assertFailure(testResource.deferred, PermissionsError)
        
        return testResource.deferred

    def test401Propfind(self):
        "Test that exists() returns True if PROPFIND return a 401 but HEAD succeeds."
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=True)

        testResource.setUpFailure(401,'PROPFIND')
        
        return testResource.deferred.addCallback(self.failUnless)

    def test401PropfindOptions(self):
        "Test that exists() returns True if PROPFIND return a 401 but HEAD succeeds."
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=True)

        testResource.setUpFailure(401,'PROPFIND', 'OPTIONS')
        
        return testResource.deferred.addCallback(self.failUnless)

    def test302(self):
        "Test that exists() returns True if HEAD returns a 302"
        
        # Not 100% clear if this is really what we want. But
        # some servers redirect requests of bad URLs to an
        # error page.
        testResource = self.ExistsTestResource(self, exists=True, isLeaf=True)

        testResource.setUpFailure(302,'GET')
        testResource.options = [ 'GET', 'HEAD', 'OPTIONS' ]
        
        return testResource.deferred.addCallback(self.failIf)


class RedirectTestCase(WebDAVTestCase):
    localServer = True
    TEST_RESOURCE_NAME = 'test.txt'
    
    def setUp(self):
        super(RedirectTestCase, self).setUp()
        topLevelResource = self.siteFactory.resource.children['folder']

        self.serverResource = TestServerResource(exists=True, isLeaf=True)
        self.serverResource.responseCode = 302
        self.serverResource.headers = {
            'Location': 'http://%s:%d%s%s' % (self.host, self.port,
                                              self.path, "xxx-redir.txt")
        }
        self.serverResource.render_GET = self.serverResource.renderFixedValues
        
        topLevelResource.putChild(self.TEST_RESOURCE_NAME, self.serverResource)
    
    def testRedirect(self):
        """
        Test that GETting a redirected resource behaves correctly (i.e.
        fetches the target URI).
        """
        topLevelResource = self.siteFactory.resource.children['folder']

        redirectedResource = TestServerResource(exists=True, isLeaf=True)
        redirectedResource.responseCode = 200
        redirectedResource.body = 'Woo-hoo!!'
        redirectedResource.render_GET = redirectedResource.renderFixedValues

        topLevelResource.putChild("xxx-redir.txt", redirectedResource)

        def checkResponse(response):
            self.failUnlessEqual(response.status, 200)
            self.failUnlessEqual(response.body, 'Woo-hoo!!')
            
        
        resource = self.server.getResource("%s%s" % (self.path,
                                                     self.TEST_RESOURCE_NAME))
                                                     
        return resource.get().addCallback(checkResponse)


    def testTwoRedirects(self):
        """
        Test that redirecting to a resource which is in turn
        redirected works.
        """
        topLevelResource = self.siteFactory.resource.children['folder']

        redir1 = TestServerResource(exists=True, isLeaf=True)
        redir1.responseCode = 302
        redir1.headers = {
            'Location': 'http://%s:%d%s%s' % (self.host, self.port,
                                              self.path, "xxx-redir-twice.txt")
        }
        redir1.render_GET = redir1.renderFixedValues

        topLevelResource.putChild("xxx-redir.txt", redir1)

        def checkResponse(response):
            self.failUnlessEqual(response.status, 404)
            
        
        resource = self.server.getResource("%s%s" % (self.path,
                                                     self.TEST_RESOURCE_NAME))
                                                     
        return resource.get().addCallback(checkResponse)
        
    def testRedirectNoHost(self):
        """
        Test that omitting the host & port from the
        Location: URI in a redirect works.
        """
        self.serverResource.headers = {
            'Location': '%s%s' % (self.path, "xxx-redir.txt")
        }

        topLevelResource = self.siteFactory.resource.children['folder']

        redirectedResource = TestServerResource(exists=True, isLeaf=True)
        redirectedResource.responseCode = 200
        redirectedResource.body = 'Woo-hoo!!'
        redirectedResource.render_GET = redirectedResource.renderFixedValues

        topLevelResource.putChild("xxx-redir.txt", redirectedResource)

        def checkResponse(response):
            self.failUnlessEqual(response.status, 200)
            self.failUnlessEqual(response.body, 'Woo-hoo!!')
            
        
        resource = self.server.getResource("%s%s" % (self.path,
                                                     self.TEST_RESOURCE_NAME))
                                                     
        return resource.get().addCallback(checkResponse)


class CalDAVSupportTestCase(WebDAVTestCase):
    localServer = True
    
    def setUp(self):
        self.siteFactory = webdav_server.getTestSite()
        super(CalDAVSupportTestCase, self).setUp()

    def testNoCalDAVSupport(self):
        rsrc = self.server.getResource(self.path)

        return rsrc.supportsCalDAV().addCallback(self.failIf)

    def testCalDAVSupport(self):
        self.siteFactory.features = list(self.siteFactory.features)
        self.siteFactory.features.append("calendar-access")
        rsrc = self.server.getResource(self.path)

        return rsrc.supportsCalDAV().addCallback(self.failUnless)
        
    def testSupportsCreateCalendar(self):
        self.siteFactory.options = list(self.siteFactory.options)
        self.siteFactory.options.append("MKCALENDAR")
        
        rsrc = self.server.getResource(self.path)

        return rsrc.supportsCreateCalendar().addCallback(self.failUnless)

    def testDoesntSupportsCreateCalendar(self):
        self.siteFactory.features = list(self.siteFactory.features)
        self.siteFactory.features.append("calendar-access")
        rsrc = self.server.getResource(self.path)

        return rsrc.supportsCreateCalendar().addCallback(self.failIf)

class CalDAVCollectionTestCase(WebDAVTestCase):
    localServer = True
    CALENDAR_HOME_NAME = 'calendar'

    class CalDAVResource(TestServerResource):
        render_MKCALENDAR = TestServerResource.renderFixedValues
        
    def _getResource(self):
        return self.server.getResource("%s%s/" % (self.path, \
                                             self.CALENDAR_HOME_NAME))

    def setUp(self):
        self.siteFactory = webdav_server.getTestSite()
        
        super(CalDAVCollectionTestCase, self).setUp()
        
        # Set up the resource on the server
        
        topLevelResource = self.siteFactory.resource.children['folder']
        self.serverResource = self.CalDAVResource(exists=True, isLeaf=False)
        topLevelResource.putChild(self.CALENDAR_HOME_NAME,
                                  self.serverResource)

    def testIsCalendar(self):
        self.serverResource.responseCode = 207
        self.serverResource.body = """<?xml version="1.0" encoding="UTF-8"?>
<D:multistatus xmlns:D="DAV:"
  xmlns="urn:ietf:params:xml:ns:caldav">
     <D:response>
       <D:href>/folder/calendar/</D:href>
       <D:propstat>
         <D:prop>
             <D:getetag>12345</D:getetag>
             <D:resourcetype><D:collection/><calendar/></D:resourcetype>
         </D:prop>
         <D:status>HTTP/1.1 200 OK</D:status>
       </D:propstat>
     </D:response>
   </D:multistatus>"""
        self.serverResource.render_PROPFIND = \
            self.serverResource.renderFixedValues
       
        return self._getResource().isCalendar().addCallback(self.failUnless)

    def testIsNotCalendar(self):
        return self._getResource().isCalendar().addCallback(self.failIf)

    def _checkCalendar(self, resource):
        path = resource.path
        self.failUnlessEqual(path, self._getResource().path + "hello/")
        
        return resource.isCalendar().addCallback(self.failUnless)

    def testCreateCalendar(self):
    
        # We have to set this on the class, because the CalDAVResource
        # object that gets instantiated corresponds to the non-existent
        # /folder/calendar/hello/ here
        self.CalDAVResource.responseCode = 201
       
        result = self._getResource().createCalendar("hello")
        result = result.addCallback(self._checkCalendar)
        
        return result

    def testCreateCalendar_200(self):
        # Some servers seem to generate a 200 OK response
        # to MKCALENDAR (instead of 201 Created); this test makes
        # sure this works.
        self.CalDAVResource.responseCode = 200
       
        result = self._getResource().createCalendar("hello")
        result = result.addCallback(self._checkCalendar)
        
        return result
        
class GetPrivilegesTestCase(WebDAVTestCase):
    localServer = True
    TEST_RESOURCE_NAME = 'privtest.moo'
    
    def _getResource(self):
        return self.server.getResource("%s%s" % (self.path,
                                                 self.TEST_RESOURCE_NAME))

        
    def setUp(self):
        self.siteFactory = webdav_server.getTestSite()
        
        super(GetPrivilegesTestCase, self).setUp()
        
        # Set up the resource on the server
        
        topLevelResource = self.siteFactory.resource.children['folder']
        self.serverResource = TestServerResource(exists=True, isLeaf=True)
        topLevelResource.putChild(self.TEST_RESOURCE_NAME,
                                  self.serverResource)
        self.serverResource.render_PROPFIND = self.serverResource.renderFixedValues
        self.serverResource.responseCode = 207
        self.serverResource.headers = {
            'content-type': 'text/xml; charset="utf-8"'
        }
    
    
    def testMultipleTickets(self):
        resource = self._getResource()
    
        self.serverResource.body = """<?xml version="1.0" encoding="UTF-8"?>
<D:multistatus xmlns:D="DAV:">
    <D:response>
        <D:href>http://localhost:9922%s</D:href>
        <D:propstat>
            <D:prop>
                <ticket:ticketdiscovery xmlns:ticket="http://www.xythos.com/namespaces/StorageServer">
                    <ticket:ticketinfo>
                        <ticket:id>wobbly-read-only-ticket</ticket:id>
                        <D:owner>
                            <D:href>https://osaf.us:443/cosmo/home/pbossut/</D:href>
                        </D:owner>
                        <ticket:timeout>Infinite</ticket:timeout>
                        <ticket:visits>infinity</ticket:visits>
                        <D:privilege>
                            <D:read/>
                        </D:privilege>
                    </ticket:ticketinfo>
                    <ticket:ticketinfo>
                        <ticket:id>woo-a-read-write-ticket</ticket:id>
                        <D:owner>
                            <D:href>http://localhost:9922%s</D:href>
                        </D:owner>
                        <ticket:timeout>Infinite</ticket:timeout>
                        <ticket:visits>infinity</ticket:visits>
                        <D:privilege>
                            <D:read/>
                            <D:write/>
                        </D:privilege>
                    </ticket:ticketinfo>
                </ticket:ticketdiscovery>
                <D:resourcetype>
                </D:resourcetype>
            </D:prop>
            <D:status>HTTP/1.1 200 OK</D:status>
        </D:propstat>
        <D:propstat>
            <D:prop>
                <D:getetag/>
                <D:current-user-privilege-set/>
            </D:prop>
            <D:status>HTTP/1.1 404 Not Found</D:status>
        </D:propstat>
    </D:response>
</D:multistatus>""" % (resource.path, resource.path, )

        def checkPrivileges(privs):
            self.failUnless(("read", "DAV:") in privs.privileges)
            self.failUnless(("write", "DAV:") in privs.privileges)

        deferred = resource.getPrivileges()
        deferred.addCallback(checkPrivileges)
        
        return deferred
        
    def testNoPrivileges(self):
        resource = self._getResource()
    
        self.serverResource.body = """<?xml version="1.0" encoding="UTF-8"?>
<D:multistatus xmlns:D="DAV:">
    <D:response>
        <D:href>http://localhost:9922%s</D:href>
        <D:propstat>
            <D:prop>
                <ticket:ticketdiscovery xmlns:ticket="http://www.xythos.com/namespaces/StorageServer"/>
                <D:getetag/>
                <D:current-user-privilege-set/>
            </D:prop>
            <D:status>HTTP/1.1 404 Not Found</D:status>
        </D:propstat>
    </D:response>
</D:multistatus>""" % (resource.path, )

        def checkPrivileges(privs):
            self.failIf(privs.privileges)

        deferred = resource.getPrivileges()
        deferred.addCallback(checkPrivileges)


class DisplayNameTestCase(WebDAVTestCase):
    localServer = True
    TEST_RESOURCE_NAME = 'test.txt'

    def _getResource(self):
        return self.server.getResource("%s%s" % (self.path,
                                                 self.TEST_RESOURCE_NAME))

    def setUp(self):
        self.siteFactory = webdav_server.getTestSite()
        
        super(DisplayNameTestCase, self).setUp()
        
        # Set up the resource on the server
        
        topLevelResource = self.siteFactory.resource.children['folder']
        self.serverResource = TestServerResource(exists=True, isLeaf=True)
        topLevelResource.putChild(self.TEST_RESOURCE_NAME,
                                  self.serverResource)
        
    def testDefault(self):
        resource = self._getResource()
        
        deferred = resource.getDisplayName()
        deferred.addCallback(lambda displayName:
                    self.failUnlessEqual(displayName, self.TEST_RESOURCE_NAME))
        return deferred

    def testSet(self):
        newName = u'\u201cQuote me?\u201d'
        resource = self._getResource()
        
        def checkServerValue(result):
            serverValue = self.serverResource.getProperty(PackElement('displayname'))
            self.failUnlessEqual(newName, serverValue)
            
        deferred = resource.setDisplayName(newName)
        deferred.addCallback(checkServerValue)
        
        return deferred

    def testSetWithProppatchResponse(self):
        newName = u'\u201cQuote me?\u201d'
        resource = self._getResource()

        self.serverResource.render_PROPPATCH = self.serverResource.renderFixedValues
        self.serverResource.responseCode = 207
        self.serverResource.headers = {
            'content-type': 'text/xml; charset="utf-8"'
        }
        self.serverResource.body = """<?xml version="1.0" encoding="UTF-8"?>
            <multistatus xmlns="DAV:">
                <response>
                  <href>http://localhost:9922%s</href>
                  <propstat>
                      <prop><displayname/></prop>
                      <status>HTTP/1.1 200 OK</status>
                  </propstat>
                </response>
            </multistatus>
        """ % (resource.path)

        
        def checkValue(result):
            self.failUnlessEqual(newName, resource._displayName)
            
        deferred = resource.setDisplayName(newName)
        deferred.addCallback(checkValue)
        
        return deferred
        
        
class ProppatchTestCase(WebDAVTestCase):
    localServer = True
    TEST_RESOURCE_NAME = 'test.txt'
    
    def _getResource(self):
        return self.server.getResource("%s%s" % (self.path,
                                                 self.TEST_RESOURCE_NAME))

        
    def setUp(self):
        self.siteFactory = webdav_server.getTestSite()
        
        super(ProppatchTestCase, self).setUp()
        
        # Set up the resource on the server
        
        topLevelResource = self.siteFactory.resource.children['folder']
        self.serverResource = TestServerResource(exists=True, isLeaf=True)
        topLevelResource.putChild(self.TEST_RESOURCE_NAME,
                                  self.serverResource)
    
    
    def testSimpleResponse(self):
        values = { PackElement('x'): None }
        
        result = self._getResource().proppatch(values)
        
        return result
        
class GetUriTestCase(unittest.TestCase):
    def test(self):
    
        serverHandle = ServerHandle("test.com", 80, useSSL=False)
        resource = serverHandle.getResource("/slide/files/")
        
        self.failUnlessEqual(resource.getUrl(),
                             "http://test.com/slide/files/")

    def testTicket(self):
        serverHandle = ServerHandle("test.com", 80, useSSL=False)
        resource = serverHandle.getResource("/slide/files/")
        resource.ticketId = '12_224'
        self.failUnlessEqual(resource.getUrl(),
                             "http://test.com/slide/files?ticket=12_224/")


    def testOtherPort(self):
        serverHandle = ServerHandle("test.com", 8080, useSSL=False)
        resource = serverHandle.getResource("/slide/files/")
        
        self.failUnlessEqual(resource.getUrl(),
                             "http://test.com:8080/slide/files/")

    def testHttps(self):
        serverHandle = ServerHandle("test.com", 443, useSSL=True)
        resource = serverHandle.getResource("/slide/files/")
        
        self.failUnlessEqual(resource.getUrl(),
                             "https://test.com/slide/files/")
                             
    def testQuoting(self):
        serverHandle = ServerHandle("test.com", 8080, useSSL=True)
        resource = serverHandle.getResource("/This should be quoted.html")
        
        self.failUnlessEqual(resource.getUrl(),
                             "https://test.com:8080/This%20should%20be%20quoted.html")
                             
class FreeBusyTestCase(WebDAVTestCase):
    TEMP_RSRC_NAME = "rsrc"
    localServer = True
    
    class FBResource(TestServerResource):
        render_REPORT = TestServerResource.renderFixedValues
        
    def setUp(self):
        super(FreeBusyTestCase, self).setUp()
        
        self.serverResource = self.FBResource(exists=True, isLeaf=True)
        
        topLevelResource = self.siteFactory.resource.children['folder']
        topLevelResource.putChild(self.TEMP_RSRC_NAME, self.serverResource)
        
        self.clientResource = self.server.getResource(
                                     "%s%s" % (self.path, self.TEMP_RSRC_NAME))


    def testFreeBusy(self):
        from datetime import datetime
        
        return self.clientResource.getFreebusy(
                datetime(2005, 12, 23, 14, 25),
                datetime(2006, 1, 11, 12, 3))


class DocTestCase(test_util.DocTestCase):
    import zanshin.webdav
    TEST_MODULE = zanshin.webdav
