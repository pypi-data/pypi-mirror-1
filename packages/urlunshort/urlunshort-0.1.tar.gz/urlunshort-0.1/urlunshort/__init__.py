"""
Urlunshort un-shortens URLs that have been created using one of the many URL
shortening services, like tinurl, bit.ly etc.
"""

__version__ = "0.1"
__author__ = "Rune Halvorsen <runefh@gmail.com>"
__homepage__ = "http://bitbucket.org/runeh/urlunshort"

import urlparse
from resolvers import generic_resolver

# If some tiny url services require a special resolver, this mapping will
# map between hostname -> resolver
_resolver_map = {

}


def resolve(url, timeout=None):
    """
    Resolve url, being a shortened url, to a destination url. If the url could
    not be resolved, return None. The optional timout
    """
    parts = urlparse.urlparse(url)
    resolver = _resolver_map.get(parts.netloc, generic_resolver)
    return resolver(parts.netloc, parts.path, timeout)
