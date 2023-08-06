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
"""
The C{zanshin.acl} module provides classes to model WebDAV access control,
and convert instances to and from an XML representation.
    
REFERENCES:
===========

    - U{WebDAV Access Control<http://www.ietf.org/rfc/rfc3744.txt>} (RFC 3744)
                 
TODO:
=====
   - Higher level API:
      - pythonic (raise exceptions on errors, return python objects
        instead of XML etc.)
      - combine WebDAV operations into one call, for example
        when setting ACL we should lock resource
      - add a higher level API to modify ACLs (currently only get and set)
      - read and understand server mappings for ACL, and respond to requests
        in a smart way - for example, you might want to set read access,
        but there is no explicit read: rather it consists of finer-grained
        properties. It would be good to be able to
        detect and set these automatically.

BUGS:
=====
    - DAV: namespace prefix hardcoded to D
    - privileges and namespaces show in the reverse order they are added
    - manually mapping some namespaces to ns-[0-9]+ prefixes will break
      things
    - serializing ACEs without going through ACL does not map the namespace
      prefixes correctly between grant and deny lists
    - only ACL serialization outputs namespace declarations (so the only
      way to use serialize anything is really by serializing ACLs only)

"""

import zanshin.util
ElementTree = zanshin.util.ElementTree

def _utf8Str(obj):
    return unicode(obj).encode('utf-8')


class ACE(object):
    """
    Access Control Entry consists of all the deny and grant rules for a
    principal. An ACE defines the complete access control definition for a
    single principal.
    """
    def __init__(self, principal, deny=(), grant=()):
        """
        @param principal: Principal name (in DAV: namespace) or URL.
        @param deny:      Tuple of privilege name and privilege namespace
        @param grant:     Tuple of privilege name and privilege namespace
        """
        self._principal = _Principal(principal)
        self._deny  = _Deny(deny)
        self._grant = _Grant(grant)

        """
        The protected flag is true for ACEs that can not be changed.
        """
        self.protected = False

    def deny(self, privilege, namespace='DAV:'):
        """
        Deny a privilege. In effect this adds a privilege to the deny
        list.
        """
        self._deny.add(privilege, namespace)

    def grant(self, privilege, namespace='DAV:'):
        """
        Grant a privilege. In effect this adds a privilege to the grant
        list.
        """
        self._grant.add(privilege, namespace)

    def removeDeny(self, privilege, namespace='DAV:'):
        """
        Remove a privilege from the deny list.
        """
        self._deny.remove(privilege, namespace)

    def removeGrant(self, privilege, namespace='DAV:'):
        """
        Remove a privilege from the grant list.
        """
        self._grant.remove(privilege, namespace)

    def denyList(self):
        """
        Get the list of lists [denyPrivilege, namespace].
        """
        return self._deny.privileges.keys()

    def grantList(self):
        """
        Get the list of lists [grantPrivilege, namespace].
        """
        return self._grant.privileges.keys()

    def __str__(self):
        if self.protected:
            return ''
        else:
            return '<D:ace>%s%s%s</D:ace>\n' %(_utf8Str(self._principal),
                                             _utf8Str(self._deny),
                                             _utf8Str(self._grant))


