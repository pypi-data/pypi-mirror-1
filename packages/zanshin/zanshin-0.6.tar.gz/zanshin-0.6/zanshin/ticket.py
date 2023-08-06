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
#
__doc__ = """
Support for WebDAV tickets, a lightweight access control
mechanism (but less secure than WebDAV ACL). The aim  is to allow sharing of
WebDAV resources without requiring sharees to have an account on the server.

For more information, see the (expired)
U{ticket internet draft<http://www.sharemation.com/%7Emilele/public/dav/draft-ito-dav-ticket-00.txt>}.

The main use cases are:

    1. Requesting a ticket, i.e. creating a ticket for a resource on a
       WebDAV server that supports tickets: Create a new L{Ticket} object,
       specifying the C{readonly}-ness you want. The
       L{Resource.createTicket()<zanshin.webdav.Resource.createTicket>} method
       can then be used to create the ticket on the server; on success that
       method will fill in your L{Ticket}'s instance variables.
       
   2. Finding out the tickets you've created for a given resource. To do that,
      call L{Resource.getTickets()<zanshin.webdav.Resource.getTickets>}.
      
   3. Accessing a resource by ticket. A ticket's identifier is just a string,
      usually specified as a parameter of the resource's URL. If you set a
      L{Resource<zanshin.webdav.Resource>}'s
      L{ticketId<zanshin.webdav.Resource.ticketId>} instance variable, that id
      will be used in future requests for that resource (and its children).
      
   4. Deleting a ticket from the server: Use the
      L{Resource.deleteTicket()<zanshin.webdav.Resource.deleteTicket>} method.

"""

from zanshin.util import ElementTree, PackElement, UnpackElement

