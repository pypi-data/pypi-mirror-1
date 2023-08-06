# Copyright 2008-2009 Canonical Ltd.

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

"""Root Launchpad API class."""

__metaclass__ = type
__all__ = [
    'Launchpad',
    ]

import os
import shutil
import simplejson
import stat
import sys
import tempfile
import urlparse
import webbrowser

from wadllib.application import Resource as WadlResource
from lazr.uri import URI

from launchpadlib._browser import Browser
from launchpadlib.resource import Resource
from launchpadlib.credentials import AccessToken, Credentials

STAGING_SERVICE_ROOT = 'https://api.staging.launchpad.net/beta/'
EDGE_SERVICE_ROOT = 'https://api.edge.launchpad.net/beta/'

class Launchpad(Resource):
    """Root Launchpad API class.

    :ivar credentials: The credentials instance used to access Launchpad.
    :type credentials: `Credentials`
    """

    def __init__(self, credentials, service_root=STAGING_SERVICE_ROOT,
                 cache=None, timeout=None, proxy_info=None):
        """Root access to the Launchpad API.

        :param credentials: The credentials used to access Launchpad.
        :type credentials: `Credentials`
        :param service_root: The URL to the root of the web service.
        :type service_root: string
        """
        self._root_uri = URI(service_root)
        self.credentials = credentials
        # Get the WADL definition.
        self._browser = Browser(self.credentials, cache, timeout, proxy_info)
        self._wadl = self._browser.get_wadl_application(self._root_uri)

        # Get the root resource.
        root_resource = self._wadl.get_resource_by_path('')
        bound_root = root_resource.bind(
            self._browser.get(root_resource), 'application/json')
        super(Launchpad, self).__init__(None, bound_root)

    def load(self, url):
        """Load a resource given its URL."""
        document = self._browser.get(url)
        try:
            representation = simplejson.loads(document)
        except ValueError:
            raise ValueError("%s doesn't serve a JSON document." % url)
        type_link = representation.get("resource_type_link")
        if type_link is None:
            raise ValueError("Couldn't determine the resource type of %s."
                             % url)
        resource_type = self._root._wadl.get_resource_type(type_link)
        wadl_resource = WadlResource(self._root._wadl, url, resource_type.tag)
        return self._create_bound_resource(
            self._root, wadl_resource, representation, 'application/json',
            representation_needs_processing=False)

    @classmethod
    def login(cls, consumer_name, token_string, access_secret,
              service_root=STAGING_SERVICE_ROOT,
              cache=None, timeout=None, proxy_info=None):
        """Convenience for setting up access credentials.

        When all three pieces of credential information (the consumer
        name, the access token and the access secret) are available, this
        method can be used to quickly log into the service root.

        :param consumer_name: the consumer name, as appropriate for the
            `Consumer` constructor
        :type consumer_name: string
        :param token_string: the access token, as appropriate for the
            `AccessToken` constructor
        :type token_string: string
        :param access_secret: the access token's secret, as appropriate for
            the `AccessToken` constructor
        :type access_secret: string
        :param service_root: The URL to the root of the web service.
        :type service_root: string
        :return: The web service root
        :rtype: `Launchpad`
        """
        access_token = AccessToken(token_string, access_secret)
        credentials = Credentials(
            consumer_name=consumer_name, access_token=access_token)
        return cls(credentials, service_root, cache, timeout, proxy_info)

    @classmethod
    def get_token_and_login(cls, consumer_name,
                            service_root=STAGING_SERVICE_ROOT,
                            cache=None, timeout=None, proxy_info=None):
        """Get credentials from Launchpad and log into the service root.

        This is a convenience method which will open up the user's preferred
        web browser and thus should not be used by most applications.
        Applications should, instead, use Credentials.get_request_token() to
        obtain the authorization URL and
        Credentials.exchange_request_token_for_access_token() to obtain the
        actual OAuth access token.

        This method will negotiate an OAuth access token with the service
        provider, but to complete it we will need the user to log into
        Launchpad and authorize us, so we'll open the authorization page in
        a web browser and ask the user to come back here and tell us when they
        finished the authorization process.

        :param consumer_name: The consumer name, as appropriate for the
            `Consumer` constructor
        :type consumer_name: string
        :param service_root: The URL to the root of the web service.
        :type service_root: string
        :return: The web service root
        :rtype: `Launchpad`
        """
        credentials = Credentials(consumer_name)
        web_root_uri = URI(service_root)
        web_root_uri.path = ""
        web_root_uri.host = web_root_uri.host.replace("api.", "", 1)
        web_root = str(web_root_uri.ensureSlash())
        authorization_url = credentials.get_request_token(web_root=web_root)
        webbrowser.open(authorization_url)
        print ("The authorization page (%s) should be opening in your "
               "browser. After you have authorized this program to "
               "access Launchpad on your behalf you should come back "
               "here and press <Enter> to finish the authentication "
               "process." % authorization_url)
        sys.stdin.readline()
        credentials.exchange_request_token_for_access_token(web_root)
        return cls(credentials, service_root, cache, timeout, proxy_info)

    @classmethod
    def login_with(cls, consumer_name,
                   service_root=STAGING_SERVICE_ROOT,
                   launchpadlib_dir=None, timeout=None, proxy_info=None):
        """Log in to Launchpad with possibly cached credentials.

        This is a convenience method for either setting up new login
        credentials, or re-using existing ones. When a login token is
        generated using this method, the resulting credentials will be
        saved in the `launchpadlib_dir` directory. If the same
        `launchpadlib_dir` is passed in a second time, the credentials
        in `launchpadlib_dir` for the consumer will be used
        automatically.

        Each consumer has their own credentials per service root in
        `launchpadlib_dir`. `launchpadlib_dir` is also used for caching
        fetched objects. The cache is per service root, and shared by
        all consumers.

        See `Launchpad.get_token_and_login()` for more information about
        how new tokens are generated.

        :param consumer_name: The consumer name, as appropriate for the
            `Consumer` constructor
        :type consumer_name: string
        :param service_root: The URL to the root of the web service.
        :type service_root: string
        :param launchpadlib_dir: The directory where the cache and
            credentials are stored.
        :type launchpadlib_dir: string
        :return: The web service root
        :rtype: `Launchpad`

        """
        if launchpadlib_dir is None:
            home_dir = os.environ['HOME']
            launchpadlib_dir = os.path.join(home_dir, '.launchpadlib')
        launchpadlib_dir = os.path.expanduser(launchpadlib_dir)
        # Each service root has its own cache and credential dirs.
        scheme, host_name, path, query, fragment = urlparse.urlsplit(
            service_root)
        service_root_dir = os.path.join(launchpadlib_dir, host_name)
        cache_path = os.path.join(service_root_dir, 'cache')
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        credentials_path = os.path.join(service_root_dir, 'credentials')
        if not os.path.exists(credentials_path):
            os.makedirs(credentials_path)
        consumer_credentials_path = os.path.join(
            credentials_path, consumer_name)
        if os.path.exists(consumer_credentials_path):
            credentials = Credentials.load_from_path(
                consumer_credentials_path)
            launchpad = cls(
                credentials, service_root=service_root, cache=cache_path,
                timeout=timeout, proxy_info=proxy_info)
        else:
            launchpad = cls.get_token_and_login(
                consumer_name, service_root=service_root, cache=cache_path,
                timeout=timeout, proxy_info=proxy_info)
            launchpad.credentials.save_to_path(
                os.path.join(credentials_path, consumer_name))
            os.chmod(
                os.path.join(credentials_path, consumer_name),
                stat.S_IREAD | stat.S_IWRITE)
        return launchpad
