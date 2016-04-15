# -*- coding: utf-8 -*-
"""Integration tests for the Consul state

This requires to define a ``SALTSTACK_TEST_CONSUL_URL`` environment variable
which would be the Consul endpoint on which Consul can be reached and queried.
"""

# Import python libs
from __future__ import absolute_import
import json

# Import Salt Testing libs
from salttesting import skipIf
from salttesting.helpers import (
    destructiveTest,
    ensure_in_syspath
)
ensure_in_syspath('../../')

# Import salt libs
import integration

import os
CONSUL_URL = os.environ.get('SALTSTACK_TEST_CONSUL_URL')


@skipIf(
    CONSUL_URL is None,
    'Define the environment variable SALTSTACK_TEST_CONSUL_URL to a Consul'
    'instance to be used for testing, such as http://localhost:8500.'
)
class ConsulKVStateTest(integration.ModuleCase,
                         integration.SaltReturnAssertsMixIn):
    @destructiveTest
    def setUp(self):
        super(ConsulKVStateTest, self).setUp()
        res = self.run_function('consul.delete', consul_url=CONSUL_URL,
                                key="/", recurse=True)

    @destructiveTest
    def test_kv_set(self):
        """Set a Consul key from a state"""

        key = "test/foo"
        value = "bar"

        ret = self.run_state('consul.key_set', name=key, value=value,
                             consul_url=CONSUL_URL)
        self.assertSaltTrueReturn(ret)
        self.assertSaltStateChangesEqual(ret, {'new': value, 'old': None})

        res = self.run_function('consul.get', consul_url=CONSUL_URL,
                                key=key, decode=True)
        self.assertTrue(res['res'])
        self.assertEqual(value, json.loads(res['data'][0]['Value']))

        # Change the value to something else
        value = "some other bar"

        ret = self.run_state('consul.key_set', name=key, value=value,
                             consul_url=CONSUL_URL)
        self.assertSaltTrueReturn(ret)
        self.assertSaltStateChangesEqual(ret, {'new': value,
                                               'old': 'bar'})

        res = self.run_function('consul.get', consul_url=CONSUL_URL,
                                key=key, decode=True)
        self.assertTrue(res['res'])
        self.assertEqual(value, json.loads(res['data'][0]['Value']))


    @destructiveTest
    def test_kv_set_complex_value(self):
        """Set a Consul key with a complex value from a state"""

        key = "test/bar"
        value = {'something': 0, 'really': ['interesting', False]}

        ret = self.run_state('consul.key_set', name=key, value=value,
                             consul_url=CONSUL_URL)
        self.assertSaltTrueReturn(ret)
        self.assertSaltStateChangesEqual(ret, {'new': value, 'old': None})

        res = self.run_function('consul.get', consul_url=CONSUL_URL,
                                key=key, decode=True)
        self.assertTrue(res['res'])
        self.assertEqual(value, json.loads(res['data'][0]['Value']))

        ret = self.run_state('consul.key_set', name=key, value=value,
                             consul_url=CONSUL_URL)
        self.assertSaltTrueReturn(ret)
        self.assertSaltStateChangesEqual(ret, {})


    @destructiveTest
    def test_kv_absent(self):
        """Ensure a Consul key is absent"""

        key = "test/some/other.key"
        value = "a b c d"

        res = self.run_function('consul.put', consul_url=CONSUL_URL,
                                key=key, value=value)
        self.assertTrue(res['res'])

        ret = self.run_state('consul.key_absent', name=key, value=value,
                             consul_url=CONSUL_URL)
        self.assertSaltTrueReturn(ret)
        self.assertSaltStateChangesEqual(
            ret, {key: 'Key deleted'})

        res = self.run_function('consul.get', consul_url=CONSUL_URL, key=key)
        self.assertFalse(res['res'])




@skipIf(
    CONSUL_URL is None,
    'Define the environment variable SALTSTACK_TEST_CONSUL_URL to a Consul'
    'instance to be used for testing, such as http://localhost:8500.'
)
class ConsulACLStateTest(integration.ModuleCase,
                         integration.SaltReturnAssertsMixIn):
    @destructiveTest
    def setUp(self):
        super(ConsulACLStateTest, self).setUp()
        res = self.run_function('consul.delete', consul_url=CONSUL_URL,
                                key="/", recurse=True)