class ACL(object):
    """
    An Access Control List (ACL) consists of one of more ACEs. ACL defines all
    the access control definitions for a single resource.
    
    One could construct an ACL object like this, starting with ACE:
    
    >>> allACE = ACE(principal='all', deny=(), grant=('read', 'DAV:'))
    >>> allACE.grant('write', 'http://www.xythos.com/namespaces/StorageServer/acl/')
    >>> print allACE
    <D:ace>
    <D:principal><D:all/></D:principal>
    <D:grant>
    <D:privilege><ns-1:write/></D:privilege>
    <D:privilege><D:read/></D:privilege>
    </D:grant>
    </D:ace>
    <BLANKLINE>
    
    Then creating the actual ACL by passing in the ACE:
        
    >>> aclObj = ACL(acl=[allACE])
    >>> print aclObj
    <D:acl xmlns:ns-1="http://www.xythos.com/namespaces/StorageServer/acl/" xmlns:D="DAV:">
    <D:ace>
    <D:principal><D:all/></D:principal>
    <D:grant>
    <D:privilege><ns-1:write/></D:privilege>
    <D:privilege><D:read/></D:privilege>
    </D:grant>
    </D:ace>
    </D:acl>
    
    Let's play with the ACE object some more:
    
    >>> allACE.deny('yawn', 'http://www.example.com/namespaces/acl/')
    >>> print allACE._deny.privileges.keys()
    [('yawn', 'http://www.example.com/namespaces/acl/')]
    >>> allACE.deny('yawn', 'http://www.example.com/namespaces/fooledya/acl/')
    >>> print allACE._grant.privileges
    {('write', 'http://www.xythos.com/namespaces/StorageServer/acl/'): 'ns-1', ('read', 'DAV:'): 'D'}
    >>> allACE.protected = True
    >>> print allACE
    <BLANKLINE>
    >>> allACE.protected = False
    >>> allACE.removeDeny('yawn', 'http://www.example.com/namespaces/fooledya/acl/')
    >>> allACE.removeDeny('yawn', 'http://www.example.com/namespaces/acl/')
    >>> print allACE
    <D:ace>
    <D:principal><D:all/></D:principal>
    <D:grant>
    <D:privilege><ns-1:write/></D:privilege>
    <D:privilege><D:read/></D:privilege>
    </D:grant>
    </D:ace>
    <BLANKLINE>
    
    You can also modify the ACL object:
    
    >>> aclObj.add(allACE)
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "acl.py", line 95, in add
        raise ValueError, 'ace already added'
    ValueError: ace already added
    >>> dummyACE = ACE(principal='http://example.com/users/dummy', deny=(), grant=('read', 'DAV:'))
    >>> aclObj.add(dummyACE)
    >>> print dummyACE.denyList()
    []
    >>> print dummyACE.grantList()
    [('read', 'DAV:')]
    >>> print allACE.denyList()
    []
    >>> print allACE.grantList()
    [('write', 'http://www.xythos.com/namespaces/StorageServer/acl/'), ('read', 'DAV:')]
    >>> print aclObj
    <D:acl xmlns:ns-1="http://www.xythos.com/namespaces/StorageServer/acl/" xmlns:D="DAV:">
    <D:ace>
    <D:principal><D:all/></D:principal>
    <D:grant>
    <D:privilege><ns-1:write/></D:privilege>
    <D:privilege><D:read/></D:privilege>
    </D:grant>
    </D:ace>
    <D:ace>
    <D:principal><D:href>http://example.com/users/dummy</D:href></D:principal>
    <D:grant>
    <D:privilege><D:read/></D:privilege>
    </D:grant>
    </D:ace>
    </D:acl>
    >>> aclObj.remove(dummyACE)
    >>> aclObj.remove(dummyACE)
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
      File "acl.py", line 99, in remove
        self.acl.remove(ace)
    ValueError: list.remove(x): x not in list
    >>> print aclObj
    <D:acl xmlns:ns-1="http://www.xythos.com/namespaces/StorageServer/acl/" xmlns:D="DAV:">
    <D:ace>
    <D:principal><D:all/></D:principal>
    <D:grant>
    <D:privilege><ns-1:write/></D:privilege>
    <D:privilege><D:read/></D:privilege>
    </D:grant>
    </D:ace>
    </D:acl>
    
    The handiest way to get an ACL object is to parse it from the XML returned
    by the server:
    
    >>> parsedACL = ACL.parse(str(aclObj))
    >>> print str(parsedACL) == str(aclObj)
    True
    
    Let's parse real life XML now:
    
    >>> xml = \"\"\"<?xml version="1.0" encoding="utf-8" ?>
    ...  <D:multistatus xmlns:D="DAV:" xmlns:XS="http://www.w3.org/2001/XMLSchema" xmlns:XSI="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
    ...  <D:response>
    ...  <D:href>https://www.sharemation.com/heikki2/hello.txt</D:href>
    ...       <D:propstat>
    ...          <D:prop>
    ...  
    ...  <D:acl xmlns:XA="http://www.xythos.com/namespaces/StorageServer/acl/">
    ...  
    ...  <D:ace>
    ...    <D:principal>
    ...      <D:property><D:owner/></D:property>
    ...    </D:principal>
    ...    <D:grant>
    ...      <D:privilege><D:read/></D:privilege>
    ...      <D:privilege><XA:permissions/></D:privilege>
    ...    </D:grant>
    ...    <D:protected/>
    ...  </D:ace>
    ...  
    ...  <D:ace>
    ...    <D:principal>
    ...      <D:property><D:owner/></D:property>
    ...    </D:principal>
    ...    <D:grant>
    ...      <D:privilege><XA:write/></D:privilege>
    ...      <D:privilege><XA:delete/></D:privilege>
    ...    </D:grant>
    ...  </D:ace>
    ...  
    ...  <D:ace>
    ...    <D:principal>
    ...      <D:all/>
    ...    </D:principal>
    ...    <D:grant/>
    ...  </D:ace>
    ...  
    ...  </D:acl>
    ...  
    ...        </D:prop>
    ...         <D:status>HTTP/1.1 200 OK</D:status>
    ...       </D:propstat>
    ...  </D:response>
    ...  </D:multistatus>
    ... \"\"\"
    >>> realACL = ACL.parse(xml)
    >>> print len(realACL.acl), realACL.acl[0].protected
    3 True
    >>> print realACL
    <D:acl xmlns:ns-1="http://www.xythos.com/namespaces/StorageServer/acl/" xmlns:D="DAV:">
    <D:ace>
    <D:principal><D:owner/></D:principal>
    <D:grant>
    <D:privilege><ns-1:write/></D:privilege>
    <D:privilege><ns-1:delete/></D:privilege>
    </D:grant>
    </D:ace>
    <D:ace>
    <D:principal><D:all/></D:principal>
    </D:ace>
    </D:acl>
    """
    
    @classmethod
    def parse(cls, text):
        """
        Parse XML into ACL object::
        
             <!ELEMENT acl (ace*) >
        
            <!ELEMENT ace ((principal | invert), (grant|deny), protected?,
                  inherited?)>

        @param text: The XML (text) to be parsed into an ACL object.
        
        """
    
        doc = ElementTree.XML(text)
        acl = cls()
        
        aclNode = _firstNamedDAVElement(doc, 'acl')
        if aclNode is None:
            raise ValueError, 'acl element not found'
            
        
        for aceNode in aclNode:
            
            if not _isDAVElement(aceNode, 'ace'):
                raise ValueError, 'expected {DAV:}ace, got %s' %(aceNode.tag)

            aceIterator = iter(aceNode)
            
            
            # 1. get principal
            principal = _nextDAVElement(aceIterator, 'principal')

            actualPrincipal = _firstChildElement(principal)
            if not _isDAVElement(actualPrincipal):
                raise ValueError, 'actual principal not found'
            if _isDAVElement(actualPrincipal, 'href'):
                ace = ACE(actualPrincipal.text)
            else:
                if _isDAVElement(actualPrincipal, 'property'):
                    actualPrincipal = _firstChildElement(actualPrincipal)
                    if not _isDAVElement(actualPrincipal):
                        raise ValueError, 'expected property in DAV: ns'

                ace = ACE(_getNameAndNamespace(actualPrincipal)[0])

            # 2. get deny or grant privileges
            node = _nextDAVElement(aceIterator)
            def addPrivileges(addFn):
                for privilege  in node:
                    if not _isDAVElement(privilege, 'privilege'):
                        raise ValueError, 'privilege expected, got %s' %(privilege.tag)
                    priv = _firstChildElement(privilege)
                    addFn(*_getNameAndNamespace(priv))
            if node.tag == zanshin.util.PackElement('deny'):
                addPrivileges(ace.deny)
            elif node.tag == zanshin.util.PackElement('grant'):
                addPrivileges(ace.grant)
            else:
                raise ValueError, 'deny or grant expected, got %s' % (node.tag)

            # 3. get protected property
            node = _nextDAVElement(aceIterator)
            if node is not None:
                if node.tag == zanshin.util.PackElement('protected'):
                    ace.protected = True
                    node = _nextDAVElement(aceIterator)

            # 4. get inherited property
            # ? not implemented
            # if node is not None:
            #    if node.tag == zanshin.util.PackElement('inherited'):
            #         ace.inherited = True

            acl.add(ace)

        return acl

    def __init__(self, acl=None):
        """
        @param acl: A list of ACE objects
        """
        if acl is None:
            acl = []
        self.acl = acl[:]
        self.namespacePrefixMap = {'DAV:': 'D'}
        
    def add(self, ace):
        """
        Add an ACE to the ACL.
        """
        if ace in self.acl:
            raise ValueError, 'ace already added'
        self.acl += [ace]

    def remove(self, ace):
        """
        Remove an ACE from the ACL.
        """
        self.acl.remove(ace)

    def mapPrefixes(self, map):
        """
        Specify namespace prefixes. They are automatically specified,
        but in some instances it is useful to override the defaults.

        @param map: A dictionary where keys are namespace URIs and values
                    the corresponding prefixes.
        """
        map['DAV:'] = 'D'
        self.namespacePrefixMap = map

    def __str__(self):
        namespaces = []
        for ace in self.acl:
            nsList = ace._deny.namespaces() + ace._grant.namespaces()
            for ns in nsList:
                if ns not in namespaces:
                    namespaces += [ns]

        acl = '<D:acl'
        s = ''
        nsCounter = 1
        map = self.namespacePrefixMap

        for namespace in namespaces:
            mappedPrefix = self.namespacePrefixMap.get(namespace)
            if mappedPrefix:
                prefix = mappedPrefix
            else:
                prefix = 'ns-' + _utf8Str(nsCounter)
                map[namespace] = prefix
                nsCounter += 1
            
            acl += ' xmlns:%s="%s"' %(prefix, namespace)

        for ace in self.acl:
            ace._deny.mapPrefixes(map)
            ace._grant.mapPrefixes(map)
            s += _utf8Str(ace)

        return '%s>\n%s</D:acl>' %(acl, s)

