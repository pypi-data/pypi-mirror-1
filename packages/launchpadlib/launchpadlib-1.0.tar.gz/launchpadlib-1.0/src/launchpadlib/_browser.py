# Copyright 2008 Canonical Ltd.

# This file is part of launchpadlib.
#
# launchpadlib is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# launchpadlib is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with launchpadlib. If not, see <http://www.gnu.org/licenses/>.

"""Browser object to make requests of Launchpad web service.

The `Browser` class implements OAuth authenticated communications with
Launchpad.  It is not part of the public launchpadlib API.
"""

__metaclass__ = type
__all__ = [
    'Browser',
    ]


import atexit
from cStringIO import StringIO
import gzip
from httplib2 import (
    FailedToDecompressContent, FileCache, Http, safename, urlnorm)
from lazr.uri import URI
from oauth.oauth import (
    OAuthRequest, OAuthSignatureMethod_PLAINTEXT)
import shutil
import simplejson
import tempfile
from urllib import urlencode
from wadllib.application import Application
import zlib

from launchpadlib.errors import HTTPError
from launchpadlib._json import DatetimeJSONEncoder


OAUTH_REALM = 'https://api.launchpad.net'

# A drop-in replacement for httplib2's _decompressContent, which looks
# in the Transfer-Encoding header instead of in Content-Encoding.
def _decompressContent(response, new_content):
    content = new_content
    try:
        encoding = response.get('transfer-encoding', None)
        if encoding in ['gzip', 'deflate']:
            if encoding == 'gzip':
                content = gzip.GzipFile(
                    fileobj=StringIO.StringIO(new_content)).read()
            if encoding == 'deflate':
                content = zlib.decompress(content)
            response['content-length'] = str(len(content))
            del response['transfer-encoding']
    except IOError:
        content = ""
        raise FailedToDecompressContent(
            ("Content purported to be compressed with %s but failed "
             "to decompress." % response.get('transfer-encoding')),
            response, content)
    return content


class OAuthSigningHttp(Http):
    """A client that signs every outgoing request with OAuth credentials."""

    def __init__(self, oauth_credentials, cache=None, timeout=None,
                 proxy_info=None):
        self.oauth_credentials = oauth_credentials
        Http.__init__(self, cache, timeout, proxy_info)

    def _request(self, conn, host, absolute_uri, request_uri, method, body,
                 headers, redirections, cachekey):
        """Sign a request with OAuth credentials before sending it."""
        oauth_request = OAuthRequest.from_consumer_and_token(
            self.oauth_credentials.consumer,
            self.oauth_credentials.access_token,
            http_url=absolute_uri)
        oauth_request.sign_request(
            OAuthSignatureMethod_PLAINTEXT(),
            self.oauth_credentials.consumer,
            self.oauth_credentials.access_token)
        if headers.has_key('authorization'):
            # There's an authorization header left over from a
            # previous request that resulted in a redirect. Remove it
            # and start again.
            del headers['authorization']

        # httplib2 asks for compressed representations in
        # Accept-Encoding.  But a different content-encoding means a
        # different ETag, which can cause problems later when we make
        # a conditional request. We don't want to treat a
        # representation differently based on whether or not we asked
        # for a compressed version of it.
        #
        # So we move the compression request from Accept-Encoding to
        # TE. Transfer-encoding compression can be handled transparently.
        if 'accept-encoding' in headers:
            headers['te'] = 'deflate, gzip'
            del headers['accept-encoding']
        headers.update(oauth_request.to_header(OAUTH_REALM))
        return super(OAuthSigningHttp, self)._request(
            conn, host, absolute_uri, request_uri, method, body, headers,
            redirections, cachekey)

    def _conn_request(self, conn, request_uri, method, body, headers):
        """Decompress content using our version of _decompressContent."""
        response, content = super(OAuthSigningHttp, self)._conn_request(
            conn, request_uri, method, body, headers)
        # Decompress the response, if it was compressed.
        if method != "HEAD":
            content = _decompressContent(response, content)
        return (response, content)

    def _getCachedHeader(self, uri, header):
        """Retrieve a cached value for an HTTP header."""
        if isinstance(self.cache, MultipleRepresentationCache):
            return self.cache._getCachedHeader(uri, header)
        return None


