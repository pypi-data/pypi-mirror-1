#  -*- coding: utf8 -*-
#  Copyright (c) 2007 Eurotux Informática S.A.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

__author__  = 'Ricardo Alves <rsa at eurotux dot com>'
__docformat__ = 'plaintext'

import ldap_connection
from ldap_connection import LDAPConnection

def initialize(context):
    # register class
    context.registerClass(
        ldap_connection.LDAPConnection,
        permission='Add LDAPConnection',
        constructors=(ldap_connection.manage_addLDAPConnectionForm,
            ldap_connection.manage_addLDAPConnection,),
    )