def _nextDAVElement(iterator, expected = None):
    result = None
    try:
        result = iterator.next()
    except StopIteration:
        if expected is not None:
            raise ValueError, "Missing element %s" % (expected)
    else:
        if expected is not None:
            if result.tag != zanshin.util.PackElement(expected):
                raise ValueError, 'expected %s, got %s' % (
                    expected, result.tag)
        elif not _isDAVElement(result):
            raise ValueError, 'expected {DAV:} element, got %s' % (result.tag)
            
    return result 

def _firstChildElement(node):
    # We need this method because of text nodes (for example whitespace)
    try:
        return node[0]
    except IndexError:
        return None
    
def _firstNamedDAVElement(node, name):
    for node in node.getiterator(zanshin.util.PackElement(name)):
        return node
    
    return None

def _isDAVElement(node, name=None):
    if name is None:
        return node.tag.startswith(zanshin.util.PackElement(''))
    else:
        return node.tag == zanshin.util.PackElement(name)

def _getNameAndNamespace(element):
    name, namespace = zanshin.util.UnpackElement(element.tag)
    
    if namespace is None: namespace = ''
    return (name, namespace)

class _Principal(object):
    def __init__(self, url):
        """
        Principal.

        @param url: Either principal URL or one of 'all', 'self',
                    'authenticated', 'unauthenticated', 'owner'
        """
        self.url = url

    def __str__(self):
        if self.url in ('all', 'self', 'authenticated', 'unauthenticated',
                        'owner'):
            return '\n<D:principal><D:%s/></D:principal>\n' %(self.url)
        else:
            return '\n<D:principal><D:href>%s</D:href></D:principal>\n' %(self.url)


