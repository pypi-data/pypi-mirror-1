#  Copyright (C) 2007 Yannick Gingras <ygingras@ygingras.net>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


from formencode import Schema, validators, All
from gazest.lib.openidutil import *
from gazest import model

import re
import iplib

USERNAME_PAT = re.compile(r'^\w(?:\w|[\-_.]){2,}$', re.UNICODE)


class CIDRValidator(validators.UnicodeString):
    """ An IP range in CIDR notation.  Single IP accepted without the
    '/32' qualifier.  An iplib.CIDR object is returned. """
    def _to_python(self, value, state):
        if iplib.is_dot(value):
            return iplib.CIDR(value+"/32")
        try:
            return iplib.CIDR(value)
        except ValueError:
            raise validators.Invalid(
                "Must be an IP range in CIDR notation. Ex: '192.168.0.0/24'",
                val, 
                state)


class IntListValidator(validators.UnicodeString):
    """A possibly empty coma separated list of integers"""
    def _to_python(self, value, state):
        val = validators.UnicodeString._to_python(self, value, state)
        try:
            ints = map(int, val.split(","))
        except ValueError:
            raise validators.Invalid(
                "Must be a coma separated list of integers like '1,2,3'",
                val, 
                state)
        return ints


class OpenIDValidator(validators.URL):
    """Check if an URL is a valid openid handle and normalize it"""
    def _to_python(self, value, state):
        norm = normalizeURI(value)
        validators.URL._to_python(self, value, state)
        cons = openid_consumer()

        try:
            auth_request = cons.begin(norm)
            return norm
        except DiscoveryFailure, e:
            raise validators.Invalid(
                "OpenID discovery error: '%s'" % str(e),
                norm, 
                state)
        

class UsernameValidator(validators.UnicodeString):
    """A username is like a Python variable name + Unicode + '-' + '.'."""
    def _to_python(self, value, state):
        val = validators.UnicodeString._to_python(self, value, state)
        if not (USERNAME_PAT.match(val) and val[0].isalpha()):
            # FIME: how do we deal with users with the same name but
            #       different case?
            raise validators.Invalid(
                ("A username must be at least 3 characters long"
                 " and start with a letter.  It can inlude only letters,"
                 " digits, '.', '-', and '_'."),
                val, 
                state)
        return val


class ActiveOpenIDValidator(OpenIDValidator):
    """Check for a valid openid that also belongs to an active user."""
    def _to_python(self, value, state):
        norm = OpenIDValidator._to_python(self, value, state)
        user = model.User.query.selectfirst_by(openid=norm, status="active")
        if not user:
            raise validators.Invalid(
                "This OpenID doesn't belong to a registered user.",
                norm, 
                state)
        return norm



class ActiveEmailValidator(validators.Email):
    """Check for a valid email that also belongs to an active user."""
    def _to_python(self, value, state):
        norm = validators.Email._to_python(self, value, state)
        user = model.User.query.selectfirst_by(email=norm, status="active")
        if not user:
            raise validators.Invalid(
                "This email doesn't belong to a registered user.",
                norm, 
                state)
        return norm



class ActiveUsernameValidator(UsernameValidator):
    """Check for a valid username that also belongs to an active user."""
    def _to_python(self, value, state):
        norm = validators.UnicodeString._to_python(self, value, state)
        user = model.User.query.selectfirst_by(username=norm, status="active")
        if not user:
            raise validators.Invalid(
                "There is no user called %s" % norm,
                norm, 
                state)
        return norm
