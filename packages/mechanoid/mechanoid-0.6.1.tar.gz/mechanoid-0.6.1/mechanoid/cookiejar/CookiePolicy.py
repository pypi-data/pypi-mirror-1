
# cookiejar.CookiePolicy.py::refactored from JJLee's ClientCookie
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



class CookiePolicy:
    """Defines which cookies get accepted from and returned to server.

    The subclass DefaultCookiePolicy defines the standard rules for Netscape
    and RFC 2965 cookies -- override that if you want a customised policy.

    As well as implementing set_ok and return_ok, implementations of this
    interface must also supply the following attributes, indicating which
    protocols should be used, and how.  These can be read and set at any time,
    though whether that makes complete sense from the protocol point of view is
    doubtful.

    Public attributes:

    netscape: implement netscape protocol
    rfc2965: implement RFC 2965 protocol
    hide_cookie2: don't add Cookie2 header to requests (the presence of
     this header indicates to the server that we understand RFC 2965
     cookies)

    """
    def set_ok(self, cookie, request, unverifiable):
        """Return true if (and only if) cookie should be accepted from server.

        Currently, pre-expired cookies never get this far -- the CookieJar
        class deletes such cookies itself.

        cookie: ClientCookie.Cookie object
        request: object implementing the interface defined by
         CookieJar.extract_cookies.__doc__
        unverifiable: flag indicating whether the transaction is unverifiable,
         as defined by RFC 2965

        """
        raise NotImplementedError()

    def return_ok(self, cookie, request, unverifiable):
        """Return true if (and only if) cookie should be returned to server.

        cookie: ClientCookie.Cookie object
        request: object implementing the interface defined by
         CookieJar.add_cookie_header.__doc__
        unverifiable: flag indicating whether the transaction is unverifiable,
         as defined by RFC 2965

        """
        raise NotImplementedError()

    def domain_return_ok(self, domain, request, unverifiable):
        """Return false if cookies should not be returned, given cookie domain.

        This is here as an optimization, to remove the need for checking every
        cookie with a particular domain (which may involve reading many files).
        The default implementations of domain_return_ok and path_return_ok
        (return True) leave all the work to return_ok.

        If domain_return_ok returns true for the cookie domain, path_return_ok
        is called for the cookie path.  Otherwise, path_return_ok and return_ok
        are never called for that cookie domain.  If path_return_ok returns
        true, return_ok is called with the Cookie object itself for a full
        check.  Otherwise, return_ok is never called for that cookie path.

        Note that domain_return_ok is called for every *cookie* domain, not
        just for the *request* domain.  For example, the function might be
        called with both ".acme.com" and "www.acme.com" if the request domain is
        "www.acme.com".  The same goes for path_return_ok.

        For argument documentation, see the docstring for return_ok.

        """
        return True

    def path_return_ok(self, path, request, unverifiable):
        """Return false if cookies should not be returned, given cookie path.

        See the docstring for domain_return_ok.

        """
        return True


