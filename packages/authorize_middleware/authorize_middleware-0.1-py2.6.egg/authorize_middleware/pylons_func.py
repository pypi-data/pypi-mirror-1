from decorator import decorator
from pylons import request
from errors import *
from auth import authorize_request


def authorize(function=None):
    """
    This is a decorator which can be used to decorate a Pylons controller action.
    It gives function ``function`` environ dictionary and executes it. Function
    should return either True or False.
    """
    def validate(func, self, *args, **kwargs):
        authorize_request(request.environ, function)
        return func(self, *args, **kwargs)
    return decorator(validate)

def authorized(function=None):
    """
    Similar to the ``authorize_request()`` function with no access to the
    request but rather than raising an exception to stop the request if a
    authorization check fails, this function simply returns ``False`` so that you
    can test permissions in your code without triggering a sign in. It can
    therefore be used in a controller action or template.

    Use like this::

        if authorized(function):
            return Response('You are authorized')
        else:
            return Response('Access denied')
 
    """
    try:
        authorize_request(request.environ, function)
    except (NotAuthorizedError, NotAuthenticatedError):
        return False
    else:
        return True
