"""Schevo identity middleware.

For copyright, license, and warranty, see bottom of file.
"""


def schevo_authfunc(db_name='schevo.db', extent_name='SchevoIdUser',
                    name_field='name', password_field='password'):
    """Return an authentication function for use as the ``authfunc``
    when using `paste.auth` middleware."""
    def authfunc(username, password, environ):
        print environ
        db = environ[db_name]
        print '   db', db
        extent = db.extent(extent_name)
        print '   extent', extent
        criteria = {name_field: username, password_field: password}
        print '   criteria', criteria
        user = extent.findone(**criteria)
        print '   user', user
        return user is not None
    return authfunc


class RemoteUserDereferencer(object):
    """If a username exists in the WSGI environ, dereference it to an
    entity."""

    def __init__(self, app, remote_user_name='REMOTE_USER',
                 dereferenced_name='REMOTE_USER.entity',
                 db_name='schevo.db', extent_name='SchevoIdUser',
                 name_field='name'):
        self._app = app
        self._remote_user_name = remote_user_name
        self._dereferenced_name = dereferenced_name
        self._db_name = db_name
        self._extent_name = extent_name
        self._name_field = name_field

    def __call__(self, environ, start_response):
        db = environ[self._db_name]
        name = environ.get(self._remote_user_name, None)
        if name is not None:
            extent = db.extent(self._extent_name)
            criteria = {self._name_field: name}
            user = extent.findone(**criteria)
            environ[self._dereferenced_name] = user
        return self._app(environ, start_response)


# Copyright (C) 2001-2007 Orbtech, L.L.C.
#
# Schevo
# http://schevo.org/
#
# Orbtech
# Saint Louis, MO
# http://orbtech.com/
#
# This toolkit is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This toolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
