##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################

"""Commonly used functions for WebDAV support modules."""

__version__='$Revision: 1.2 $'[11:-2]

import string, time, urllib, re
from App_Common import iso8601_date, rfc850_date, rfc1123_date
from App_Common import aq_base

def absattr(attr):
    if callable(attr):
        return attr()
    return attr

def urlfix(url, s):
    n=len(s)
    if url[-n:]==s: url=url[:-n]
    if len(url) > 1 and url[-1]=='/':
        url=url[:-1]
    return url

def is_acquired(ob):
    # Return true if this object is not a direct
    # subobject of its aq_parent object.
    if not hasattr(ob, 'aq_parent'):
        return 0
    if hasattr(aq_base(ob.aq_parent), absattr(ob.id)):
        return 0
    if hasattr(aq_base(ob), 'isTopLevelPrincipiaApplicationObject') and \
            ob.isTopLevelPrincipiaApplicationObject:
        return 0
    return 1

def urlbase(url, ftype=urllib.splittype, fhost=urllib.splithost):
    # Return a '/' based url such as '/foo/bar', removing
    # type, host and port information if necessary.
    if url[0]=='/': return url
    type, uri=ftype(url)
    host, uri=fhost(uri)
    return uri or '/'

def generateLockToken():
    # Generate a lock token
    # XXX This is simple right now, just lifted from the original shortcut
    # in Resource.dav__genlocktoken, but should be replaced by something
    # better.
    return 'AA9F6414-1D77-11D3-B825-00105A989226:%.03f' % time.time()

def tokenFinder(token):
    # takes a string like '<opaquelocktoken:afsdfadfadf> and returns the token
    # part.
    if not token: return None           # An empty string was passed in
    if token[0] == '[': return None     # An Etag was passed in
    if token[0] == '<': token = token[1:-1]
    return token[string.find(token,':')+1:]


### If: header handling support.  IfParser returns a sequence of
### TagList objects in the order they were parsed which can then
### be used in WebDAV methods to decide whether an operation can
### proceed or to raise HTTP Error 412 (Precondition failed)
IfHdr = re.compile(
    r"(?P<resource><.+?>)?\s*\((?P<listitem>[^)]+)\)"
    )

ListItem = re.compile(
    r"(?P<not>not)?\s*(?P<listitem><[a-zA-Z]+:[^>]*>|\[.*?\])",
    re.I)

class TagList:
    def __init__(self):
        self.resource = None
        self.list = []
        self.NOTTED = 0

def IfParser(hdr):
    out = []
    i = 0
    while 1:
        m = IfHdr.search(hdr[i:])
        if not m: break

        i = i + m.end()
        tag = TagList()
        tag.resource = m.group('resource')
        if tag.resource:                # We need to delete < >
            tag.resource = tag.resource[1:-1]
        listitem = m.group('listitem')
        tag.NOTTED, tag.list = ListParser(listitem)
        out.append(tag)

    return out

def ListParser(listitem):
    out = []
    NOTTED = 0
    i = 0
    while 1:
        m = ListItem.search(listitem[i:])
        if not m: break

        i = i + m.end()
        out.append(m.group('listitem'))
        if m.group('not'): NOTTED = 1

    return NOTTED, out
