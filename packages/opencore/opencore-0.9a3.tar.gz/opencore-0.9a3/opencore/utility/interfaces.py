from zope.interface import Interface

class IHTTPClient(Interface):
    """
    An HTTP client that promises to handle all methods, caching,
    ETags, compression, HTTPS, Basic, Digest, WSSE, etc.
    """
      
    def __init__(self, cache=None, timeout=None):
        """init"""
      
    def add_certificate(self, key, cert, domain):
        """Add a key and cert that will be used
        any time a request requires authentication."""
      
    def add_credentials(self, name, password, domain=''):
          """Add a name and password that will be used
          any time a request requires authentication."""
      
    def clear_credentials(self):
          """Remove all the names and passwords
          that are used for authentication"""
      
    def request(self, uri, method='GET', body=None, headers=None, redirections=5):
        """
        Performs a single HTTP request.
        The 'uri' is the URI of the HTTP resource and can begin 
        with either 'http' or 'https'. The value of 'uri' must be an absolute URI.
        
        The 'method' is the HTTP method to perform, such as GET, POST, DELETE, etc. 
        There is no restriction on the methods allowed.
        
        The 'body' is the entity body to be sent with the request. It is a string
        object.
          
        Any extra headers that are to be sent with the request should be provided in the
        'headers' dictionary.
          
        The maximum number of redirect to follow before raising an 
        exception is 'redirections. The default is 5.
          
        The return value is a tuple of (response, content), the first 
        being and instance of the 'Response' class, the second being 
        a string that contains the response entity body.
        """