class _Privileges(object):
    """
    The set of privileges.
    """
    def __init__(self, privilege=()):
        """
        @param privilege: Privilege is a tuple of privilege name and
                          privilege namespace.
        """
        if privilege is not ():
            if privilege[1] == 'DAV:':
                prefix = 'D'
                self.nsCounter = 0
            else:
                self.nsCounter = 1
                prefix = 'ns-1'
            self.privileges = {privilege : prefix}
        else:
            self.nsCounter = 0
            self.privileges = {}
        self.namespacePrefixMap = {'DAV:': 'D'}

    def add(self, name, namespace='DAV:'):
        if namespace == 'DAV:':
            prefix = 'D'
        else:
            self.nsCounter += 1
            prefix = 'ns-%d' %(self.nsCounter)
        self.privileges[(name, namespace)] = prefix

    def remove(self, name, namespace='DAV:'):
        self.privileges.pop((name, namespace))

    def namespaces(self):
        namespaces = []
        keys = self.privileges.keys()
        for key in keys:
            if key[1] not in namespaces:
                namespaces += [key[1]]
        return namespaces

    def mapPrefixes(self, map):
        #@param map: {'namespace': 'prefix'}
        # XXX It kind of sucks that we have another copy of namespacePrefixMap
        # XXX here; ACL also has a version.
        map['DAV:'] = 'D'
        self.namespacePrefixMap = map

    def __str__(self):
        s = ''
        keys = self.privileges.keys()
        for key in keys:
            mappedPrefix = self.namespacePrefixMap.get(key[1])
            if mappedPrefix:
                prefix = mappedPrefix
            else:
                prefix = self.privileges[key]
            s += '<D:privilege><%s:%s/></D:privilege>\n' %(prefix, key[0]) 
        return s


class _Grant(_Privileges):
    """
    The set of privileges to grant.
    """
    def __str__(self):
        if self.privileges:
            return '<D:grant>\n%s</D:grant>\n' %(super(_Grant, self).__str__())
        else:
            return ''


class _Deny(_Privileges):
    """
    The set of privileges to deny.
    """
    def __str__(self):
        if self.privileges:
            return '<D:deny>%s</D:deny>\n' %(super(_Deny, self).__str__())
        else:
            return ''


class SupportedPrivilegeSet(object):
    """
Supported privilege set is defined in RFC3744 Section 5.3.

Client will need this to figure out how custom privileges map to standard
privileges.

>>> xml = \"\"\"<?xml version="1.0" encoding="utf-8" ?>
...   <D:multistatus xmlns:D="DAV:">
...     <D:response>
...       <D:href>http://www.example.com/papers/</D:href>
...       <D:propstat>
...         <D:prop>
...           <D:supported-privilege-set>
...             <D:supported-privilege>
...               <D:privilege><D:all/></D:privilege>
...              <D:abstract/>
...               <D:description xml:lang="en">
...                 Any operation
...               </D:description>
...               <D:supported-privilege>
...                 <D:privilege><D:read/></D:privilege>
...                 <D:description xml:lang="en">
...                   Read any object
...                 </D:description>
...                 <D:supported-privilege>
...                   <D:privilege><D:read-acl/></D:privilege>
...                   <D:abstract/>
...                   <D:description xml:lang="en">Read ACL</D:description>
...                 </D:supported-privilege>
...                 <D:supported-privilege>
...                   <D:privilege>
...                     <D:read-current-user-privilege-set/>
...                   </D:privilege>
...                   <D:abstract/>
...                   <D:description xml:lang="en">
...                     Read current user privilege set property
...                   </D:description>
...                 </D:supported-privilege>
...               </D:supported-privilege>
...               <D:supported-privilege>
...                 <D:privilege><D:write/></D:privilege>
...                 <D:description xml:lang="en">
...                   Write any object
...                 </D:description>
...                 <D:supported-privilege>
...                   <D:privilege><D:write-acl/></D:privilege>
...                   <D:description xml:lang="en">
...                     Write ACL
...                   </D:description>
...                   <D:abstract/>
...                </D:supported-privilege>
...                <D:supported-privilege>
...                   <D:privilege><D:write-properties/></D:privilege>
...                   <D:description xml:lang="en">
...                     Write properties
...                   </D:description>
...                 </D:supported-privilege>
...                 <D:supported-privilege>
...                   <D:privilege><D:write-content/></D:privilege>
...                   <D:description xml:lang="en">
...                     Write resource content
...                   </D:description>
...                 </D:supported-privilege>
...               </D:supported-privilege>
...               <D:supported-privilege>
...                 <D:privilege><D:unlock/></D:privilege>
...                 <D:description xml:lang="en">
...                   Unlock resource
...                 </D:description>
...               </D:supported-privilege>
...               <!-- XXX Put in custom privilege here in custom namespace-->
...             </D:supported-privilege>
...           </D:supported-privilege-set>
...         </D:prop>
...         <D:status>HTTP/1.1 200 OK</D:status>
...       </D:propstat>
...     </D:response>
...   </D:multistatus>\"\"\"
"""
    def __init__(self, privileges=None):
        if privileges is None:
            privileges = []
        self.privileges = privileges
        
    @classmethod
    def parse(cls, text):
        """
        Parse XML to SupportedPrivilegeSet object.::
        
            <!ELEMENT supported-privilege-set (supported-privilege*)>
            <!ELEMENT supported-privilege
                      (privilege, abstract?, description, supported-privilege*)>
            <!ELEMENT privilege ANY>
            <!ELEMENT abstract EMPTY>
            <!ELEMENT description #PCDATA>
        """
        doc = ElementTree.XML(text)

        supportedPrivSet = _firstNamedDAVElement(doc, 'supported-privilege-set')
        if supportedPrivSet is None:
            raise ValueError, 'no supported-privilege-set'

        privileges = []
        for supportedPriv in supportedPrivSet:
            if not _isDAVElement(priv, 'supported-privilege'):
                raise ValueError, 'expected supported-privilege, got %s' %node.tag
            # [@@@] grant too many StopIterations
            spIter = iter(supportedPriv)
            
            node = _nextDAVElement(spIter, 'privilege')
            privilegeNs, privilegeName = _getNameAndNamespace(node[0])

            node = _nextDAVElement(spIter)

            if _isDAVElement(node, 'abstract'):
                abstract = True
            else:
                node = _nextDAVElement(spIter)
                
            if _isDAVElement(node, 'description'):
                description = node.text
                descriptionLanguage = node.get('lang', default='')
            else:
                raise ValueError, 'expected description, got %s' %node.name
                
            privileges.append(SupportedPrivilege(privilegeNamespace,
                                                 privilegeName,
                                                 abstract,
                                                 description,
                                                 descriptionLanguage))

            for node in spIter:
                if _isDAVElement(node, 'supported-privilege'):
                    raise NotImplementedError
                    # Do the same stuff as above
                    # then add as child to current privilege
            
        return cls(privileges)


