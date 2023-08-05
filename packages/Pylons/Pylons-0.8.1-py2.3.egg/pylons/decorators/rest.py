"""REST decorators"""

import pylons

def restrict(*methods):
    """Restricts access to the function depending on HTTP method
    
    Takes a list of HTTP methods that are allowed for the action, and
    returns a HTTP 405 Method Not Allowed if the action does not accept
    that method.
    
    Example::
        
        from pylons.decorators import rest
        
        class SomeController(BaseController):
            
            @rest.restrict('POST')
            def comment(self, id):
                # Only runs if its a POST
            
            @rest.restrict('POST','GET')
            def view(self, post):
                # Runs if method is POST or GET
    
    """
    def check_methods(func):
        def new_func(*args, **kw):
            pylons.request.headers_out['Allow'] = ','.join(methods)
            if pylons.request.method not in methods:
                return pylons.m.abort('405', reason='Method Not Allowed')
            return func(*args, **kw)
        new_func._orig = getattr(func, '_orig', func)
        return new_func
    return check_methods

def dispatch_on(**method_map):
    """Dispatches to alternate controller methods based on HTTP method
    
    Multiple keyword arguments should be passed, with the keyword corresponding
    to the HTTP method to dispatch on (DELETE, POST, GET, etc.) and the
    value being the function to call. The value should *not* be a string, but
    the actual function object that should be called.
    
    Example::
        
        from pylons.decorators import rest
        
        class SomeController(BaseController):
            
            @rest.dispatch_on(POST=create_comment)
            def comment(self, id):
                # Do something with the comment
            
            def create_comment(self, id):
                # Do something if its a post to comment
    
    **Please Note:** Due to how the argument inspection process works for
    methods, any desired function args must be present in the decorated
    function for them to be available in the dispatched function. The
    dispatched method can however have less arguments than the decorated
    one.
    
    """
    def dispatcher(func):
        def new_func(self, *args, **kw):
            alt_method = method_map.get(pylons.request.method)
            if alt_method:
                alt_method = getattr(self, alt_method)
                return self._inspect_call(alt_method, **kw)
            return func(self, *args, **kw)
        new_func._orig = getattr(func, '_orig', func)
        return new_func
    return dispatcher

__all__ = ['restrict', 'dispatch_on']
