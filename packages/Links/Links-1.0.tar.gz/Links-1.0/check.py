try:
    import httplib as _httplib
    import urlparse as _urlparse
except ImportError: # 3.x!
    import urllib.parse as _urlparse
    import http.client as _httplib

def _get_connection(link, *args):
    pieces = _urlparse.urlsplit(link)
    scheme, netloc, path_pieces = pieces[0], pieces[1], pieces[2:]
    path = _urlparse.urlunsplit(('', '') + path_pieces)
    if not path[0] == '/':
        path = '/' + path
    if scheme == 'http':
        return _httplib.HTTPConnection(netloc, *args), path
    if scheme == 'https':
        return _httplib.HTTPSConnection(netloc, *args), path
    # else raise error

def linkstatus(link):
    """Return the HTTP status code for the link, see httplib.responses"""
    connection, path = _get_connection(link)
    connection.request('HEAD', path)
    status = connection.getresponse().status
    connection.close()
    return status