class Privileges(object):
    """
    WebDAV and CalDAV default privileges to numeric values and back.
    
>>> Privileges.getPrivilegeValue('read')
1
>>> Privileges.getPrivilegeValue('read', 'custom')
0
>>> Privileges.getPrivilegeValue('nonexistent')
Traceback (most recent call last):
...
AttributeError: type object 'Privileges' has no attribute 'NONEXISTENT'

>>> Privileges.getPrivilege(Privileges.READ)
('read', 'DAV:')
>>> Privileges.getPrivilege(Privileges.READ | Privileges.READ_ACL, True)
[('read', 'DAV:'), ('read-acl', 'DAV:')]

>>> Privileges.getPrivilege(Privileges.READ | Privileges.READ_ACL)
Traceback (most recent call last):
...
ValueError: privilege is a list: [('read', 'DAV:'), ('read-acl', 'DAV:')]
>>> Privileges.getPrivilege(0)
Traceback (most recent call last):
...
ValueError: unknown value
""" 
    READ                            = 1
    READ_ACL                        = 2
    READ_CURRENT_USER_PRIVILEGE_SET = 4
    READ_FREE_BUSY                  = 8    # CalDAV
    WRITE                           = 16
    WRITE_ACL                       = 32
    WRITE_CONTENT                   = 64
    WRITE_PROPERTIES                = 128
    BIND                            = 256
    UNBIND                          = 512
    UNLOCK                          = 1024
    ALL                             = 2048 # Not a real privilege

    @classmethod
    def getPrivilegeValue(cls, name, namespace='DAV:'):
        """
        Given a privilege namespace and name, return the numeric value
        of the privilege.
        """
        if namespace != 'DAV:':
            return 0
        return getattr(cls, name.upper().replace('-', '_'))

    @classmethod
    def getPrivilege(cls, value, returnList=False):
        """
        Given a privilege numeric value, return the namespace, name tuple.
        """
        if not (cls.READ <= value <= cls.ALL):
            raise ValueError, 'unknown value'
            
        privileges = []
        
        if value & cls.READ:
            privileges.append(('read', 'DAV:'))
        if value & cls.READ_ACL:
            privileges.append(('read-acl', 'DAV:'))
        if value & cls.READ_CURRENT_USER_PRIVILEGE_SET:
            privileges.append(('read-current-user-privilege-set', 'DAV:'))
        if value & cls.READ_FREE_BUSY:
            privileges.append(('read-free-busy', 'DAV:'))
        if value & cls.WRITE:
            privileges.append(('write', 'DAV:'))
        if value & cls.WRITE_ACL:
            privileges.append(('write-acl', 'DAV:'))
        if value & cls.WRITE_CONTENT:
            privileges.append(('write-content', 'DAV:'))
        if value & cls.WRITE_PROPERTIES:
            privileges.append(('write-properties', 'DAV:'))
        if value & cls.BIND:
            privileges.append(('bind', 'DAV:'))
        if value & cls.UNBIND:
            privileges.append(('unbind', 'DAV:'))
        if value & cls.UNLOCK:
            privileges.append(('unlock', 'DAV:'))
        if value & cls.ALL:
            privileges.append(('all', 'DAV:'))
        
        l = len(privileges)
        
        if l == 0:
            raise Exception, 'internal error'

        if returnList:
            return privileges

        if l > 1:
            raise ValueError, 'privilege is a list: %s' % str(privileges)

        return privileges[0]
    
    
class SupportedPrivilege(object):
    """
>>> sp = SupportedPrivilege('DAV:', 'read', False, 'can read', 'en', [
...      SupportedPrivilege('DAV:', 'read-acl', False, 'can read ACL', 'en', []),
...      SupportedPrivilege('custom', 'admin', False, 'admin', 'en', [])                                                                                 
...      ])
>>> sp.evaluatedPrivilege() == Privileges.READ | Privileges.READ_ACL
True
"""
    def __init__(self, privilegeNamespace, privilegeName, abstract,
                 description, descriptionLanguage, children=None):
        if children is None:
            children = []
        self.privilegeNamespace = privilegeNamespace
        self.privilegeName = privilegeName
        self.abstract = abstract
        self.description = description
        self.descriptionLanguage = descriptionLanguage
        self.children = children
      
    def evaluatedPrivilege(self):
        """
        Evaluate the privileges for this and children.
        """
        evaluated = Privileges.getPrivilegeValue(self.privilegeName,
                                                 self.privilegeNamespace)
        for child in self.children:
            evaluated |= child.evaluatedPrivilege()
            
        return evaluated
        

