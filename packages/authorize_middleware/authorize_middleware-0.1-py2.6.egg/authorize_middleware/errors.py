from paste import httpexceptions

class NotAuthenticatedError(httpexceptions.HTTPClientError):
    """
    Raised when a permission check fails because the user is not authenticated.

    The exception is caught by the ``httpexceptions`` middleware and converted into
    a ``401`` HTTP response which is intercepted by the authentication middleware
    triggering a sign in.
    """
    required_headers = ()
    code = 401
    title = 'Not Authenticated'

class NotAuthorizedError(httpexceptions.HTTPClientError):
    """
    Raised when a permission check fails because the user is not authorized.

    The exception is caught by the ``httpexceptions`` middleware and converted into
    a ``403`` HTTP response which is intercepted by the authentication middleware
    triggering a sign in.
    """
    code = 403
    title = 'Forbidden'
    explanation = ('Access was denied to this resource.')
