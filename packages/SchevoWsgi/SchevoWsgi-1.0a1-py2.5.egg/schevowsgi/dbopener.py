"""Database opener middleware for WSGI apps.

For copyright, license, and warranty, see bottom of file.
"""

from StringIO import StringIO

from schevo import database
from schevo import schema


def filter_factory(global_conf, **local_conf):
    def filter(app):
        return DatabaseOpener(app, local_conf)
    return filter


class DatabaseOpener(object):
    """Database opener middleware for WSGI apps.

    A DatabaseOpener instance will look for configuration items whose
    keys begin with ``schevo.db.``, and open the corresponding
    database using the location given by that configuration item.

    During WSGI application invocation, a DatabaseOpener attaches
    those same keys in the WSGI environment, with the values being the
    open Schevo databases.  It also attaches a key ``schevo.db``,
    which is a dictionary whose keys are the names of each database and
    whose values are the open Schevo databases.

    The DatabaseOpener instance itself is injected into the WSGI
    environment with the key ``schevo.dbopener``.  This allows other
    components in the WSGI stack to call the `open` and `close`
    methods to open and close more databases, respectively.
    """

    key_prefix = 'schevo.db'
    name = key_prefix + 'opener'
    verbose = False

    def __init__(self, app, config):
        """Create a new DatabaseOpener instance.

        - ``app``: The application to filter.

        - ``config``: The configuration in which to look for database
          keys and filenames.
        """
        verbose = config.get('verbose', 'false').lower()
        self.verbose = (verbose == 'true')
        self._app = app
        dbdict = self._dbdict = {}
        environ = self._environ = {
            self.name: self,
            self.key_prefix: dbdict,
            }
        dot_prefix = self.key_prefix + '.'
        for key, value in config.iteritems():
            if key.startswith(dot_prefix):
                db_alias = key[len(dot_prefix):]
                self.open(db_alias, value)

    def __call__(self, environ, start_response):
        environ.update(self._environ)
        return self._app(environ, start_response)

    def open(self, db_alias, db_filename, environ=None):
        if self.verbose:
            print '[dbopener] Opening %r (%r)' % (db_alias, db_filename)
        environ_key = self.key_prefix + '.' + db_alias
        if db_filename.startswith('memory://'):
            db = self._open_memory(db_alias, db_filename)
        else:
            db = self._open_file(db_alias, db_filename)
        self._dbdict[db_alias] = db
        self._environ[environ_key] = db
        if environ is not None:
            environ[environ_key] = db

    def _open_memory(self, db_alias, db_filename):
        # XXX: Only supports version 1 of databases so far.
        scheme, resource = db_filename.split('://')
        module_name, version = resource.split('/')
        version = int(version)
        fp = StringIO()
        schema_source = schema.read(module_name, version)
        db = database.open(fp=fp, schema_source=schema_source)
        return db

    def _open_file(self, db_alias, db_filename):
        db = database.open(db_filename)
        return db

    def close(self, db_alias, environ=None):
        if self.verbose:
            print '[dbopener] Closing %r' % db_alias
        environ_key = self.key_prefix + '.' + db_alias
        db = self._dbdict[db_alias]
        del self._dbdict[db_alias]
        del self._environ[environ_key]
        if environ is not None:
            del environ[environ_key]
        db.close()


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