class CurrentUserPrivilegeSet(object):
    """
    Current user privilege set is defined in RFC3744 Section 5.4.
    
    Client will need this to figure out what it is allowed to do. In practice,
    SupportedPrivilegeSet is also needed to figure out what custom privileges do.
    
    >>> xml = \"\"\"<?xml version="1.0" encoding="utf-8" ?>
    ...   <D:multistatus xmlns:D="DAV:" xmlns:c="custom">
    ...     <D:response>
    ...     <D:href>http://www.example.com/papers/</D:href>
    ...     <D:propstat>
    ...       <D:prop>
    ...         <D:current-user-privilege-set>
    ...           <D:privilege><D:read/></D:privilege>
    ...           <D:privilege><D:write/></D:privilege>
    ...           <D:privilege><c:administer/></D:privilege>
    ...         </D:current-user-privilege-set>
    ...       </D:prop>
    ...       <D:status>HTTP/1.1 200 OK</D:status>
    ...     </D:propstat>
    ...     </D:response>
    ...   </D:multistatus>\"\"\"
    
    >>> cups = CurrentUserPrivilegeSet.parse(xml)
    >>> cups.privileges
    [('read', 'DAV:'), ('write', 'DAV:'), ('administer', 'custom')]
    
    Then some error cases:
    
    >>> CurrentUserPrivilegeSet.parse('')
    Traceback (most recent call last):
    ...
    SyntaxError: no element found: line 1, column 0
    >>> CurrentUserPrivilegeSet.parse('<foo/>')
    Traceback (most recent call last):
    ...
    ValueError: no current-user-privilege-set
    >>> CurrentUserPrivilegeSet.parse('<foo xmlns:D="DAV:"/>')
    Traceback (most recent call last):
    ...
    ValueError: no current-user-privilege-set
    
    It is legal to have empty set, though:
    
    >>> cups2 = CurrentUserPrivilegeSet.parse('<foo xmlns:D="DAV:"><D:current-user-privilege-set/></foo>')
    >>> cups2.privileges
    []
    
    This is perhaps questionable:
        
    >>> cups3 = CurrentUserPrivilegeSet.parse('<foo xmlns:D="DAV:"><D:current-user-privilege-set><D:privilege><somepriv/></D:privilege></D:current-user-privilege-set></foo>')
    >>> cups3.privileges
    [('somepriv', '')]
    """

    def __init__(self, privileges=None):
        if privileges is None:
            privileges = []
        self.privileges = privileges
        
    @classmethod
    def parse(cls, text):
        """
        Parse XML to CurrentUserPrivilegeSet object.::
        
            <!ELEMENT current-user-privilege-set (privilege*)>
            <!ELEMENT privilege ANY>
        """
        doc = ElementTree.XML(text)
        cups = _firstNamedDAVElement(doc, 'current-user-privilege-set')
        
        if cups is None:
            raise ValueError, 'no current-user-privilege-set'
        
        privileges = []
        for node in cups:
            if _isDAVElement(node, 'privilege'):
                try:
                    child = node[0]
                except IndexError:
                    pass
                else:
                    privileges.append(_getNameAndNamespace(child))
            
        return cls(privileges)
            


