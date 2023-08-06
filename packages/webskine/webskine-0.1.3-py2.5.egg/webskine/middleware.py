import re

class ContentMiddleware(object):
    def __init__(self, mapping):
        self.mapping = mapping

    def __call__(self, environ, start_response):
        content = environ.get('CONTENT_TYPE', '') or environ.get('HTTP_ACCEPT', '')
        content = content.split(';')[0]
        
        for type, app in self.mapping:
            if re.match(type, content): return app(environ, start_response)
