# Copyright (c) 2005-2006 Open Source Applications Foundation.
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
__doc__ = """
This is a pretty basic in-memory twisted.web derived WebDAV server,
It has been implemented primarily for use in unit and regression tests.

It's good enough to run the zanshin's test_webdav module, but little more.
Unimplemented:

  - Any If- headers.
  - COPY (Right now, it just MOVEs)
  - DAV:liveprops in a PROPFIND
  
Probably never to be implemented:
  - LOCK
  - Any persistence between server invocations.
  
For testing purposes, you can execute the file from Python to get
a little test database.
"""

from twisted.internet import defer, reactor
import twisted.web.http as http
import twisted.web.server as server
import twisted.web.resource
import twisted.web.error as error

import time
import copy
import urllib, urlparse
import re

import zanshin.webdav as webdav
import zanshin.util as util

ElementTree = util.ElementTree

def datetimeToWebDAVString(msSinceEpoch=None):
    """Convert seconds since epoch to WebDAV datetime string."""
    if msSinceEpoch is None:
        msSinceEpoch = time.time()
        
    timeTuple = time.gmtime(msSinceEpoch)
    return "%4d-%02d-%02dT%02d:%02d:%02dZ" % timeTuple[:6]


class WebDAVChannel(http.HTTPChannel):
    def connectionLost(self, reason=None):
        http.HTTPChannel.connectionLost(self, reason)
        self.factory.serverConnectionLost(self)

class WebDAVSite(server.Site):
    """
    @ivar features: What to return in the DAV: header of an OPTIONS
        response.
    @type features: list of str

    @ivar options: The list of all possible options (i.e. what's returned
        from OPTIONS *. This list gets filtered when OPTIONS is called
        on a specific resource (e.g., you can't MKCOL an already existing
        resource)..
    @type options: list of str
    
    @ivar serverName: The string to report in the Server: header of returned
        responses.
    @type serverName: str

    """
    
    protocol = WebDAVChannel
    requestFactory = server.Request
    serverName = "zanshin test server (0.1)"
    runningProtocols = None

    features = ['1']
    options = ['OPTIONS', 'MKCOL', 'PUT', 'GET', 'DELETE', 'PROPFIND',
               'PROPPATCH', 'HEAD', 'COPY', 'MOVE']
    _lastETag = 0
    
    def newETag(self):
        """
        Override this to customize ETag generation. The current implementation
        just generates ETags for resources on the site sequentially.
        """
        self._lastETag += 1
        
        return str(self._lastETag)
        
    def __init__(self, resource=None):
        if resource is None:
            resource = WebDAVResource(exists=True, isLeaf=False)
            
        server.Site.__init__(self, resource)
        
    def getResourceFor(self, request):
        
        request.path = urlparse.urlsplit(request.uri)[2]
        
        request.prepath = []
        request.postpath = [server.unquote(pathElement)
                            for pathElement in request.path[1:].split('/')]

        result = server.Site.getResourceFor(self, request)
        
        return result
        
    def stopFactory(self):
        deferreds = [defer.maybeDeferred(server.Site.stopFactory, self)]
        
        if self.runningProtocols is not None:
            runningProtocols = self.runningProtocols
            self.runningProtocols = None
            
            for protocol in runningProtocols:
                if protocol.transport is not None:
                    deferreds += [defer.maybeDeferred(
                                     protocol.transport.loseConnection
                                 )]
        return defer.DeferredList(deferreds)
        
    def buildProtocol(self, addr):
        result = server.Site.buildProtocol(self, addr)
        
        if self.runningProtocols is None:
            self.runningProtocols = set([result])
        else:
            self.runningProtocols.add(result)

        return result
        
    def serverConnectionLost(self, protocol):
        if self.runningProtocols:
            try:
                self.runningProtocols.remove(protocol)
            except KeyError:
                pass


