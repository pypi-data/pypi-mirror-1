
# cookiejar.Cookie.py::refactored from JJLee's ClientCookie
# richardharris@operamail.com
# http://cheeseshop.python.org

# Copyright (C) 2004 by Richard Harris
# Released under the GNU General Public License
# (See the included COPYING file)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

# Hack_History:
# 
# Copyright 2004 Richard Harris (mechanoid fork under GNU GPL)
# Copyright 2002-2003 John J Lee <jjl@pobox.com>
# Copyright 1997-1999 Gisle Aas (original libwww-perl code)
# Copyright 2002-2003 Johnny Lee (original MSIE Perl code)
#

import copy, string, time

class Cookie:
    """HTTP Cookie.

    This class represents both Netscape and RFC 2965 cookies.

    This is deliberately a very simple class.  It just holds attributes.  It's
    possible to construct Cookie instances that don't comply with the cookie
    standards.  CookieJar.make_cookies is the factory function for Cookie
    objects -- it deals with cookie parsing, supplying defaults, and
    normalising to the representation used in this class.  CookiePolicy is
    responsible for checking them to see whether they should be accepted from
    and returned to the server.

    version: integer;
    name: string (may be None);
    value: string;
    port: string; None indicates no attribute was supplied (eg. "Port", rather
     than eg. "Port=80"); otherwise, a port string (eg. "80") or a port list
     string (eg. "80,8080")
    port_specified: boolean; true if a value was supplied with the Port
     cookie-attribute
    domain: string;
    domain_specified: boolean; true if Domain was explicitly set
    domain_initial_dot: boolean; true if Domain as set in HTTP header by server
     started with a dot (yes, this really is necessary!)
    path: string;
    path_specified: boolean; true if Path was explicitly set
    secure:  boolean; true if should only be returned over secure connection
    expires: integer; seconds since epoch (RFC 2965 cookies should calculate
     this value from the Max-Age attribute)
    discard: boolean, true if this is a session cookie; (if no expires value,
     this should be true)
    comment: string;
    comment_url: string;
    rest: mapping of other attributes

    Note that the port may be present in the headers, but unspecified ("Port"
    rather than"Port=80", for example); if this is the case, port is None.

    """

    def __init__(self, version, name, value,
                 port, port_specified,
                 domain, domain_specified, domain_initial_dot,
                 path, path_specified,
                 secure,
                 expires,
                 discard,
                 comment,
                 comment_url,
                 rest):

        if version is not None: version = int(version)
        if expires is not None: expires = int(expires)
        if port is None and port_specified is True:
            raise ValueError("if port is None, port_specified must be false")

        self.version = version
        self.name = name
        self.value = value
        self.port = port
        self.port_specified = port_specified
        # normalise case, as per RFC 2965 section 3.3.3
        self.domain = string.lower(domain)
        self.domain_specified = domain_specified
        # Sigh.  We need to know whether the domain given in the
        # cookie-attribute had an initial dot, in order to follow RFC 2965
        # (as clarified in draft errata).  Needed for the returned $Domain
        # value.
        self.domain_initial_dot = domain_initial_dot
        self.path = path
        self.path_specified = path_specified
        self.secure = secure
        self.expires = expires
        self.discard = discard
        self.comment = comment
        self.comment_url = comment_url

        self.rest = copy.copy(rest)

    def is_expired(self, now=None):
        if now is None: now = time.time()
        if (self.expires is not None) and (self.expires <= now):
            return True
        return False

    def __str__(self):
        if self.port is None: p = ""
        else: p = ":"+self.port
        limit = self.domain + p + self.path
        if self.name is not None:
            namevalue = "%s=%s" % (self.name, self.value)
        else:
            namevalue = self.value
        return "<Cookie %s for %s>" % (namevalue, limit)

    def __repr__(self):
        args = []
        for name in ["version", "name", "value",
                     "port", "port_specified",
                     "domain", "domain_specified", "domain_initial_dot",
                     "path", "path_specified",
                     "secure", "expires", "discard", "comment", "comment_url",
                     "rest"]:
            attr = getattr(self, name)
            args.append("%s=%s" % (name, repr(attr)))
        return "Cookie(%s)" % string.join(args, ", ")

