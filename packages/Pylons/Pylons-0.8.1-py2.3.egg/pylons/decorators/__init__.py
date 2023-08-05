"""Custom Decorators, currently ``jsonify``"""

import pylons
import simplejson as json
import rest

def jsonify(func):
    """Action decorator that formats output for JSON
    
    Given a function that will return content, this decorator will
    turn the result into JSON, with a content-type of 'text/javascript'
    and output it.
    """
    def decorator(*args, **kw):
        pylons.request.content_type = 'text/javascript'
        return pylons.m.write(json.dumps(func(*args, **kw)))
    decorator._orig = getattr(func, '_orig', func)
    return decorator

__all__ = ['jsonify']
