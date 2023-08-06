from errors import *

def authorize_request(environ, function=None):
    """
    This function can be used within a controller action to ensure that no code 
    after the function call is executed if the user doesn't pass the permission
    check in function ``function``.
    """

    if 'REMOTE_USER' not in environ:
        raise NotAuthenticatedError('Not Authenticated')
    elif function is not None and not function(environ):
        raise NotAuthorizedError('Not Authorized')
