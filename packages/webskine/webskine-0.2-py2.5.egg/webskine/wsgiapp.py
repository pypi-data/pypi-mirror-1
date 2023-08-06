import re
import os.path
import datetime
from urlparse import urljoin
from cgi import escape
import md5

from paste import httpexceptions
from paste.request import construct_url, parse_dict_querystring
from paste.urlmap import URLMap
from paste.auth.digest import digest_password, AuthDigestHandler
from Cheetah.Template import Template

from jsonstore import JSONStore


def make_app(global_conf, store, templates,
        cache='simple://',
        index='index.db',
        title='Test Webskine installation',
        entries=10,
        user='test',
        password='test'):

    store = JSONStore(store=store, cache=cache, index=index)
    def authfunc(environ, realm, username):
        return digest_password(realm, user, password)

    app = URLMap()
    app['/json'] = AuthDigestHandler(store, title, authfunc)
    app['/'] = Webskine(store, templates, title, entries)
    return app


class Webskine(object):
    def __init__(self, store, templates, title, entries):
        self.templates = templates
        self.title = title
        self.entries = entries

        # Get entry manager.
        self.em = store.em

    def __call__(self, environ, start_response):
        id_ = environ.get('PATH_INFO', '/').lstrip('/')
        qs = parse_dict_querystring(environ)
        template_name = qs.get('t', 'xhtml')

        if id_:
            try:
                entry = self.em.search(__id__=id_)[0]
                entries = [entry]
                title = entry['title']
            except KeyError:
                raise httpexceptions.HTTPNotFound()
        else:
            entries = self.em.search(size=self.entries)
            title = self.title
        
        # Update entry with a proper id (pointing to the resource location).
        location = construct_url(environ, with_query_string=False, with_path_info=False) + '/'
        namespace = {
            'name': self.title,
            'title': title,
            'home': location,
            'entries': entries,
        }
        template = Template(
                file=os.path.join(self.templates, '%s.tmpl' % template_name),
                searchList=[namespace],
                filter='EncodeUnicode')

        headers = [('Content-Encoding', 'utf-8')]
        start_response('200 OK', headers)
        return [str(template)] 