class _PropfindWriter(object):
    """
    Internal class that writes the <multistatus> xml in response to a
    PROPFIND request.
    """
    
    rootElement = None
    
    def processResourceUri(self, resource, uri):
        if self.rootElement is None:
            self.rootElement = ElementTree.Element(util.PackElement("multistatus"))

        response = ElementTree.SubElement(self.rootElement, 
                                          util.PackElement("response"))
        # Need to quote uri here?
        ElementTree.SubElement(response, util.PackElement("href")).text = uri
        
        self.processResource(resource, response)
        
    def processResource(self, resource, containerElement):
        pass
    
    def getOutput(self):
        """
        Builds and returns the output xml string (including <?xml ...?>.
        Once called, this resets is state.
        """
        
        output = ElementTree.tostring(self.rootElement, 'UTF-8')
        
        # Now, get rid of all internal state
        self.rootElement = None
        
        return output

    def _doPropAndValue(self, container, prop, value):
        
        result = ElementTree.SubElement(container, prop)

        if ElementTree.iselement(value):
            value = copy.deepcopy(value)
            result.append(value)
        elif value is not None:
            result.text = unicode(value)
            
        return result
        
        
    def processAllProp(self, rsrc, allprop):
        propstatElement = ElementTree.SubElement(allprop, util.PackElement("propstat"))
        propElement = ElementTree.SubElement(propstatElement, util.PackElement("prop"))

        statElement = ElementTree.SubElement(propstatElement, util.PackElement("status"))
        statElement.text = "HTTP/1.1 200 OK"

        for prop, value in rsrc.iterProperties():
            # Code for propfind with a bunch of properties
            
            # Now insert the props...
            self._doPropAndValue(propElement,  prop, value)

                
    def processPropname(self, rsrc, element):
        propstatElement = ElementTree.SubElement(xmlNode, util.PackElement("propstat"))
        propElement = ElementTree.SubElement(propstatElement, util.PackElement("prop"))

        for propAndValue in rsrc.iterProperties():
            self._doPropAndValue(propElement, propAndValue[0], None)

        statElement = ElementTree.SubElement(propstatElement, util.PackElement("status"))
        statElement.text = "HTTP/1.1 200 OK"
            
    def _newPropInPropStat(self, parent, status):
        propstatElement = ElementTree.SubElement(parent, util.PackElement("propstat"))
        propElement = ElementTree.SubElement(propstatElement, util.PackElement("prop"))

        statElement = ElementTree.SubElement(propstatElement, util.PackElement("status"))
        statElement.text = status

        return propElement

    def processRequestedProps(self, rsrc, xmlNode, requestedProps):
        foundProp = None
        notFoundProp = None # All the properties (strs) not present on this resource
        
        for prop in requestedProps:
            value = rsrc.getProperty(prop)
            
            if value is None:
                if notFoundProp is None:
                    notFoundProp = self._newPropInPropStat(
                        xmlNode, "HTTP/1.1 404 Not Found")
                propElement = notFoundProp
                
            else:
                if foundProp is None:
                    foundProp = self._newPropInPropStat(xmlNode,
                                                        "HTTP/1.1 200 OK")
                propElement = foundProp

            self._doPropAndValue(propElement, prop, value)

