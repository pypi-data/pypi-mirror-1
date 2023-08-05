"""mysqlstore - Database storage for flup session middleware.

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


from flup.middleware.session import SessionMiddleware
from MySQLdb import connect, escape_string, DatabaseError
from storage import DBSessionStore


# maybe this should take a connection string
def mysql_sessionizer(*args, **kwargs):
    """Take args for connection and return decorator."""
    def get_connection():
        return connect(*args, **kwargs)
    store = DBSessionStore(get_connection, escape_string, DatabaseError)
    def sessionizer(app):
        return SessionMiddleware(store, app)
    return sessionizer


if __name__ == '__main__':
    sessionized = mysql_sessionizer(host='localhost', 
                                    user='foo', 
                                    passwd='foo', 
                                    db='foo')

    @sessionized
    def foo_app(environ, start_response):
        """WSGI app for simple test of session."""
        session = environ['com.saddi.service.session'].session
        if not session.has_key('foo'):
            session['foo'] = 0
            session['bar'] = {'a':'A', 'b':'B'}
            session['baz'] = r"Try these !@#$%^&*()_+-=|}{\][\":';?></.,"
        session['foo'] += 1
        start_response('200 Ok', [('content-type', 'text/plain')])
        return ["Session id: %s\n" % session.identifier,
                "Session['foo'] == %s\n" % session['foo'],
                "a == %(a)r and b == %(b)r\n" % session['bar'],
                session['baz']]

    from flup.server.scgi import WSGIServer
    WSGIServer(foo_app).run()

