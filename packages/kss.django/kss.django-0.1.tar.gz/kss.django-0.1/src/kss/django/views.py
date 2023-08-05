from django.http import HttpResponse, Http404
from django.utils.cache import patch_response_headers
from django.core.cache import cache
from django.middleware.gzip import GZipMiddleware

from kss.base import javascript

cache_time = 60 * 60 * 24 * 30

def kss_js(request):
    from django.conf import settings

    concatinated = cache.get('kss.js')
    if concatinated is None:
        debug = getattr(settings, 'KSS_DEBUG', False)
        if debug:
            compression = None
        else:
            compression = 'safe'

        concatinated = javascript.packed(compression_level=compression)
        # Do not cache the KSS Javascript when in debug mode
        if not debug:
            cache.set('kss.js', concatinated, cache_time)

    response = HttpResponse(concatinated, mimetype='text/javascript')

    patch_response_headers(response, cache_time)

    gzip_middleware = GZipMiddleware()
    return gzip_middleware.process_response(request, response)

def extra_js(request, js_name):
    extra_jsscripts = javascript.extra_scripts()
    if js_name not in extra_jsscripts:
        raise Http404

    response = HttpResponse(extra_jsscripts[js_name], 
                            mimetype='text/javascript')

    patch_response_headers(response, cache_time)
    gzip_middleware = GZipMiddleware()
    return gzip_middleware.process_response(request, response)

