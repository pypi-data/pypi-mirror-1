# -*- coding: utf-8 -*-
from django.conf import settings
from django_cachepurge import clear_urls, get_urls
from django_cachepurge.utils import pruneAsync

CACHE_URLS = settings.CACHE_URLS

if isinstance(CACHE_URLS, basestring):
    CACHE_URLS = (CACHE_URLS,)

class CachePurge(object):
    """ Middleware responsible of sending PURGE to upstream cache(s)
    """
    def process_request(self, request):
        clear_urls()

    def process_response(self, request, response):

        for url in get_urls():
            for cache in CACHE_URLS:
                url_in_cache = "%s%s" % (cache, url)

                pruneAsync(url_in_cache)

        return response
