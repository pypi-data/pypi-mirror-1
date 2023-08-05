# Copyright (c) 2005, the Lawrence Journal-World
# Copyright (c) 2006 L. C. Rees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Django nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Memcached cache backend'''

import memcache

from wsgistate import BaseCache
from wsgistate.cache import WsgiMemoize
from wsgistate.session import CookieSession, URLSession, SessionCache

__all__ = ['MemCached', 'memoize', 'session', 'urlsession']

def mcmemo_deploy(global_conf, **kw):
    '''Paste Deploy loader for caching.'''
    def decorator(application):
        _mc_memo_cache = MemCached(kw.get('cache'), **kw)
        return WsgiMemoize(application, _mc_memo_cache, **kw)
    return decorator

def mcsess_deploy(global_conf, **kw):
    '''Paste Deploy loader for sessions.'''
    def decorator(application):
        _mc_base_cache = MemCached(kw.get('cache'), **kw)
        _mc_session_cache = SessionCache(_mc_base_cache, **kw)
        return CookieSession(application, _mc_session_cache, **kw)
    return decorator

def mcurlsess_deploy(global_conf, **kw):
    '''Paste Deploy loader for URL encoded sessions.

    @param initstr Database initialization string
    '''
    def decorator(application):
        _mc_ubase_cache = MemCached(kw.get('cache'), **kw)
        _mc_url_cache = SessionCache(_mc_ubase_cache, **kw)
        return URLSession(application, _mc_url_cache, **kw)
    return decorator

def memoize(path, **kw):
    '''Decorator for caching.

    @param path Client path
    '''
    def decorator(application):
        _mc_memo_cache = MemCached(path, **kw)
        return WsgiMemoize(application, _mc_memo_cache, **kw)
    return decorator

def session(path, **kw):
    '''Decorator for sessions.

    @param path Client path
    '''
    def decorator(application):
        _mc_base_cache = MemCached(path, **kw)
        _mc_session_cache = SessionCache(_mc_base_cache, **kw)
        return CookieSession(application, _mc_session_cache, **kw)
    return decorator

def urlsession(path, **kw):
    '''Decorator for URL encoded sessions.

    @param path Client path
    '''
    def decorator(application):
        _mc_ubase_cache = MemCached(path, **kw)
        _mc_url_cache = SessionCache(_mc_ubase_cache, **kw)
        return URLSession(application, _mc_url_cache, **kw)
    return decorator


class MemCached(BaseCache):

    '''Memcached cache backend'''

    def __init__(self, *a, **kw):
        super(MemCached, self).__init__(*a, **kw)
        self._cache = memcache.Client(a[0].split(';'))

    def get(self, key, default=None):
        '''Fetch a given key from the cache.  If the key does not exist, return
        default, which itself defaults to None.

        @param key Keyword of item in cache.
        @param default Default value (default: None)
        '''
        val = self._cache.get(key)
        if val is None: return default
        return val

    def set(self, key, value):
        '''Set a value in the cache.

        @param key Keyword of item in cache.
        @param value Value to be inserted in cache.
        '''
        self._cache.set(key, value, self.timeout)

    def delete(self, key):
        '''Delete a key from the cache, failing silently.

        @param key Keyword of item in cache.
        '''
        self._cache.delete(key)

    def get_many(self, keys):
        '''Fetch a bunch of keys from the cache.

        Returns a dict mapping each key in keys to its value.  If the given
        key is missing, it will be missing from the response dict.

        @param keys Keywords of items in cache.
        '''
        return self._cache.get_multi(keys)

    def _cull(self):
        '''Stub.'''
        pass