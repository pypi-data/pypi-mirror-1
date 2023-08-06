# Copyright 2009 Canonical Ltd.

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

"""Tests for the Launchpad class."""

__metaclass__ = type

import atexit
import os
import os.path
import shutil
import stat
import tempfile
import unittest

from launchpadlib.credentials import AccessToken, Credentials
from launchpadlib.launchpad import Launchpad


class NoNetworkLaunchpad(Launchpad):
    """A Launchpad instance for tests with no network access.

    It's only useful for making sure that certain methods were called.
    It can't be used to interact with the API.
    """

    consumer_name = None
    passed_in_kwargs = None
    credentials = None
    get_token_and_login_called = False

    def __init__(self, credentials, **kw):
        self.credentials = credentials
        self.passed_in_kwargs = kw

    @classmethod
    def get_token_and_login(cls, consumer_name, **kw):
        """Create fake credentials and recored that we were called."""
        credentials = Credentials(
            consumer_name, consumer_secret='consumer_secret:42',
            access_token=AccessToken('access_key:84', 'access_secret:168'))
        launchpad = cls(credentials, **kw)
        launchpad.get_token_and_login_called = True
        launchpad.consumer_name = consumer_name
        launchpad.passed_in_kwargs = kw
        return launchpad


class TestLaunchpadLoginWith(unittest.TestCase):
    """Tests for Launchpad.login_with()."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_dirs_created(self):
        # The path we pass into login_with() is the directory where
        # cache and credentials for all service roots are stored.
        launchpadlib_dir = os.path.join(self.temp_dir, 'launchpadlib')
        launchpad = NoNetworkLaunchpad.login_with(
            'not important', service_root='http://api.example.com/beta',
            launchpadlib_dir=launchpadlib_dir)
        # The 'launchpadlib' dir got created.
        self.assertTrue(os.path.isdir(launchpadlib_dir))
        # A directory for the passed in service root was created.
        service_path = os.path.join(launchpadlib_dir, 'api.example.com')
        self.assertTrue(os.path.isdir(service_path))
        # Inside the service root directory, there is a 'cache' and a
        # 'credentials' directory.
        self.assertTrue(
            os.path.isdir(os.path.join(service_path, 'cache')))
        credentials_path = os.path.join(service_path, 'credentials')
        self.assertTrue(os.path.isdir(credentials_path))

    def test_no_credentials_calls_get_token_and_login(self):
        # If no credentials are found, get_token_and_login() is called.
        service_root = 'http://api.example.com/beta'
        timeout = object()
        proxy_info = object()
        launchpad = NoNetworkLaunchpad.login_with(
            'app name', launchpadlib_dir=self.temp_dir,
            service_root=service_root, timeout=timeout, proxy_info=proxy_info)
        self.assertEqual(launchpad.consumer_name, 'app name')
        expected_arguments = dict(
            service_root=service_root,
            timeout=timeout,
            proxy_info=proxy_info,
            cache=os.path.join(self.temp_dir, 'api.example.com', 'cache'))
        self.assertEqual(launchpad.passed_in_kwargs, expected_arguments)

    def test_new_credentials_are_saved(self):
        # After get_token_and_login() have been called, the created
        # credentials are saved.
        launchpad = NoNetworkLaunchpad.login_with(
            'app name', launchpadlib_dir=self.temp_dir,
            service_root='http://api.example.com/beta')
        credentials_path = os.path.join(
            self.temp_dir, 'api.example.com', 'credentials', 'app name')
        self.assertTrue(os.path.exists(credentials_path))
        # Make sure that the credentials can be loaded, thus were
        # written correctly.
        loaded_credentials = Credentials.load_from_path(credentials_path)
        self.assertEqual(loaded_credentials.consumer.key, 'app name')
        self.assertEqual(
            loaded_credentials.consumer.secret, 'consumer_secret:42')
        self.assertEqual(
            loaded_credentials.access_token.key, 'access_key:84')
        self.assertEqual(
            loaded_credentials.access_token.secret, 'access_secret:168')

    def test_new_credentials_are_secure(self):
        # The newly created credentials file is only readable and
        # writable by the user.
        launchpad = NoNetworkLaunchpad.login_with(
            'app name', launchpadlib_dir=self.temp_dir,
            service_root='http://api.example.com/beta')
        credentials_path = os.path.join(
            self.temp_dir, 'api.example.com', 'credentials', 'app name')
        statinfo = os.stat(credentials_path)
        mode = stat.S_IMODE(statinfo.st_mode)
        self.assertEqual(mode, stat.S_IWRITE | stat.S_IREAD)

    def test_existing_credentials_are_reused(self):
        # If a credential file for the application already exists, that
        # one is used.
        os.makedirs(
            os.path.join(self.temp_dir, 'api.example.com', 'credentials'))
        credentials_file_path = os.path.join(
            self.temp_dir, 'api.example.com', 'credentials', 'app name')
        credentials = Credentials(
            'app name', consumer_secret='consumer_secret:42',
            access_token=AccessToken('access_key:84', 'access_secret:168'))
        credentials.save_to_path(credentials_file_path)

        launchpad = NoNetworkLaunchpad.login_with(
            'app name', launchpadlib_dir=self.temp_dir,
            service_root='http://api.example.com/beta')
        self.assertFalse(launchpad.get_token_and_login_called)
        self.assertEqual(launchpad.credentials.consumer.key, 'app name')
        self.assertEqual(
            launchpad.credentials.consumer.secret, 'consumer_secret:42')
        self.assertEqual(
            launchpad.credentials.access_token.key, 'access_key:84')
        self.assertEqual(
            launchpad.credentials.access_token.secret, 'access_secret:168')

    def test_existing_credentials_arguments_passed_on(self):
        # When re-using existing credentials, the arguments login_with
        # is called with are passed on the the __init__() method.
        os.makedirs(
            os.path.join(self.temp_dir, 'api.example.com', 'credentials'))
        credentials_file_path = os.path.join(
            self.temp_dir, 'api.example.com', 'credentials', 'app name')
        credentials = Credentials(
            'app name', consumer_secret='consumer_secret:42',
            access_token=AccessToken('access_key:84', 'access_secret:168'))
        credentials.save_to_path(credentials_file_path)

        service_root = 'http://api.example.com/beta'
        timeout = object()
        proxy_info = object()
        launchpad = NoNetworkLaunchpad.login_with(
            'app name', launchpadlib_dir=self.temp_dir,
            service_root=service_root, timeout=timeout, proxy_info=proxy_info)
        expected_arguments = dict(
            service_root=service_root,
            timeout=timeout,
            proxy_info=proxy_info,
            cache=os.path.join(self.temp_dir, 'api.example.com', 'cache'))
        self.assertEqual(launchpad.passed_in_kwargs, expected_arguments)

    def test_None_launchpadlib_dir(self):
        # If no launchpadlib_dir is passed in to login_with,
        # $HOME/.launchpadlib is used.
        old_home = os.environ['HOME']
        os.environ['HOME'] = self.temp_dir
        launchpad = NoNetworkLaunchpad.login_with(
            'app name', service_root='http://api.example.com/beta')
        # Reset the environment to the old value.
        os.environ['HOME'] = old_home

        cache_dir = launchpad.passed_in_kwargs['cache']
        launchpadlib_dir = os.path.abspath(
            os.path.join(cache_dir, '..', '..'))
        self.assertEqual(
            launchpadlib_dir, os.path.join(self.temp_dir, '.launchpadlib'))
        self.assertTrue(os.path.exists(
            os.path.join(launchpadlib_dir, 'api.example.com', 'cache')))
        self.assertTrue(os.path.exists(
            os.path.join(launchpadlib_dir, 'api.example.com', 'credentials')))

def additional_tests():
    return unittest.TestLoader().loadTestsFromName(__name__)
