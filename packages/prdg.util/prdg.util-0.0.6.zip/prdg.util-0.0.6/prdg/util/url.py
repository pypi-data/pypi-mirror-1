"""URL utils."""
from urllib import urlencode
from logging import getLogger

import rbco.commandwrap.decorators as cmdwrap

log = getLogger(__name__)

@cmdwrap.retain_only_output
@cmdwrap.check_status
@cmdwrap.run_command
@cmdwrap.wrap_command(
    'wget -qO- --post-data="%(post_data)s" %(kwargs)s %(url)s'
)
def wget(url=None, post_data='', **kwargs):
    """wget wrapper"""

def urlread(host, protocol='http', port=80, path='', username=None, 
    password=None, post_data={}):
    """
    Return: open the given `url` and read it, returning the result. 
        `data_dict` is a mapping containing data to be POSTed. 
    """
    url = compose(host, protocol, port, path, username, password)
    
    log.info('Reading %s' % url)
      
    post_data_str = urlencode(post_data)    
    return wget(url, post_data_str)


def compose(host, protocol='http', port=None, path='', username=None, 
    password=None):
    """Create a URL."""
    
    url = protocol + '://'
    
    if username:
        if not password:
            raise ValueError('password must be given if username is')
        
        url += '%s:%s@' % (username, password)
    
    url += host
    if port is not None:
        url += ':' + str(port)
    if path:
        url = remove_slash_end(url) + '/' + remove_slash_start(path)
                    
    return url

def decompose(url):
    """Decompose a URL."""
    parts = url.split('://', 1)        
    protocol = parts[0]
    url = parts[1]
    if '/' not in url:
        url += '/'
    
    parts = url.split('/', 1)
    host = parts[0]
    path = parts[1]
        
    if ':' in host:
        parts = host.split(':', 1)
        host = parts[0]
        port = parts[1]
    else:
        port = None
    
    return (protocol, host, port, path)

def get_path(url):
    """Return the path component of a URL."""
    return decompose(url)[-1]

def remove_slash_end(url):
    """Remove '/' from the end of the string, if any."""
    return (url.endswith('/') and url[:-1]) or url

def remove_slash_start(url):
    """Remove '/' from the start of the string, if any."""
    return (url.startswith('/') and url[1:]) or url