class ACLRestrictions(object):
    """
    ACL restrictions  is defined in RFC3744 Section 5.6.
    
    Client will need this to figure out how it is allowed to modify ACL.
    
    >>> xml = \"\"\"<?xml version="1.0" encoding="utf-8" ?>
    ...   <D:multistatus xmlns:D="DAV:">
    ...     <D:response>
    ...       <D:href>http://www.example.com/papers/</D:href>
    ...       <D:propstat>
    ...         <D:prop>
    ...           <D:acl-restrictions>
    ...             <D:grant-only/>
    ...             <D:required-principal>
    ...               <!-- XXX This shouldn't be possible per the DTD, but this makes
    ...                    XXX sense to me. -->
    ...               <D:all/>
    ...               <D:property><D:owner/></D:property>
    ...               <D:href>http://www.example.com/users/nobody</D:href>
    ...             </D:required-principal>
    ...           </D:acl-restrictions>
    ...         </D:prop>
    ...         <D:status>HTTP/1.1 200 OK</D:status>
    ...       </D:propstat>
    ...     </D:response>
    ...   </D:multistatus>\"\"\"
       
    >>> ar = ACLRestrictions.parse(xml)
    >>> ar.grantOnly, ar.noInvert, ar.denyBeforeGrant
    (True, False, False)
    >>> ar.requiredPrincipals
    {'all': True, 'authenticated': False, 'unauthenticated': False, 'self': False, 'href': ['http://www.example.com/users/nobody'], 'property': ['owner']}
    
    Then some error cases:
    
    >>> ACLRestrictions.parse('')
    Traceback (most recent call last):
    ...
    SyntaxError: no element found: line 1, column 0
    >>> ACLRestrictions.parse('<foo/>')
    Traceback (most recent call last):
    ...
    ValueError: no acl-restrictions
    >>> ACLRestrictions.parse('<foo xmlns:D="DAV:"/>')
    Traceback (most recent call last):
    ...
    ValueError: no acl-restrictions
    
    It is legal to have empty restrictions, though:
    
    >>> ar2 = ACLRestrictions.parse('<foo xmlns:D="DAV:"><D:acl-restrictions/></foo>')
    >>> ar2.grantOnly, ar.noInvert, ar.denyBeforeGrant
    (False, False, False)
    >>> ar2.requiredPrincipals is None
    True
    """
    
    def __init__(self, grantOnly=False, noInvert=False, denyBeforeGrant=False,
                 requiredPrincipals=None):
        self.grantOnly = grantOnly
        self.noInvert = noInvert
        self.denyBeforeGrant = denyBeforeGrant
        self.requiredPrincipals = requiredPrincipals
        
    @classmethod
    def parse(cls, text):
        """
        Parse XML to ACLRestrictions object.::
        
            <!ELEMENT acl-restrictions (grant-only?, no-invert?,
                                       deny-before-grant?, required-principal?)>
            <!ELEMENT grant-only EMPTY>
            <!ELEMENT no-invert EMPTY>
            <!ELEMENT deny-before-grant EMPTY>
            <!ELEMENT required-principal
                      (all? | authenticated? | unauthenticated? | self? |
                       href* | property*)>
        """
        doc = ElementTree.XML(text)

        aclRestrElement = _firstNamedDAVElement(doc, 'acl-restrictions')
        if aclRestrElement is None:
            raise ValueError, 'no acl-restrictions'

        aclRestrictions = {'grant-only':False, 'no-invert': False,
                           'deny-before-grant': False}
                           
        def matchAndSetBooleans(dictionary, node, *keys):
            for key in keys:
                matched = _isDAVElement(node, key)
                if matched:
                    if dictionary[key]:
                        raise ValueError, '%s appears more than once' % (
                                          key)
                    dictionary[key] = True
                    return True
            return False

        for child in aclRestrElement:

            if not matchAndSetBooleans(aclRestrictions, child, 'grant-only',
                                      'no-invert', 'deny-before-grant'):
                if _isDAVElement(child, 'required-principal'):
                    # XXX (heikki) I disagree with what the DTD says and what
                    # XXX I think the intent is - I've implemented the intent.
                    principals = {'all': False, 'authenticated': False,
                                  'unauthenticated': False, 'self': False,
                                  'href': [], 'property': []}
                    for node in child:
                        if not matchAndSetBooleans(principals, node, 'all',
                                         'authenticated', 'unauthenticated',
                                         'self'):
                                 
                            if _isDAVElement(node, 'href'):
                                principals['href'].append(node.text)
                            if _isDAVElement(node, 'property'):
                                # XXX Are custom properties not in DAV: 
                                # XXX namespace allowed?
                                # XXX IndexError on node[0]?
                                principals['property'].append(
                                    _getNameAndNamespace(node[0])[0])
                        
                    return cls(aclRestrictions['grant-only'],
                               aclRestrictions['no-invert'],
                               aclRestrictions['deny-before-grant'],
                               principals)
            
        return cls(aclRestrictions['grant-only'],
                   aclRestrictions['no-invert'],
                   aclRestrictions['deny-before-grant'])
            
            
class PrincipalCollectionSet(object):
    """
    Principal collection is defined in RFC3744 Section 5.8. 
    
    Client can use this to find the principals that could be specified in ACEs, 
    but this may not be an exhaustive list - in fact the server may refuse to 
    return anything.

    >>> xml = \'\'\'<?xml version="1.0" encoding="utf-8" ?>
    ...   <D:multistatus xmlns:D="DAV:">
    ...     <D:response>
    ...       <D:href>http://www.example.com/papers/</D:href>
    ...       <D:propstat>
    ...         <D:prop>
    ...           <D:principal-collection-set>
    ...             <D:href>http://www.example.com/acl/users/</D:href>
    ...             <D:href>http://www.example.com/acl/groups/</D:href>
    ...           </D:principal-collection-set>
    ...         </D:prop>
    ...       <D:status>HTTP/1.1 200 OK</D:status>
    ...       </D:propstat>
    ...     </D:response>
    ...   </D:multistatus>\'\'\'
    
    >>> pcs = PrincipalCollectionSet.parse(xml)
    >>> pcs.hrefs
    ['http://www.example.com/acl/users/', 'http://www.example.com/acl/groups/']
    
    Some error cases:
    
    >>> PrincipalCollectionSet.parse('<foo/>')
    Traceback (most recent call last):
    ...
    ValueError: no principal-collection-set
    >>> PrincipalCollectionSet.parse('<foo xmlns:D="DAV:"/>')
    Traceback (most recent call last):
    ...
    ValueError: no principal-collection-set
    
    It is legal to have empty set, though:
    
    >>> pcs2 = PrincipalCollectionSet.parse('<foo xmlns:D="DAV:"><D:principal-collection-set/></foo>')
    >>> pcs2.hrefs
    []
    """

    def __init__(self, hrefs=None):
        if hrefs is None:
            hrefs = []
        self.hrefs = hrefs
        
    @classmethod
    def parse(cls, text):
        """
        Parse XML to PrincipalCollectionSet object.::
        
            <!ELEMENT principal-collection-set (href*)>
        """
        doc = ElementTree.XML(text)

        pcsNode = _firstNamedDAVElement(doc, 'principal-collection-set')
        if pcsNode is None:
            raise ValueError, 'no principal-collection-set'
            

        hrefs = []
        for node in pcsNode:
            if _isDAVElement(node, 'href'):
                hrefs.append(node.text)
            
        return cls(hrefs)


