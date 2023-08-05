"""storage - Database storage for flup session middleware.

This module is part of the dbstore package.

Copyright (C) 2006 Luke Arno - http://lukearno.com/

This program is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, or (at your 
option) any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/

"""


import time
import pickle
from flup.middleware.session import SessionStore


class DBSessionStore(SessionStore):
    """DB-based session store (uses 'sessions' table.)
    
    The sessions table should have these three fields:
    
        id (a character field long enough to store your identifiers)
        touched (a float type of some kind)
        pickle (a long text field)

    The size of your text field will limit the size of your session.
    Check your database and driver documentation.

    For example, in MySQL:

    CREATE TABLE sessions (
        id VARCHAR(32) NOT NULL, 
        touched  FLOAT, 
        pickle LONGTEXT, 
        primary key (id));
    """

    _insert = "insert into sessions (id, touched) values ('%s', '%s')"
    _select = "select pickle from sessions where id = '%s'"
    _update = "update sessions set pickle = '%s', touched = '%s'\
                where id = '%s'"
    _delete = "delete from session where id = '%s'"
    _clean_up = "delete from sessions where touched < '%s'"

    def __init__(self, get_connection, escape, DBError, *a, **kw):
        """Initialize with the particulars of your database
        
        get_connection must need no args and return a connection.
        escape is a func to do escaping for the query string
        DBError should be the appropriate DatabaseError (dbapi2.0)
        """
        super(DBSessionStore, self).__init__(*a, **kw)
        self._get_connection = get_connection
        self._escape = escape
        self._DBError = DBError

    def execute(self, query):
        """Run the query and return the results."""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
        finally:
            connection.close()
        return results

    def _createSession(self, identifier):
        """Create an empty session record in the DB."""
        escaped_id = self._escape(identifier)
        try:
            self.execute(self._insert % (escaped_id, time.time()))
        except self._DBError, e:
            return None
        return self._sessionClass(identifier)

    def _loadSession(self, identifier, block=True):
        """Load the session from the database."""
        escaped_id = self._escape(identifier)
        results = self.execute(self._select % escaped_id)
        session_string = results[0][0]
        return pickle.loads(session_string)

    def _saveSession(self, session):
        """Save the session to the database."""
        escaped_id = self._escape(session.identifier)
        last_access = session._lastAccessTime
        s = pickle.dumps(session, protocol=pickle.HIGHEST_PROTOCOL)
        s = self._escape(s)
        self.execute(self._update % (s, last_access, escaped_id))

    def _deleteSession(self, identifier):
        """Delete the session record from the database."""
        escaped_id = self._escape(identifier)
        self.execute(self._delete % escaped_id)

    def _periodic(self):
        """Delete all the timed out sessions."""
        oldest_valid = time.time() - self._sessionTimeout * 60
        self.execute(self._clean_up % oldest_valid)

    def _shutdown(self):
        """Do nothing."""
        pass