class Ticket(object):
    """
    A C{Ticket} encapsulates a single ticket on a WebDAV server.
    
    @cvar TICKET_NAMESPACE: The XML namespace URI.  This URI is NOT specified in
        the U{ticket internet draft<http://www.sharemation.com/%7Emilele/public/dav/draft-ito-dav-ticket-00.txt>},
        see U{this link<http://wiki.osafoundation.org/bin/view/Projects/CosmoTickets#Deviations%20from%20Spec>}
        for a list of deviations from the spec.
    @type TICKET_NAMESPACE: C{str}
    
    @ivar read: Does the ticket grant read privileges?
    @type read: C{boolean}

    @ivar write: Does the ticket grant read privileges?
    @type write: C{boolean}

    @ivar timeoutSeconds: When does the ticket expire (in seconds)? Set to
        C{None} for no expiration.
    @type timeoutSeconds: numeric (C{float} or C{int})
    
    @ivar visits: How many distinct uses does this ticket allow? Set to
        C{None} for no restriction.
    @type visits: C{int}
    
    @ivar ownerUri: URI specifying the owner; may be C{None} in the
                    case when a ticket is being requested.
    @type ownerUri: str
    
    @ivar ticketId: The ID of the ticket; may be C{None} in the
                    case when a ticket is being requested.
    @type ticketId: C{str}
    """
    
    TICKET_NAMESPACE = "http://www.xythos.com/namespaces/StorageServer"

    ownerUri = None
    ticketId = None
    
    def __init__(self, read=True, write=False, timeoutSeconds=None, visits=None,
                 **kwargs):
        """
        @param read: Initial value for the C{read} instance variable.
        @type read: C{boolean}

        @param write: Initial value for the C{write} instance variable.
        @type write: C{boolean}
        
        @param timeoutSeconds: Initial value for the C{timeoutSeconds} instance
            variable. Pass C{None} for an infinite timeout.
        @type timeoutSeconds: Numeric
        
        @param visits: Initial value for the C{visits} instance variable.
        @type visits: C{int}
        
        Additional ticket types can be passed in as keyword arguments.
        
        >>> ticket = Ticket(write=True)
        >>> ticket.read
        True
        >>> ticket.write
        True
        >>> print ticket.timeoutSeconds
        None
        >>> print ticket.visits
        None
        """
    
        super(Ticket, self).__init__()
        
        self.privileges = dict(read=read, write=write)
        self.privileges.update(kwargs)
        
        self.timeoutSeconds = timeoutSeconds
        self.visits = visits
        
    def getPrivilege(self, name):
        return self.privileges.get(name)

    def setPrivilege(self, name, value):
        self.privilege[name] = value
    
    def makeProperty(name):
        def get(self): return self.privileges.get(name)
        def set(self, value): self.privilege[name] = value
        return property(get, set)

    read  = makeProperty('read')
    write = makeProperty('write')

    @classmethod
    def parse(cls, element):
        """
        Given an C{ElementTree.Element} object specifying a DAV:ticket
        node, returns a Ticket object
        
        >>> xml = \"\"\"<?xml version="1.0" encoding="utf-8" ?>
        ... <t:ticketinfo xmlns:D="DAV:" xmlns:t="http://www.xythos.com/namespaces/StorageServer">
        ...  <t:id>A658B29924F9D39C</t:id>
        ...  <D:owner>
        ...    <D:href>http://www.foo.com/users/testuser</D:href>
        ...  </D:owner>
        ...  <t:visits>1</t:visits>
        ...  <t:timeout>Second-3600</t:timeout>
        ...  <D:privilege>
        ...    <D:read/>
        ...    <D:freebusy/>
        ...  </D:privilege>']
        ... </t:ticketinfo>
        ... \"\"\"
        >>> ticketNode= ElementTree.XML(xml)
        >>> ticket = Ticket.parse(ticketNode)
        >>> ticket.read
        True
        >>> ticket.write
        False
        >>> ticket.getPrivilege('freebusy')
        True
        >>> ticket.ticketId
        'A658B29924F9D39C'
        >>> ticket.visits
        1
        >>> ticket.timeoutSeconds
        3600
        >>> ticket.ownerUri
        'http://www.foo.com/users/testuser'
        """
        
        visits = None
        timeoutSeconds = None
        privileges = []        
        
        ownerUri = None
        ticketId = None
        
        if not element.tag in (PackElement("ticket", cls.TICKET_NAMESPACE),
                               PackElement("ticketinfo", cls.TICKET_NAMESPACE)):
            raise ValueError, "Invalid XML node: expected ticketinfo"

        for childElement in element:
            
            # The only nodes we understand are in DAV:. We're
            # going to ignore all the nodes we don't understand
            # (since in theory these could be some kind of
            # DAV extension)
            
            childTag = childElement.tag
            
            if childTag == PackElement("id", cls.TICKET_NAMESPACE):
                ticketId = childElement.text.encode('us-ascii')
            elif childTag == PackElement("timeout", cls.TICKET_NAMESPACE):
                timeoutStr = childElement.text
                    
                if timeoutStr[:len('Second-')] == 'Second-':
                    timeoutSeconds = int(timeoutStr[len('Second-'):])
                elif timeoutStr != "Infinite":
                    raise ValueError, \
                        "Unexpected timeout value '%s'" % (timeoutStr)
                    
            elif childTag == PackElement("visits", cls.TICKET_NAMESPACE):
                    visitsStr = childElement.text
                    if visitsStr != "infinity":
                        visits = int(visitsStr)
            elif childTag == PackElement("owner"): # "DAV:" namespace
                for ownerNode in childElement:
                    if ownerNode.tag == PackElement("href"):
                        ownerUri = ownerNode.text
            elif childTag == PackElement("privilege"):
                for privNode in childElement:
                    val = UnpackElement(privNode.tag)[0]
                    # if val is None, the child wasn't in the DAV: namespace,
                    # ignore it.
                    if val is not None:
                        privileges.append(val)
        
        # Ticket's constructor defaults to read=True, don't do that when
        # parsing, you might have a ticket like freebusy that doesn't include
        # the read privilege
        privDict = {'read' : False}
        for priv in privileges:
            privDict[priv] = True

        res = cls(visits=visits, timeoutSeconds=timeoutSeconds, **privDict)
        
        res.ownerUri = ownerUri
        res.ticketId = ticketId

        return res
        
    def __str__(self):
        ticketElement = ElementTree.Element(
            PackElement("ticketinfo", self.__class__.TICKET_NAMESPACE))

        privElement = ElementTree.SubElement(ticketElement, PackElement("privilege"))

        for priv, val in self.privileges.iteritems():
            if val:
                ElementTree.SubElement(privElement, PackElement(priv))

        timeoutElement = ElementTree.SubElement(
            ticketElement, PackElement("timeout", self.__class__.TICKET_NAMESPACE))
        if self.timeoutSeconds is not None:
            timeoutElement.text = "Seconds-" + str(self.timeoutSeconds)
        else:
            timeoutElement.text = "Infinite"
            
        visitsElement = ElementTree.SubElement(
            ticketElement, PackElement("visits", self.__class__.TICKET_NAMESPACE))
        
        if self.visits is not None:
            visitsElement.text = str(self.visits)
        else:
            visitsElement.text = "infinity"
            
        if self.ownerUri is not None:
            owner = ElementTree.SubElement(ticketElement, PackElement("owner"))
            href = ElementTree.SubElement(owner, PackElement("href"))
            href.text = unicode(self.ownerUri)

        if self.ticketId is not None:
            ticketId = ElementTree.SubElement(ticketElement, PackElement("id"))
            ticketId.text = self.ticketId
        
        return ElementTree.tostring(ticketElement, 'UTF-8')


def getTicketInfoNodes(body):
    """
    Given a string, return the list of all ticketinfo ElementTree nodes found.    
    """
    root = ElementTree.XML(body)
    ticketInfoNodes = []
    for node in root.getiterator(PackElement("ticketinfo",
                                             Ticket.TICKET_NAMESPACE)):
        ticketInfoNodes.append(node)
    
    return ticketInfoNodes
