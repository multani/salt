# -*- coding: utf-8 -*-
"""Unit tests for the Consul module"""

# Import Python Libs
from __future__ import absolute_import

import base64
import json

# Import Salt Testing Libs
from salttesting import TestCase, skipIf
from salttesting.mock import (
    Mock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)
from salttesting.helpers import ensure_in_syspath

ensure_in_syspath('../../')

# Import Salt Libs
from salt.modules import consul
import salt.utils.http


consul.__opts__ = {}


class Result(dict):
    def json(self):
        return dict(self)


@skipIf(NO_MOCK, NO_MOCK_REASON)
class ConsulModuleTestCase(TestCase):
    def test_session_list_empty(self):
        """List the (empty) session from Consul"""

        mock_query = Mock(side_effect=[
            Result({'status': 200, 'dict': []}),
            Result({'status': 200, 'dict': []}),
        ])

        with patch.object(salt.utils.http, 'query', mock_query):
            key = "test/foo"
            value = "bar"

            res = consul.session_list(consul_url='http://consul.url:8500',
                                      return_list=True)

        mock_query.assert_called_with(
            'http://consul.url:8500/v1/session/list',
            method='GET',
            params={},
            data='{}',
            decode=True,
            status=True,
            header_dict={},
            opts={},
        )

        self.assertEqual([], res)


    def test_kv_list_empty(self):
        """List an empty K/V store"""

        mock_query = Mock(side_effect=[
            Result({'status': 200, 'dict': []}),
        ])

        with patch.object(salt.utils.http, 'query', mock_query):
            res = consul.list_(consul_url='http://consul.url:8500')

        mock_query.assert_called_with(
            'http://consul.url:8500/v1/kv/',
            method='GET',
            params={'keys': 'True', 'recurse': 'True'},
            data='{}',
            decode=True,
            status=True,
            header_dict={},
            opts={},
        )

        self.assertTrue(res['res'])
        self.assertEqual([], res['data'])


    def test_kv_put_get_simple_value(self):
        """Set and retrieve a simple key/value

        Be sure the value is first encoded into JSON during PUT and correctly
        decoded from JSON during the GET call.
        """

        key = "test/foo"
        value = "bar"

        mock_query = Mock()

        with patch.object(salt.utils.http, 'query', mock_query):
            # Set up mock for the PUT call
            mock_query.side_effect = [
                Result({'status': 200, 'dict': []}), # session_list()
                Result({'status': 200, 'dict': []}), # put() > get()
                Result({'status': 200, 'dict': []}), # put() (for real)
            ]

            res = consul.put(consul_url='http://consul.url:8500',
                             key=key, value=value)

            # consul.put() does several call before the actual PUT call, such as
            # checking the sessions and trying to retrieve the key being set.
            self.assertEqual(3, mock_query.call_count)
            # ... but we are only interested into the last Consul call for this
            # test.
            mock_query.assert_called_with(
                'http://consul.url:8500/v1/kv/test/foo',
                method='PUT',
                params={},
                # The data is actually converted to JSON before being sent to
                # Consul.
                data='%s' % json.dumps(value),
                decode=True,
                status=True,
                header_dict={},
                opts={},
            )
            self.assertTrue(res['res'])


            # Now for the GET call
            mock_query.side_effect = [
                # get()
                Result({
                    'status': 200,
                    'dict': [{
                        # The value coming from Consul has been first converted to
                        # JSON by consul.put() then encoded into base64 by Consul.
                        'Value': base64.b64encode(json.dumps(value)),

                        #'LockIndex': 0,
                        #'ModifyIndex': 1,
                        #'Flags': 0,
                        #'Key': key,
                        #'CreateIndex': 1
                    }]
                    #'body': '', # JSON body
                })
            ]

            res = consul.get(consul_url='http://consul.url:8500',
                             key=key, decode=True)

            mock_query.assert_called_with(
                'http://consul.url:8500/v1/kv/test/foo',
                method='GET',
                params={},
                data='{}',
                decode=True,
                status=True,
                header_dict={},
                opts={},
            )
            self.assertTrue(res['res'])
            self.assertEqual(1, len(res['data']))

            # Most importantly, check that the value retrieved is actually the
            # value we stored.
            self.assertEqual(value, res['data'][0]['Value'])
