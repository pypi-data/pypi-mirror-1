import re
import os.path
import datetime
from urlparse import urljoin
from cgi import escape
import md5

from paste import httpexceptions
from paste.request import construct_url
from Cheetah.Template import Template

from jsonstore import EntryManager


def make_app(global_conf, store, templates,
        cache='simple://',
        index='index.db',
        title='Test Webskine installation',
        entries=10,
        user='test',
        password='test'):
    """
    Create a weblog.

    Configuration should be like this::

        [app:webskine]
        use = egg:webskine
        title = Test Webskine installation
        store = sqlite:///%(here)s/entries.db
        cache = simple://
        index = %(here)s/index.db
        templates = %(here)s/templates/
        entries = 10
        user = test
        password = test
    """
    from paste.auth.digest import digest_password, AuthDigestHandler

    from webskine.middleware import ContentMiddleware
    from jsonstore import JSONStore

    # Apps we're using.
    conf = {'store': store, 'cache': cache, 'index': index}
    jsonstore = JSONStore(**conf)
    webskine = Webskine(jsonstore.em, templates, title, entries)

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
    def __init__(self, em, templates, title, entries):
        self.templates = templates
        self.title = title
        self.entries = entries

        # Get entry manager.
        self.em = em

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '/')

        # Parse request.
        dispatchers = [ ('/atom', lambda d: self._atom(**d)),
                        ('/(?P<id>.+)?', lambda d: self._entry(**d)), ]
        for regexp, func in dispatchers:
            p = re.compile(regexp)
            m = p.match(path_info)
            if m:
                reqdict = m.groupdict()
                reqdict['environ'] = environ
                reqdict['start_response'] = start_response
                return func(reqdict)
        
        # Raise 404.
        raise httpexceptions.HTTPNotFound()

    def _entry(self, id, environ, start_response):
        """
        Return entry or list of entries.

        Return a single entry if id is specified. Otherwise,
        return last self.entries entries.
        """
        if id is None:  
            entries = self.em.search(size=self.entries)
            title = self.title
        else:
            try:
                entry = self.em.search(__id__=str(id))[0]
                entries = [entry]
                title = entry['title']
            except KeyError:
                raise httpexceptions.HTTPNotFound()

        # Update entry with a proper id (pointing to the resource location).
        location = construct_url(environ, with_query_string=False, with_path_info=False) + '/'
        namespace = {'name': self.title, 'title': title, 'home': location, 'entries': entries}
        template = Template(file=os.path.join(self.templates, 'xhtml.tmpl'),
                searchList=[namespace], filter='EncodeUnicode')

        headers = [('Content-Encoding', 'utf-8'),
                   ('Content-Type', 'text/html')]
        start_response('200 OK', headers)
        return [str(template)] 

    def _atom(self, environ, start_response):
        """
        Return an atom feed.
        """
        entries = self.em.search(size=self.entries)

        # Update entry with a proper id (pointing to the resource location).
        location = construct_url(environ, with_query_string=False, with_path_info=False) + '/'
        namespace = {'title': self.title,
                     'feed': urljoin(location, 'atom'),
                     'updated': entries[0]['__updated__'],
                     'home': location,
                     'entries': entries}
        template = Template(file=os.path.join(self.templates, 'atom.tmpl'),
                searchList=[namespace], filter='EncodeUnicode')

        headers = [('Content-Encoding', 'utf-8'),
                   ('Content-Type', 'application/atom+xml')]
        start_response('200 OK', headers)
        return [str(template)]
