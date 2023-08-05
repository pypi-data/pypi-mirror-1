# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import re
import posixpath
import sys
from StringIO import StringIO
from urllib import quote, unquote
from datetime import datetime, timedelta
try:
    set = set
    frozenset = frozenset
except:
    from sets import Set as set
    from sets import ImmutableSet as frozenset


__all__ = """
set frozenset
quote unquote
URI TimingFilter
""".split()

class URI(object):
    """Parse a URI into its component parts. The `query` component is passed
    through `cgi.parse_qs()`.

        scheme://username:password@host/path?query#fragment

    Each component is available as an attribute of the object.

    TODO: Support "parameters???" Never seen this in the wild:
        scheme://username:password@host/path;parameters?query#fragment

    PS. `urlparse` is not useful.

    The URI constructor can be passed a string:

    >>> u = URI('http://user:password@www.example.com/some/path?parm=1&parm=2&other=3#fragment')
    >>> u
    URI(u'http://user:password@www.example.com/some/path?other=3&parm=1&parm=2#fragment')
    >>> u.scheme
    'http'
    >>> u.username
    'user'
    >>> u.password
    'password'
    >>> u.host
    'www.example.com'
    >>> u.path
    '/some/path'
    >>> u.query
    {'parm': ['1', '2'], 'other': ['3']}
    >>> u.fragment
    'fragment'

    ...or the individual URI components as keyword arguments:

    >>> URI(scheme='http', username='user', password='password', host='www.example.com', path='/some/path', query={'parm': [1, 2], 'other': [3]}, fragment='fragment')
    URI(u'http://user:password@www.example.com/some/path?other=3&parm=1&parm=2#fragment')

    ...or finally, another URI object:

    >>> v = URI(u)
    >>> v == u
    True
    >>> v.query is u.query
    False
    >>> v
    URI(u'http://user:password@www.example.com/some/path?other=3&parm=1&parm=2#fragment')

    URI also normalises the path component:

    >>> URI('http://www.example.com//some/../foo/path/')
    URI(u'http://www.example.com/foo/path')
    """

    _pattern = re.compile(r'(?:(?P<scheme>[^:]+)://)?(?:(?P<username>[^:@]*)(?::(?P<password>[^@]*))?@)?(?P<host>[^?/#:]*)(?::(P<port>[\d+]+))?(?P<path>/[^#?]*)?(?:\?(?P<query>[^#]*))?(?:#(?P<fragment>.*))?')

    __slots__ = ('scheme', 'username', 'password', 'host', 'port', '_path',
                 'query', 'fragment')

    def __init__(self, uri=None, scheme='', username='', password='', host='',
                 port='', path='', query={}, fragment=''):
        self._path = ''
        # Copy attributes of a URI object
        if isinstance(uri, URI):
            from copy import copy
            self.scheme, self.username, self.password, self.host, self.port, \
                self.path, self.query, self.fragment = \
                    uri.scheme, uri.username, uri.password, uri.host, \
                    uri.port, uri.path, copy(uri.query), uri.fragment
        elif uri is not None:
            # Parse URI string
            from cgi import parse_qs

            match = self._pattern.match(uri)
            if match is None:
                raise ValueError('Invalid URI')
            groups = [g or '' for g in match.groups()]
            groups = map(unquote, groups[0:6]) + \
                     [parse_qs(groups[6] or '')] + \
                     map(unquote, groups[7:])
            self.scheme, self.username, self.password, self.host, self.port, \
                self.path, self.query, self.fragment = groups
        else:
            # Explicitly provide URI components
            self.scheme, self.username, self.password, self.host, self.port, \
                self.path, self.query, self.fragment = scheme, username, \
                    password, host, port, path, query, fragment

    def _set_path(self, path):
        """Return a normalised path.
        """
        if path:
            self._path = '/' + posixpath.normpath(path).lstrip('/')
        else:
            self._path = ''

    def _get_path(self):
        return self._path

    path = property(_get_path, _set_path)

    def __cmp__(self, other):
        """Compare two URI objects.

        >>> u = URI('http://user:password@www.example.com/some/path?parm=1&parm=2&other=3#fragment')
        >>> v = URI(u)
        >>> u == v
        True
        >>> v.host = 'www.google.com'
        >>> u == v
        False
        """
        return cmp(repr(self), repr(other))

    def __repr__(self):
        return "URI(u'%s')" % unicode(self)

    def __str__(self):
        uri = unicode(self.scheme and (quote(self.scheme) + u'://') or u'')
        if self.username or self.password:
            if self.username:
                uri += quote(self.username)
            if self.password:
                uri += u':' + quote(self.password)
            uri += u'@'
        uri += quote(self.host)
        if self.port:
            uri += u':%s' % port
        uri += quote(self.path)
        if self.query:
            uri += u'?' + u'&'.join([u'&'.join([u'%s=%s' % (k, quote(str(v)))
                                                for v in l])
                                     for k, l in sorted(self.query.items())])
        if self.fragment:
            uri += u'#' + quote(self.fragment)
        return uri


class TimingFilter(object):
    """A Framework filter for collecting timing statistics."""
    def __init__(self, next_filter=None, progressive=False):
        """`next_filter` is the next filter in the chain.

        `progressive` will print statistics while the indexer is running."""
        if next_filter:
            self.next_filter = next_filter
        self.times = []
        self.total = timedelta()
        self.average = timedelta()
        self.progressive = progressive

    def next_filter(self, framework, context, stream):
        for transition, uri in stream:
            yield transition, uri

    def __call__(self, framework, context, stream):
        self.times = []
        for transition, uri in self.next_filter(framework, context, stream):
            start = datetime.now()
            yield transition, uri
            end = datetime.now()
            line = (transition, uri, start, end)
            self.times.append(line)
            if self.progressive:
                self.print_line(*line)

        self.total = timedelta()
        self.average = timedelta()
        for transition, uri, start, end in self.times:
            self.total += end - start
        if self.total:
            self.average = self.total / len(self.times)
        if self.progressive:
            self.print_summary()

    def print_line(self, transition, uri, start, end, out=sys.stdout):
        from pyndexter import MODIFIED, ADDED, REMOVED
        mapping = {MODIFIED: 'MODIFIED', ADDED: 'ADDED', REMOVED: 'REMOVED'}
        print >>out, '%s %s (in %s)' % (mapping[transition], uri, end - start)

    def print_summary(self, out=sys.stdout):
        print >>out
        print >>out, "Indexed %i documents" % len(self.times)
        print >>out, 'Total time to index: %s' % self.total
        print >>out, 'Average time to index: %s' % self.average

    def __str__(self):
        from StringIO import StringIO
        out = StringIO()
        for transition, uri, start, end in self.times:
            self.print_line(transition, uri, start, end, out=out)
        self.print_summary(out)
        return out.getvalue()
