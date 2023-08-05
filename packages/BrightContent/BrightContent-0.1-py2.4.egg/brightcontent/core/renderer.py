from Ft.Xml.Xslt import Transform
from brightcontent.util import get_base_url

XSL = 'brightcontent/static/bluesky/index.xslt'
BC_NS = 'http://brightcontent.net/ns/'

class FeedRenderer(object):
    def __init__(self, application):
        self.application = application

    def start_response(self, status, headers, exc_info=None):
        self.status = status
        self.headers = headers
        self.exc_info = exc_info

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        cache = environ['beaker.cache'].get_cache('brightcontent')
        try:
            result = cache.get_value(path)
        except:
            result = self.application(environ, self.start_response)
            if environ.get('brightcontent.render', False):
                #self.headers = [('Content-type', 'application/xhtml+xml')]
                self.headers = [('Content-type', 'text/html')]
                #expose the environment within XSLT
                params = dict([ ((BC_NS, k), environ[k]) for k in environ])
                params[(BC_NS, u'weblog-base-uri')] = get_base_url(environ)
                result = Transform(''.join(result[0]), XSL, params=params)
            if isinstance(result, str):
                result = [result]
            cache.set_value(path, result)
        start_response(self.status, self.headers, self.exc_info)
        return result

