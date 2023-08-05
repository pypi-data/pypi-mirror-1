"""
This module defines the WSGI entry point for this application.
"""

from paste.urlmap import URLMap
from paste.urlparser import make_static

from beaker.cache import CacheMiddleware

def make_app(global_conf, store = 'core', app = 'core', renderer = 'core', **kw):
    brightcontent = __import__('brightcontent.%s.store' % store)
    store = getattr(getattr(brightcontent, store), 'store')
    store = store.flatfile_repository(kw['store_config'])

    brightcontent = __import__('brightcontent.%s.app' % app)
    app = getattr(getattr(brightcontent, app), 'app')

    brightcontent = __import__('brightcontent.%s.renderer' % renderer)
    renderer = getattr(getattr(brightcontent, renderer), 'renderer')

    app = renderer.FeedRenderer(app.WSGIApplication(store))
    app = CacheMiddleware(app, global_conf)

    static = make_static(global_conf, 'brightcontent/static')

    urlmap = URLMap()
    urlmap['/'] = app
    urlmap['/static'] = static

    return urlmap
