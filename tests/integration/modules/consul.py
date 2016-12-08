# -*- coding: utf-8 -*-
"""Integration tests for the Consul module

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
class ConsulKVModuleTest(integration.ModuleCase,
                         integration.SaltReturnAssertsMixIn):

    def assertRequireValueString(self, msg):
        self.assertTrue(isinstance(msg, str))

        error_headline = msg.split('\n')[0]
        self.assertTrue(error_headline.startswith(
            "ERROR executing 'consul.put': The value has to be a string."),
            error_headline)


    @destructiveTest
    def setUp(self):
        super(ConsulKVModuleTest, self).setUp()
        res = self.run_function('consul.delete', consul_url=CONSUL_URL,
                                key="/", recurse=True)

    @destructiveTest
    def test_kv_list_empty(self):
        """Listing an empty Consul K/V store returns nothing"""

        res = self.run_function('consul.list', consul_url=CONSUL_URL)
        self.assertTrue(res['res'])
        self.assertEqual([], res['data'])

    @destructiveTest
    def test_kv_put_get_simple_value(self):
        """Set and retrieve a simple key/value"""

        key = "test/foo"
        value = "bar"

        res = self.run_function('consul.put', consul_url=CONSUL_URL,
                                key=key, value=value)
        self.assertTrue(res['res'])

        res = self.run_function('consul.get', consul_url=CONSUL_URL,
                                key=key, decode=True)
        self.assertTrue(res['res'])
        self.assertEqual(value, res['data'][0]['Value'])

    @destructiveTest
    def test_kv_fail_put_non_string_value(self):
        """Can't set a non-string value"""

        key = "test/foo"
        value = 42

        res = self.run_function('consul.put', consul_url=CONSUL_URL,
                                key=key, value=value)
        self.assertRequireValueString(res)

    @destructiveTest
    def test_kv_put_get_complex_value(self):
        """Set and retrieve a value composed of other values"""

        key = "test/foo"
        value = {"something": "like", "a list of": [0, 1, 2]}

        res = self.run_function('consul.put', consul_url=CONSUL_URL,
                                key=key, value=value)
        self.assertRequireValueString(res)

        # If we convert the value into JSON, we can load/restore it.
        res = self.run_function('consul.put', consul_url=CONSUL_URL,
                                key=key, value=json.dumps(value))
        res = self.run_function('consul.get', consul_url=CONSUL_URL,
                                key=key, decode=True)
        self.assertTrue(res['res'])
        self.assertEqual(value, json.loads(res['data'][0]['Value']))
