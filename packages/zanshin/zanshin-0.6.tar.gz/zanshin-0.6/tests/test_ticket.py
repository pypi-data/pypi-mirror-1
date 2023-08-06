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
# Tests for the zanshin.Ticket class

from twisted.trial import unittest
from zanshin.util import ElementTree
from zanshin.ticket import Ticket

class TicketParseTestCase(unittest.TestCase):
    """Tests of zanshin.Ticket.parse()"""
    
    def _parseTicket(self, string):
        # Utility method that turns an XML string
        # into an ElementTree.Element...
        element = ElementTree.XML(string)

        # ... and then parses that.
        return Ticket.parse(element)

    def testTicket(self):
        # Test that ticket XML with a top-level element named "ticket"
        # instead of "ticketinfo" parses correctly. (Currently, Xythos uses
        # the former, while cosmo -- more logically, IMHO -- uses the latter).
        # This is something that should be ironed out with the new ticket I-D.
        
        ticket = self._parseTicket(
"""<?xml version="1.0" encoding="utf-8" ?>
<t:ticket xmlns:D="DAV:" xmlns:t="http://www.xythos.com/namespaces/StorageServer">
  <t:id>A658B29924F9D39C</t:id>
  <D:owner>
    <D:href>http://www.foo.com/users/testuser</D:href>
  </D:owner>
  <t:visits>1</t:visits>
  <t:timeout>Second-3600</t:timeout>
  <D:privilege>
    <D:read/>
  </D:privilege>']
</t:ticket>
""")
        self.failUnless(isinstance(ticket, Ticket))
        self.failUnlessEqual(ticket.ticketId, 'A658B29924F9D39C')
        self.failUnlessEqual(ticket.ownerUri, 'http://www.foo.com/users/testuser')
        self.failUnlessEqual(ticket.timeoutSeconds, 3600)
        self.failUnlessEqual(ticket.visits, 1)
        self.failUnless(ticket.read)
        
    def testBadTimeout(self):
        # Test that parsing ticket XML with a badly formed <timeout> element
        # raises a ValueError.
        self.assertRaises(
            ValueError,
            self._parseTicket,
            """<?xml version="1.0" encoding="utf-8" ?>
            <t:ticketinfo xmlns:D="DAV:" xmlns:t="http://www.xythos.com/namespaces/StorageServer">
              <t:id>A658B29924F9D39C</t:id>
              <D:owner>
                <D:href>http://www.foo.com/users/testuser</D:href>
              </D:owner>
              <t:visits>1</t:visits>
              <t:timeout>3600</t:timeout>
              <D:privilege>
                <D:read/>
              </D:privilege>']
            </t:ticketinfo>
            """)

    def testInfiniteTimeout(self):
        # Test that a <timeout> value of "Infinite" is handled correctly
        ticket = self._parseTicket(
            """<?xml version="1.0" encoding="utf-8" ?>
            <t:ticketinfo xmlns:D="DAV:" xmlns:t="http://www.xythos.com/namespaces/StorageServer">
              <t:id>A658B29924F9D39C</t:id>
              <D:owner>
                <D:href>http://www.foo.com/users/testuser</D:href>
              </D:owner>
              <t:visits>10</t:visits>
              <t:timeout>Infinite</t:timeout>
              <D:privilege>
                <D:read/>
              </D:privilege>']
            </t:ticketinfo>
            """)
        self.failUnlessEqual(ticket.timeoutSeconds, None)

    def testBadVisits(self):
        # Test that parsing ticket XML with a badly formed <visits> element
        # raises a ValueError.
        self.assertRaises(
            ValueError,
            self._parseTicket,
            """<?xml version="1.0" encoding="utf-8" ?>
            <t:ticketinfo xmlns:D="DAV:" xmlns:t="http://www.xythos.com/namespaces/StorageServer">
              <t:id>A658B29924F9D39C</t:id>
              <D:owner>
                <D:href>http://www.foo.com/users/testuser</D:href>
              </D:owner>
              <t:visits>x</t:visits>
              <t:timeout>Second-3600</t:timeout>
              <D:privilege>
                <D:read/>
              </D:privilege>']
            </t:ticketinfo>
            """)

    def testInfinityVisits(self):
        # Test that a <visits> value of "infinity" is handled correctly
        ticket = self._parseTicket(
            """<?xml version="1.0" encoding="utf-8" ?>
            <t:ticketinfo xmlns:D="DAV:" xmlns:t="http://www.xythos.com/namespaces/StorageServer">
              <t:id>A658B29924F9D39C</t:id>
              <D:owner>
                <D:href>http://www.foo.com/users/testuser</D:href>
              </D:owner>
              <t:visits>infinity</t:visits>
              <t:timeout>Second-3600</t:timeout>
              <D:privilege>
                <D:read/>
              </D:privilege>']
            </t:ticketinfo>
            """)
        self.failUnlessEqual(ticket.visits, None)

    def testUnknownPrivilege(self):
        # Test that parsing ticket XML with a extra elements under
        # privileges can be parsed (with the unknown elements being
        # ignored).
        ticket = self._parseTicket(
            """<?xml version="1.0" encoding="utf-8" ?>
            <t:ticketinfo xmlns:D="DAV:" xmlns:t="http://www.xythos.com/namespaces/StorageServer">
              <t:id>A658B29924F9D39C</t:id>
              <D:owner>
                <D:href>http://www.foo.com/users/testuser</D:href>
              </D:owner>
              <t:timeout>Second-3600</t:timeout>
              <D:privilege>
                <D:read/>
                <D:inherit/>
                <D:write/>
              </D:privilege>']
            </t:ticketinfo>
            """)
        self.failUnless(isinstance(ticket, Ticket))
        self.failUnless(ticket.read)
        self.failUnless(ticket.write)
        self.failUnlessEqual(ticket.ticketId, 'A658B29924F9D39C')
        self.failUnlessEqual(ticket.ownerUri, 'http://www.foo.com/users/testuser')
        self.failUnlessEqual(ticket.timeoutSeconds, 3600)
        self.failUnlessEqual(ticket.visits, None)

    def testUnknownElement(self):
        # Test that parsing XML whose top-level element is not
        # "ticket" or "ticketinfo" raises a ValueError.
        # (This test actually uses a top-level element of
        # ("DAV:", "ticketinfo")).
        self.assertRaises(
            ValueError,
            self._parseTicket,
            """<?xml version="1.0" encoding="utf-8" ?>
            <D:ticketinfo xmlns:D="DAV:">
              <D:id>A658B29924F9D39C</D:id>
              <D:owner>
                <D:href>http://www.foo.com/users/testuser</D:href>
              </D:owner>
              <D:timeout>Second-3600</D:timeout>
              <D:privilege>
                <D:read/>
                <D:inherit/>
                <D:write/>
              </D:privilege>']
            </D:ticketinfo>
            """)

import test_util

class DocTestCase(test_util.DocTestCase):
    import zanshin.ticket
    TEST_MODULE = zanshin.ticket