def getNonAbstractPrivileges(supportedPrivilege):
    """
    Get non-abstract (concrete) supported privileges.
    
    @param supportedPrivilege: Supported privilege to operate on.
    @type supportedPrivilege:  SupportedPrivilege

    >>> sp = SupportedPrivilege('DAV:', 'read', False, 'can read', 'en', [
    ...      SupportedPrivilege('DAV:', 'read-acl', False, 'can read ACL', 'en', []),
    ...      SupportedPrivilege('custom', 'admin', False, 'admin', 'en', [])                                                                                 
    ...      ])
    >>> getNonAbstractPrivileges(sp)
    [('DAV:', 'read'), ('DAV:', 'read-acl'), ('custom', 'admin')]
    
    >>> sp = SupportedPrivilege('DAV:', 'read', True, 'can read', 'en', [
    ...      SupportedPrivilege('DAV:', 'read-acl', False, 'can read ACL', 'en', []),
    ...      SupportedPrivilege('custom', 'admin', False, 'admin', 'en', [])                                                                                 
    ...      ])
    >>> getNonAbstractPrivileges(sp)
    [('DAV:', 'read-acl'), ('custom', 'admin')]
    """
    privileges = []
    if not supportedPrivilege.abstract:
        privileges.append((supportedPrivilege.privilegeNamespace,
                           supportedPrivilege.privilegeName))
                
    for child in supportedPrivilege.children:
        privileges.extend(getNonAbstractPrivileges(child))
        
    return privileges


def _mapStandardPrivilegeToCustomPrivileges(stdName, supportedPrivilege, 
                                            currentUserPrivilegeSet=None):
    # The actual worker function for mapStandardPrivilegeToCustomPrivilege
    if (stdName, 'DAV:') == (supportedPrivilege.privilegeName,
                             supportedPrivilege.privilegeNamespace):
        if not supportedPrivilege.abstract:
            stdPrivilege = ('DAV:', stdName)
            if currentUserPrivilegeSet is not None and \
               stdPrivilege not in currentUserPrivilegeSet.privileges:
                #XXX Need better exception class
                raise Exception, 'current user does not have privilege %s' % str(stdPrivilege)
            #XXX Should probably check default grouping as well and add what
            #XXX needs to be added
            return [stdPrivilege]
        
        # Since the supportedPrivilege we want is abstract, we must look at it's
        # children to determine the list of non-abstract privileges
        concretePrivileges = getNonAbstractPrivileges(supportedPrivilege)
        for privilege in concretePrivileges:
            if currentUserPrivilegeSet is not None and \
               privilege not in currentUserPrivilegeSet.privileges:
                #XXX Need better exception class
                raise Exception, 'current user does not have privilege %s' % str(privilege)
        return concretePrivileges

    for child in supportedPrivilege.children:
        ret = _mapStandardPrivilegeToCustomPrivileges(stdName, child, 
                                                      currentUserPrivilegeSet)
        if ret:
            return ret
    
    return []


def mapStandardPrivilegeToCustomPrivileges(stdName, supportedPrivilegeSet,
                                           currentUserPrivilegeSet=None):
    """
    Map a standard privilege (in the DAV: namespace) to the possibly custom
    list of (namespace, name) tuples of privileges. Or in ther words, this
    function returns the list of actual privileges that need to be set in
    order to cause the same effect (or as close as possible) as the standard
    privilege defines.
    
    The optional current user privilege set will check the privileges against
    the what the current user is allowed to to do. This will raise an exception
    if something is not allowed.
    
    @param stdName:                 Name of a standard privilege (in the DAV: 
                                    namespace).
    @type stdName:                  str
    @param supportedPrivilegeSet:   The privileges supported by the server.
    @type supportedPrivilegeSet:    SupportedPrivilegeSet
    @param currentUserPrivilegeSet: The actual privileges allowed by current
                                    user.
    @type currentUserPrivilegeSet:  CurrentUserPrivilegeSet
    
    >>> sp = SupportedPrivilege('DAV:', 'read', False, 'can read', 'en', [
    ...      SupportedPrivilege('DAV:', 'read-acl', False, 'can read ACL', 'en', []),
    ...      SupportedPrivilege('custom', 'admin', False, 'admin', 'en', [])                                                                                 
    ...      ])
    >>> spSet = SupportedPrivilegeSet([sp])
    >>> mapStandardPrivilegeToCustomPrivileges('read', spSet)
    [('DAV:', 'read')]
    
    >>> sp = SupportedPrivilege('DAV:', 'read', True, 'can read', 'en', [
    ...      SupportedPrivilege('DAV:', 'read-acl', False, 'can read ACL', 'en', []),
    ...      SupportedPrivilege('custom', 'admin', False, 'admin', 'en', [])                                                                                 
    ...      ])
    >>> spSet = SupportedPrivilegeSet([sp])
    >>> mapStandardPrivilegeToCustomPrivileges('read', spSet)
    [('DAV:', 'read-acl'), ('custom', 'admin')]
    
    >>> cupSet = CurrentUserPrivilegeSet([('DAV:', 'read-acl'), ('custom', 'admin')])
    >>> mapStandardPrivilegeToCustomPrivileges('read', spSet, cupSet)
    [('DAV:', 'read-acl'), ('custom', 'admin')]
    
    >>> cupSet = CurrentUserPrivilegeSet([('DAV:', 'read-acl')])
    >>> mapStandardPrivilegeToCustomPrivileges('read', spSet, cupSet)
    Traceback (most recent call last):
    ...
    Exception: current user does not have privilege ('custom', 'admin')
"""
    privileges = []
    for supportedPrivilege in supportedPrivilegeSet.privileges:
        privilegeList = _mapStandardPrivilegeToCustomPrivileges(stdName, supportedPrivilege, currentUserPrivilegeSet)
        privileges.extend(privilegeList)
    return privileges


if __name__ == '__main__':
    import doctest
    doctest.testmod()
