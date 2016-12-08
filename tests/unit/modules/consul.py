from salttesting import TestCase
from salttesting.mock import (
    MagicMock,
    patch,
    call,
    ANY,
)

from salt.modules import consul
consul.__salt__ = {}
consul.__opts__ = {}

import salt.utils.http


class ConsulModuleTestCase(TestCase):
    def test_kv_list_empty(self):
        query_result = {'body': '[]',
                        'dict': [],
                        'status': 200}

        mock_http = MagicMock(return_value=query_result)
        mock_cfg = MagicMock(return_value="http://example.com:8500")

        with patch.dict(consul.__salt__, {'config.get': mock_cfg}), \
                patch.dict(consul.__opts__, {}), \
                patch.object(salt.utils.http, 'query', mock_http):

            res = consul.list_()

        mock_http.assert_called_once_with(
            'http://example.com:8500/v1/kv/',
            method='GET',
            params={'keys': 'True', 'recurse': 'True'},
            data=None,
            decode=True,
            header_dict=ANY, opts=ANY, status=ANY,
        )

        self.assertTrue(res['res'])
        self.assertEqual([], res['data'])



    def test_kw_put_simple_value(self):


#{'data': None,
 #'decode': True,
 #'header_dict': {'User-agent': 'Salt/2015.8.11-41-g2431878 http.query()'},
 #'method': 'GET',
 #'params': {},
 #'result': {'body': '[]', 'dict': [], 'status': 200},
 #'status': True,
 #'url': 'http://localhost:55000/v1/session/list'}
#{'data': None,
 #'decode': True,
 #'header_dict': {'User-agent': 'Salt/2015.8.11-41-g2431878 http.query()'},
 #'method': 'GET',
 #'params': {},
 #'result': {'error': 'HTTP 404: Not Found', 'status': 404},
 #'status': True,
 #'url': 'http://localhost:55000/v1/kv/test/foo'}
#{'data': 'bar',
 #'decode': True,
 #'header_dict': {'User-agent': 'Salt/2015.8.11-41-g2431878 http.query()'},
 #'method': 'PUT',
 #'params': {},
 #'result': {'body': 'true', 'dict': True, 'status': 200},
 #'status': True,
 #'url': 'http://localhost:55000/v1/kv/test/foo'}
#{'data': None,
 #'decode': True,
 #'header_dict': {'User-agent': 'Salt/2015.8.11-41-g2431878 http.query()'},
 #'method': 'GET',
 #'params': {},
 #'result': {'body': '[{"LockIndex":0,"Key":"test/foo","Flags":0,"Value":"YmFy","CreateIndex":183,"ModifyIndex":183}]',
            #'dict': [{u'CreateIndex': 183,
                      #u'Flags': 0,
                      #u'Key': u'test/foo',
                      #u'LockIndex': 0,
                      #u'ModifyIndex': 183,
                      #u'Value': u'YmFy'}],
            #'status': 200},
 #'status': True,
 #'url': 'http://localhost:55000/v1/kv/test/foo'}

        key = "test/foo"
        value = "bar"

        query_result = (
            {'body': '[]', 'dict': [], 'status': 200},
            {'error': 'HTTP 404: Not Found', 'status': 404},
            {'body': 'true', 'dict': True, 'status': 200},
            #{'body': '[{"LockIndex":0,"Key":"test/foo","Flags":0,"Value":"YmFy","CreateIndex":183,"ModifyIndex":183}]',
            #'dict': [{u'CreateIndex': 183,
                      #u'Flags': 0,
                      #u'Key': u'test/foo',
                      #u'LockIndex': 0,
                      #u'ModifyIndex': 183,
                      #u'Value': u'YmFy'}],
            #'status': 200},
        )

        mock_http = MagicMock(side_effect=query_result)
        mock_cfg = MagicMock(return_value="http://example.com:8500")

        with patch.dict(consul.__salt__, {'config.get': mock_cfg}), \
                patch.dict(consul.__opts__, {}), \
                patch.object(salt.utils.http, 'query', mock_http):

            res = consul.put(key=key, value=value)

        self.assertEqual(3, mock_http.call_count)

        self.assertEqual(
            call(
                'http://example.com:8500/v1/session/list',
                method='GET',
                params=ANY,
                data=None,
                decode=True,
                header_dict=ANY, opts=ANY, status=ANY,
            ),
            mock_http.call_args_list[0]
        )

        self.assertEqual(
            call(
                'http://example.com:8500/v1/kv/test/foo',
                method='GET',
                params=ANY,
                data=None,
                decode=True,
                header_dict=ANY, opts=ANY, status=ANY,
            ),
            mock_http.call_args_list[1]
        )

        self.assertEqual(
            call(
                'http://example.com:8500/v1/kv/test/foo',
                method='PUT',
                params=ANY,
                data='bar',
                decode=True,
                header_dict=ANY, opts=ANY, status=ANY,
            ),
            mock_http.call_args_list[2]
        )

        #mock_http.assert_called_once_with(
            #'http://example.com:8500/v1/kv/',
            #method='GET',
            #params={'keys': 'True', 'recurse': 'True'},
            #data=None,
            #decode=True,
            #header_dict=ANY, opts=ANY, status=ANY,
        #)

        self.assertTrue(res['res'])
        self.assertEqual("Added key test/foo with value bar.", res['data'])
