
"""

utils.py
========

Misc utilities for ternate
--------------------------

General purpose helper functions and classes for ternate

License: GPL-2

"""

#pylint: disable-msg=C0103

import logging
from urllib2 import build_opener, HTTPError, ProxyHandler, URLError


__docformat__ = 'epytext'

LOG = logging.getLogger('ternate')

COLOR = {'normal': "\033[0m",
          'bold': "\033[1m",
          'underline': "\033[4m",
          'blink': "\033[5m",
          'reverse': "\033[7m",
          'black': "\033[30m",
          'red': "\033[31m",
          'green': "\033[32m",
          'yellow': "\033[33m",
          'blue': "\033[34m",
          'magenta': "\033[35m",
          'cyan': "\033[36m",
          'white': "\033[37m"}


class NotFoundError(Exception):

    '''File not found'''

    #pylint: disable-msg=W0231
    def __init__(self, err_msg):
        '''Initialize attributes'''
        self.err_msg = err_msg

    def __str__(self):
        return repr(self.err_msg)


def fetch_file(url, proxy=None):
    '''
    Download file by URL

    @param url: URL of a file
    @type url: string

    @param proxy: URL of HTTP Proxy
    @type proxy: string

    @return: File
    @rtype: string

    '''
    if not url.startswith('http://') and not url.startswith('ftp://'):
        try:
            return open(url, 'r').read()
        except IOError, errmsg:
            LOG.error(errmsg)
            return ''
    LOG.debug('Fetching ' + url)
    if proxy:
        opener = build_opener(ProxyHandler({'http': proxy}))
    else:
        opener = build_opener()
    opener.addheaders = [('Accept', 'application/rdf+xml'),
            ('User-agent',
             'Mozilla/5.0 (compatible; ternate ' +
             'http://trac.assembla.com/ternate)')]
    try:
        result = opener.open(url)
    except HTTPError, err_msg:
        if err_msg.code == 404:
            raise NotFoundError('Not found: %s' % url)
        else:
            LOG.error(err_msg)
            return
    except URLError, err_msg:
        LOG.error(err_msg)
        return
    return result.read()


if __name__ == '__main__':
    import doctest
    doctest.testmod()

