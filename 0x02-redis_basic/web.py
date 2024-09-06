#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
'''The module-level Redis instance.
'''


def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data and tracks the number of accesses.
    '''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output and tracking accesses.
        '''
        # Increment the count of how many times this URL was accessed
        redis_store.incr(f'count:{url}')
        
        # Check if the result for this URL is already cached
        cached_result = redis_store.get(f'result:{url}')
        if cached_result:
            return cached_result.decode('utf-8')
        
        # If not cached, fetch the content from the URL
        result = method(url)
        
        # Cache the result for 10 seconds
        redis_store.setex(f'result:{url}', 10, result)
        
        return result
    
    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    response = requests.get(url)
    return response.text