class WebDAVResource(twisted.web.resource.Resource):
    """
    This subclass of C{twisted.web.resource.Resource} implements
    a simple in-memory tree of WebDAV resources.
    
    @ivar exists: This resource actually exists. For example, if
          /x/ is a collection, and a client does a request
          for /x/y/z,/x/y/ and /x/y/z will have exists=False.
          This allows for correct handling of requests like
          PUT, MKCOL, MOVE, COPY, etc.
          
          Is rsrc.exists equivalent to rsrc being in rsrc.parent.children's
          values?

    @type exists: boolean
    
    @ivar parent: The parent of the given resource
    @type parent: WebDAVResource

    @ivar _data: The resource's data (i.e. what GET returns)
    @type _data: str
    
    @ivar _props: The WebDAV properties of the given resource. These
        should be accessed by the getProperty(), setProperty() and
        iterProperties() methods.
    @type _props: dict. Keys are strs, usually made with zanshin.util.PackElement.
    
    @ivar features: A list of DAV: features supported by this resource.
                    (If None, these are inherited from the C{WebDAVSite}).
    @type features: C{list} of C{str}

    """

    SPLITTER = re.compile(',\s*')

    exists = True
    parent = None
    _nsNum = 1
    features = None

    def __init__(self, exists=False, isLeaf=False, data=""):
        self._props = ElementTree.Element(util.PackElement("props"))
        self._data = data
        self.exists = exists
        self.isLeaf = isLeaf
        twisted.web.resource.Resource.__init__(self)
        
    def __getPropertyNode(self, propname):
        for child in self._props:
            if child.tag == propname:
                return child
        return None

    def __copyPropertyValue(self, propNode):
        for child in propNode:
            return copy.deepcopy(child)
                
        return propNode.text
    
    def setProperty(self, prop, value):
        elt = self.__getPropertyNode(prop)
        
        if elt is not None:
            self._props.remove(elt)
            
        
        if value is not None:
            elt = ElementTree.SubElement(self._props, prop)
            
            if ElementTree.iselement(value):
                elt.append(value) # deepcopy?
            elif isinstance(value, (str, unicode)):
                elt.text = value
            else:
                raise Exception, "Don't know how to insert a %s" % (type(value))
                
    def getProperty(self, propid):
        result = None
        elt = self.__getPropertyNode(propid)
        
        if elt is not None:
            result = self.__copyPropertyValue(elt)
            
        if result is None:
            if propid == util.PackElement("resourcetype"):
                if self.isLeaf:
                    result = ""
                else:
                    result = ElementTree.Element(util.PackElement("collection"))
            elif self.isLeaf and propid == util.PackElement("getcontentlength"):
                if self._data is None:
                    length = "0"
                else:
                    length = str(len(self._data))
                result = length
        return result

        
    def iterProperties(self):
        for node in self._props:
            yield (node.tag, self.__copyPropertyValue(node))

    def getChild(self, name, request):
        """
        This is called by Twisted when a request comes in, and
        self.children[name] is None. Our goal is to create a
        new resource, with isLeaf set appropriately, and
        exists set to False.
        """
        

        # A resource is a leaf (i.e. not a collection) iff there is
        # nothing else left in the path to process, and the path did
        # not end in /.
        isLeaf = (request.postpath == [] and request.prepath[-1:] != [''])
        
        if request.path == "*":
            result = self.__class__(exists=False, isLeaf=True)
            result.imAStar = None
        elif not name:
            # This happens when a request is received with a path
            # ending in /: when the last call to getChild() propagates
            # down the resource tree, name is passed in as "".
            result = self
        else:
            result = self.__class__(exists=False, isLeaf=isLeaf)
            result.parent = self
            
        return result
        
    def render(self, request):
        result = twisted.web.resource.Resource.render(self, request)
            
        request.setHeader('server', request.site.serverName)
            
        return result

        
    def _options(self, site):
        allOptions = []
        
        myOptions = getattr(self, "options", None)
        if myOptions is None:
            myOptions = site.options
            
        allOptions += myOptions
        invalidOptions = set([])
        
        if not hasattr(self, "imAStar"):
        
            parent = getattr(self, "parent", None)
            
            if parent is None or not self.exists:
                # The root resource
                invalidOptions.add('DELETE')
            
            if parent is None or not parent.exists or parent.isLeaf:
                invalidOptions.add('MKCOL')
                invalidOptions.add('PUT')
                    
                
            if not self.isLeaf or not self.exists:
                invalidOptions.add('GET')
                invalidOptions.add('HEAD')
                
            if not self.exists:
                invalidOptions.add('PROPFIND')
                #invalidOptions.add('PROPPATCH')
        
        for removeThisOption in invalidOptions:
            try:
                allOptions.remove(removeThisOption)
            except ValueError:
                pass
        
        return allOptions
        
    def render_OPTIONS(self, request):
        request.setHeader('Allow', ', '.join(self._options(request.site)))
        request.setResponseCode(http.OK)
        #request.setHeader('Content-Length', 0)
        
        features = self.features
        if features is None:
            features = request.channel.site.features
            
        if features:
            request.setHeader('MS-Author-Via', 'DAV')
            request.setHeader('DAV', ', '.join(features))
        
        return ''
    
    
    def render_GET(self, request):
        if not self.exists:
            page = error.NoResource(
                message="The resource %s was not found" % request.URLPath())
            
            return page.render(request)
        elif self.isLeaf:

            etag = str(self.getProperty(util.PackElement("getetag")))
            if not etag: 
                etag = request.site.newETag()
                self.setProperty(util.PackElement("getetag"), etag)
    
            request.setHeader('ETag', etag)
            
            contentType = str(
                    self.getProperty(util.PackElement("getcontenttype")))
            
            if etag:
                request.setETag(etag)
            if contentType:
                request.setHeader('content-type', contentType)
            
            if self._data is None:
                return ""
            else:
                return self._data

        else:
            return "<HTML>\n<BODY>\n" + \
            "Did you really want to GET a collection?\n" + \
            "</BODY>\n</HTML>\n"

    def render_MKCOL(self, request):
        if self.exists:
            page = error.ForbiddenResource(message="%s already exists" %
                request.URLPath())
            return page.render(request)
        else:
            parent = self.parent
            
            if not parent.exists:
                page = error.ErrorPage(
                    http.CONFLICT,
                    "Conflict",
                    "MKCOL Failed: The parent of %s doesn't exist" %
                      request.URLPath())
                return page.render(request)
            elif parent.isLeaf:
                page = error.ErrorPage(
                    http.CONFLICT,
                    "Conflict",
                    "The parent of %s is not a collection" %
                      request.URLPath())
                return page.render(request)
            else:
                self.isLeaf = False
                self.exists = True
                
                name = request.prepath[-1]
                
                if name == '':
                    name = request.prepath[-2]
                
                parent.putChild(name, self)
                
                request.setResponseCode(http.CREATED)
                request.setHeader('Content-Length', 0)
                return ''
                
    def render_DELETE(self, request):
        if not self.exists:
            page = error.NoResource(
                message="The resource %s was not found" % request.URLPath())
            return page.render(request)
            
        if not hasattr(self, "parent"):
            page = error.ErrorPage(
                http.CONFLICT,
                "Conflict",
                "Resource %s has no parent" % request.URLPath())
            return page.render(request)
        
        self.remove()
        
        request.setResponseCode(http.NO_CONTENT)
        request.setHeader('Content-Length', 0)
        return ''
        
    def render_PUT(self, request):
        parent = getattr(self, "parent", None)
        
        if parent is None:
            request.setHeader('Allow', ', '.join(self._options(request.site)))
            epage = error.ErrorPage(http.NOT_ALLOWED,
                            "Method Not Allowed",
                            "Can't PUT to %s" % (request.path))
            return epage.render(request)
            
        if not parent.exists:
            epage = error.ErrorPage(http.NOT_FOUND,
                            "Method Not Allowed",
                            "Parent of resource '%s' doesn't exist" % (
                                request.URLPath()))
            return epage.render(request)
        
        myEtag = self.getProperty(util.PackElement("getetag"))
        if myEtag is None and self.exists:
            myEtag = request.site.newETag()
            self.setProperty(util.PackElement("getetag"), myEtag)
        if myEtag is not None:
            myEtag = myEtag.encode('utf-8')

        conflictMsg = None
        matchHeaders = request.getHeader('If-Match')
        if matchHeaders:
            matchHeaders = self.SPLITTER.split(matchHeaders)
        
            for etag in matchHeaders:
                if '*' != etag:
                    if myEtag != etag:
                        conflictMsg = "If-Match ETag '%s' doesn't match %s" % (
                            etag, myEtag)
                        break
                else:
                    if myEtag is None:
                        conflictMsg = "If-Match ETag '*' doesn't match non-existent resource"
                        break

        if conflictMsg is None:
            notMatchHeaders = request.getHeader('If-None-Match')
            if notMatchHeaders:
                notMatchHeaders = self.SPLITTER.split(notMatchHeaders)
                
                for etag in notMatchHeaders:
                    if '*' != etag:
                        if myEtag == etag:
                            conflictMsg = "If-None-Match ETag '%s' matches %s" % (
                                            etag, myEtag)
                            break
                    else:
                        if myEtag is not None:
                            conflictMsg = "If-None-Match ETag is '*', but resource exists"
                            break
                            
        if conflictMsg is not None:
            epage = error.ErrorPage(http.PRECONDITION_FAILED,
                            None,
                            conflictMsg)
            return epage.render(request)
        
        # @@@ [grant] Last-Modified support goes here
        now = datetimeToWebDAVString()

        self.isLeaf = True
        
        if not self.exists:
            self.exists = True
                
            name = str(request.URLPath())
                
            if name[-1] == "/":
                name = name[:-1]
            name = name.split("/")[-1]
                
            self.setProperty(util.PackElement("creationdate"), now)
            self.parent.putChild(name, self)
                
            request.setResponseCode(http.CREATED)
        else:
            request.setResponseCode(http.NO_CONTENT)
        
        self._data = request.content.read()
        
        # Update Last-Modified
        self.setProperty(util.PackElement("getlastmodified"), now)

        # Make a new ETag, since we updated the resource.
        etag = request.site.newETag()
        self.setProperty(util.PackElement("getetag"), etag)
        request.setHeader('ETag', etag)
        
        return ''
        
    def _iterateChildren(self, depth, uri):
        thisGeneration = [(self, uri)]
        nextGeneration = []
        
        while len(thisGeneration) > 0:

            if depth is not None:
                depth -= 1

            for (current, uri) in thisGeneration:
            
                if not current.isLeaf and uri[-1] != '/':
                    uri = uri + "/"
    
                yield (current, uri)
            
                if (depth is None or depth >= 0):
                    for (name, child) in current.children.iteritems():
                        nextGeneration.append((child, uri + urllib.quote(name)))
                    
            thisGeneration = nextGeneration
            nextGeneration = []
        
    
    def _getPropXmlWriter(self, xmlData):
        writer = _PropfindWriter()

        if not xmlData:
            writer.processResource = writer.processAllProp
            return writer

        try:
            propfindNode = ElementTree.XML(xmlData)
        except:
            import pdb; pdb.set_trace()

        if propfindNode is None:
            raise Exception, "No <DAV:propfind> element"

        if propfindNode.tag !=  util.PackElement("propfind"):
            raise Exception, "Expected a <DAV:propfind> element, got %s" % (
                                propfindNode.tag, )
        
        processResource = None
        
        for node in propfindNode:
            tag = node.tag
            
            if tag == util.PackElement("prop"):
                requestedProps = [childNode.tag for childNode in node]
                processResource = lambda rsrc, parent: (
                    writer.processRequestedProps(rsrc, parent, requestedProps))
            elif tag == util.PackElement("allprop"):
                processResource = writer.processAllProp
            elif tag == util.PackElement("propname"):
                processResource = writer.processPropname
            # Should do live-props
                
        if processResource is None:
            raise Exception, "Unknown <DAV:propfind> contents"
            
        writer.processResource = processResource


        return writer

    

    def render_PROPFIND(self, request):
    
        data = request.content.read()

        # @@@ [grant] Should check "infinity"
        try:
            depth = int(request.getHeader('depth'))
            assert(depth >= 0)
        except:
            depth = None
            

        if not self.exists:
            page = error.NoResource(
                message="The resource %s was not found" % request.URLPath())
            
            return page.render(request)
            

        #  PROPFIND of a collection whose uri doesn't end in / should
        # be redirected to the more correctly named version 
        if not self.isLeaf and request.prepath[-1] != '':
            request.setResponseCode(http.FOUND)
            request.setHeader('Location', str(request.URLPath()) + '/')
            return ''
            
        try:
            xmlWriter = self._getPropXmlWriter(data)
        except TypeError, xmlError:
            epage = error.ErrorPage(http.BAD_REQUEST,
                            "Bad Request",
                            "Failed to parse request body: %s" % (xmlError))
            return epage.render(request)
    
        
        request.setResponseCode(http.MULTI_STATUS)
        request.setHeader('Content-Type', webdav.XML_CONTENT_TYPE)

        startUri = request.URLPath().path
        for (rsrc, uri) in self._iterateChildren(depth, startUri):
            xmlWriter.processResourceUri(rsrc, uri)
            
        return xmlWriter.getOutput()
        
    def render_PROPPATCH(self, request):
        xmlData = request.content.read()

        if not self.exists:
            page = error.NoResource(
                message="The resource %s was not found" % request.URLPath())
            
            return page.render(request)
            

        #  PROPPATCH of a collection whose uri doesn't end in / should
        # be redirected to the more correctly named version 
        if not self.isLeaf and request.prepath[-1] != '':
            request.setResponseCode(http.FOUND)
            request.setHeader('Location', str(request.URLPath()) + '/')
            return ''
            
        try:
            doc = ElementTree.XML(xmlData)
        except TypeError, e:
            epage = error.ErrorPage(http.BAD_REQUEST,
                            "Bad Request",
                            "Failed to parse request body: %s" % (e))
            return epage.render(request)
            
        setElements = []
        removeElements = []
        
        if doc.tag != util.PackElement("propertyupdate"):
            epage = error.ErrorPage(http.BAD_REQUEST,
                            "Request body wasn't a DAV:propertyupdate")
            return epage.render(request)

        for node in doc:
            tag = node.tag
            
            if tag == util.PackElement("remove"):
                appendList = removeElements
            elif tag == util.PackElement("set"):
                appendList = setElements
            else:
                appendList = None
                
            if appendList is not None:
                for child in node:
                    if util.PackElement("prop") == child.tag:
                        
                        appendList.extend(list(child))
                                
        for e in setElements:
            element = self.__getPropertyNode(util.PackElement(e.tag))
            
            # Remove the existing property, so we don't
            # end up with duplicates!
            if element is not None:
                self._props.remove(element)
                
            self._props.append(copy.deepcopy(e))
            
        for e in removeElements:
            element = self.__getPropertyNode(util.PackElement(e.tag))

            if element is not None:
                self._props.remove(element)

        request.setResponseCode(http.OK)
        return ''


    def _doMoveOrCopy(self, request, preserveOriginal):
        if not self.exists:
            page = error.NoResource(
                message="The resource %s was not found" % request.URLPath())
            
            return page.render(request)

        destinationUri = request.getHeader('destination')
        
        if not destinationUri:
            page = error.ErrorPage(http.BAD_REQUEST,
                    "Bad Request",
                    "Missing Destination header")
            return page.render(request)

        if "?" in destinationUri:
            page = error.ErrorPage(http.BAD_REQUEST,
                    "Bad Request",
                    "Destination '%s' cannot include a query string" % (
                       destinationUri))
            return page.render(request)

        
        depth = request.getHeader('depth')
        if depth is not None:
            if self.isLeaf and depth != "0":
                page = error.ErrorPage(http.BAD_REQUEST,
                        "Bad Request",
                        "Invalid Depth header '%s'" % (depth))
                return page.render(request)
            elif not self.isLeaf and depth.lower() != "infinity":
                page = error.ErrorPage(http.BAD_REQUEST,
                        "Bad Request",
                        "Invalid Depth header '%s'" % (depth))
                        
        # @@@ [grant] Gross, but tree-walking
        fakeRequest = copy.copy(request)
        fakeRequest.uri = destinationUri
        
        # @@@ [grant] Should check host, etc, and fail if
        # it doesn't match
        fakeRequest.path = util.parseConfigFromUrl(fakeRequest.uri)[5]
        
        
        fakeRequest.prepath = []
        fakeRequest.postpath = [server.unquote(pathElement) for pathElement in 
                                fakeRequest.path[1:].split('/')]
        
        destResource = request.site.getResourceFor(fakeRequest)
        
        # Make sure we're not doing something very
        # wacky, like moving something onto an
        # ancestor.
        tmpResource = destResource
        while tmpResource is not None:
            if tmpResource is self:
                page = error.ErrorPage(http.FORBIDDEN,
                    "Forbidden",
                    "Can't copy '%s' to '%s'" % (
                       request.path, fakeRequest.path))
                       
                return page.render(request)
            tmpResource = tmpResource.parent
                    
        newParent = destResource.parent
        if newParent is None or not newParent.exists:
            page = error.ErrorPage(http.CONFLICT,
                "Conflict",
                "The parent of '%s' does not exist" % (
                   destinationUri))
                   
            return page.render(request)
            
        if destResource.exists:
            overwrite = request.getHeader("overwrite")
            
            if overwrite is not None and overwrite.lower() == "f":
                page = error.ErrorPage(http.PRECONDITION_FAILED,
                    "Precondition Failed",
                    "Refusing to overwrite '%s'" % (
                       destResource.path))
                return page.render(request)
                
            request.setResponseCode(http.NO_CONTENT)
        else:
            request.setResponseCode(http.OK)
            
        if preserveOriginal:
            # Need a deep copy of the original resource
            print "Eek: I haven't implemented COPY yet!"
        else:
            name = fakeRequest.prepath[-1]
            if name == '':
                name = fakeRequest.prepath[-2]
                
            self.remove()
            newParent.putChild(name, self)

        return ''




        
    def render_MOVE(self, request):
        return self._doMoveOrCopy(request, False)

    def render_COPY(self, request):
        return self._doMoveOrCopy(request, True)


    def putChild(self, name, child):
        child.parent = self
        
        now = datetimeToWebDAVString()
        
        self.setProperty(util.PackElement("getlastmodified"), now)
        child.setProperty(util.PackElement("getlastmodified"), now)
        
        if child.getProperty(util.PackElement("creationdate")) is None:
            child.setProperty(util.PackElement("creationdate"), now)
    
        return twisted.web.resource.Resource.putChild(self, name, child)
        
    def remove(self):
        parent = self.parent
        
        if parent is not None:
            myName = None
            for (name, value) in self.parent.children.iteritems():
                if value is self:
                    myName = name
        
            if myName is not None:
                del self.parent.children[myName]
            
        self.parent = None

def getTestSite():
    rootResource = WebDAVResource(exists=True, isLeaf=False)
    rootResource.features = [] # i.e. root doesn't support WebDAV
    rootResource.options = ['OPTIONS', 'GET', 'HEAD']
    
    fileResource = WebDAVResource(exists=True, isLeaf=True,
                                  data="Hello, world!\n")
    fileResource.setProperty(util.PackElement("getcontenttype"), 'text/plain')
    fileResource.setProperty(util.PackElement("getetag"), '2')
    
    rootResource.putChild('aFile', fileResource)
    
    collectionResource = WebDAVResource(exists=True, isLeaf=False)
    rootResource.putChild('folder', collectionResource)
    
    return WebDAVSite(rootResource)


if __name__ == "__main__":
    reactor.listenTCP(8081, getTestSite())
    reactor.run()
