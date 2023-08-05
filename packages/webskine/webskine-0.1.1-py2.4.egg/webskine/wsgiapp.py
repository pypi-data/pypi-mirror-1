import re
import datetime
from urlparse import urljoin
from cgi import escape

from paste import httpexceptions
from paste.request import construct_url
from paste.auth.digest import digest_password, AuthDigestHandler

from atomstorage import EntryManager
from jsonstore.jsonstore import JSONStore
from webskine.templates import xhtml, atom
from webskine.middleware import ContentMiddleware


def make_app(global_conf, title='', dsn='shelve://entries.db', entries=10, user='test', password='test', **kwargs):
    """
    Create a weblog.

    Configuration should be like this::

        [app:weblob]
        use = egg:webskine
        title = Weblog title
        dsn = protocol://location  # for atomstorage
        entries = 10
        user = username
        password = *******
    """
    # Apps we're using.
    webskine = Webskine(title, dsn, entries)
    jsonstore = JSONStore(dsn) 

    # Add authentication to the JSON store.
    def authfunc(environ, realm, username):
        return digest_password(realm, user, password)
    jsonstore = AuthDigestHandler(jsonstore, title, authfunc)

    # Pass application/json requests to jsonstore, all others to webskine.
    mapping = [ ('application/json', jsonstore),
                ('.*', webskine) ]

    app = ContentMiddleware(mapping)
    return app


class Webskine(object):
    def __init__(self, title, dsn, entries):
        self.title = title
        self.entries = entries

        # Get entry manager.
        self.em = EntryManager(dsn)

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

        # Parse request.
        dispatchers = [ ('/atom', lambda d: self._atom()),
                        ('/(?P<id>\d+)?', lambda d: self._entry(**d)), ]
        path_info = environ.get('PATH_INFO', '/')
        for regexp, func in dispatchers:
            p = re.compile(regexp)
            m = p.match(path_info)
            if m:
                reqdict = m.groupdict()
                return func(reqdict)
        
        # Raise 404.
        raise httpexceptions.HTTPNotFound()

    def _entry(self, id):
        """
        Return entry or list of entries.

        Return a single entry if id is specified. Otherwise,
        return last self.entries entries.
        """
        if id is None:  
            entries = self.em.get_entries(self.entries)
        else:
            try:
                entries = [self.em.get_entry(id)]
            except KeyError:
                raise httpexceptions.HTTPNotFound()

        # Update entry with a proper id (pointing to the resource location)
        # and a nicely formated updated timestamp.
        location = construct_url(self.environ, with_query_string=False, with_path_info=False) + '/'
        now = datetime.datetime.utcnow()
        for entry in entries:
            entry['id'] = urljoin(location, entry['id'])
            entry.setdefault('content', {'content': ''})
            
        namespace = {'title': self.title, 'home': location, 'entries': entries}
        output = xhtml.xhtml(searchList=[namespace], filter='EncodeUnicode')
        output = str(output)

        headers = [('Content-Encoding', 'utf-8'),
                   ('Content-Type', 'text/html')]
        self.start('200 OK', headers)
        return [output] 

    def _atom(self):
        """
        Return an atom feed.
        """
        entries = self.em.get_entries(self.entries)

        # Update entry with a proper id (pointing to the resource location)
        # and a nicely formated updated timestamp.
        location = construct_url(self.environ, with_query_string=False, with_path_info=False) + '/'
        now = datetime.datetime.utcnow()
        for entry in entries:
            entry['id'] = urljoin(location, entry['id'])
            entry.setdefault('content', {'content': ''})

        namespace = {'title': self.title,
                     'feed': urljoin(location, 'atom'),
                     'updated': entries[0]['updated'],
                     'home': location,
                     'entries': entries}
        output = atom.atom(searchList=[namespace], filter='EncodeUnicode')
        output = str(output)

        headers = [('Content-Encoding', 'utf-8'),
                   ('Content-Type', 'application/atom+xml')]
        self.start('200 OK', headers)
        return [output]

    def close(self):
        self.em.close()