class MultipleRepresentationCache(FileCache):
    """A cache that can hold different representations of the same resource.

    If a resource has two representations with two media types,
    FileCache will only store the most recently fetched
    representation. This cache can keep track of multiple
    representations of the same resource.

    This class works on the assumption that outside calling code sets
    an instance's request_media_type attribute to the value of the
    'Accept' header before initiating the request.

    This class is very much not thread-safe, but FileCache isn't
    thread-safe anyway.
    """
    def __init__(self, cache):
        """Tell FileCache to call append_media_type when generating keys."""
        super(MultipleRepresentationCache, self).__init__(
            cache, self.append_media_type)
        self.request_media_type = None

    def append_media_type(self, key):
        """Append the request media type to the cache key.

        This ensures that representations of the same resource will be
        cached separately, so long as they're served as different
        media types.
        """
        if self.request_media_type is not None:
            key = key + '-' + self.request_media_type
        return safename(key)


    def _getCachedHeader(self, uri, header):
        """Retrieve a cached value for an HTTP header."""
        (scheme, authority, request_uri, cachekey) = urlnorm(uri)
        cached_value = self.get(cachekey)
        header_start = header + ':'
        if cached_value is not None:
            for line in StringIO(cached_value):
                if line.startswith(header_start):
                    return line[len(header_start):].strip()
        return None


class Browser:
    """A class for making calls to Launchpad web services."""

    def __init__(self, credentials, cache=None, timeout=None,
                 proxy_info=None):
        """Initialize, possibly creating a cache.

        If no cache is provided, a temporary directory will be used as
        a cache. The temporary directory will be automatically removed
        when the Python process exits.
        """
        if cache is None:
            cache = tempfile.mkdtemp()
            atexit.register(shutil.rmtree, cache)
        if isinstance(cache, str):
            cache = MultipleRepresentationCache(cache)
        self._connection = OAuthSigningHttp(
            credentials, cache, timeout, proxy_info)

    def _request(self, url, data=None, method='GET',
                 media_type='application/json', extra_headers=None):
        """Create an authenticated request object."""
        # Add extra headers for the request.
        headers = {'Accept' : media_type}
        if isinstance(self._connection.cache, MultipleRepresentationCache):
            self._connection.cache.request_media_type = media_type
        if extra_headers is not None:
            headers.update(extra_headers)
        # Make the request. It will be signed automatically when
        # _request is called.
        response, content = self._connection.request(
            str(url), method=method, body=data, headers=headers)
        # Turn non-2xx responses into exceptions.
        if response.status // 100 != 2:
            raise HTTPError(response, content)
        return response, content

    def get(self, resource_or_uri, headers=None, return_response=False):
        """GET a representation of the given resource or URI."""
        if isinstance(resource_or_uri, (basestring, URI)):
            url = resource_or_uri
        else:
            method = resource_or_uri.get_method('get')
            url = method.build_request_url()
        response, content = self._request(url, extra_headers=headers)
        if return_response:
            return (response, content)
        return content

    def get_wadl_application(self, url):
        """GET a WADL representation of the resource at the requested url."""
        response, content = self._request(
            url, media_type='application/vd.sun.wadl+xml')
        return Application(str(url), content)

    def post(self, url, method_name, **kws):
        """POST a request to the web service."""
        kws['ws.op'] = method_name
        data = urlencode(kws)
        return self._request(url, data, 'POST')

    def put(self, url, representation, media_type, headers=None):
        """PUT the given representation to the URL."""
        extra_headers = {'Content-Type': media_type}
        if headers is not None:
            extra_headers.update(headers)
        return self._request(
            url, representation, 'PUT', extra_headers=extra_headers)

    def delete(self, url):
        """DELETE the resource at the given URL."""
        self._request(url, method='DELETE')

    def patch(self, url, representation, headers=None):
        """PATCH the object at url with the updated representation."""
        extra_headers = {'Content-Type': 'application/json'}
        if headers is not None:
            extra_headers.update(headers)
        # httplib2 doesn't know about the PATCH method, so we need to
        # do some work ourselves. Pull any cached value of "ETag" out
        # and use it as the value for "If-Match".
        cached_etag = self._connection._getCachedHeader(str(url), 'etag')
        if cached_etag is not None and not self._connection.ignore_etag:
            # http://www.w3.org/1999/04/Editing/
            headers['If-Match'] = cached_etag

        return self._request(
            url, simplejson.dumps(representation,
                                  cls=DatetimeJSONEncoder),
            'PATCH', extra_headers=extra_headers)
