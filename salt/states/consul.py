# -*- coding: utf-8 -*-

"""
Manage Consul contents.
=======================

Consul URL configuration
''''''''''''''''''''''''

You need to setup the Consul URL on which you want to manipulate Consul, for
example by setting in your pillar:

.. code-block:: yaml

    # From a pillar file
    consul:
      url:
         http://consul:8500

See :mod:`salt.modules.consul` for more information on how to configure a
proper URL.
"""

# Import Python Libs
from __future__ import absolute_import
import json

# Define the module's virtual name
__virtualname__ = 'consul'


def key_set(name, value, consul_url=None):
    """
    Set a key to the specified value in Consul's K/V store.

    :param name: The name of the key to set.
    :param value: The value of the key.
    :param consul_url: The Consul server URL. (optional)

    .. code-block:: yaml

        /foo/bar/baz:
          consul.key_set:
            - value: foo

    More complex structures can also be set:

    .. code-block:: yaml

        /foo/bar/baz:
          consul.key_set:
            - value:
                something:
                    - bar
                    - 1
                something else: true
    """

    ret = {
        'name': name,
        'comment': 'Key already set to defined value',
        'result': True,
        'changes': {}
    }

    res = __salt__['consul.get'](consul_url=consul_url, key=name, decode=True)
    old_value = json.loads(res['data'][0]['Value']) if res['res'] else None

    if __opts__['test']:
        if old_value is None: # no key
            ret['comment'] = "Key {0} doesn't exist".format(name)
            ret['result'] = None
        elif old_value != value:
            ret['comment'] = "Value of key {0} will be updated".format(name)
            ret['result'] = None

        return ret

    if old_value != value:
        if old_value is None:
            ret['comment'] = 'New key created'
        else:
            ret['comment'] = 'Key updated'

        res = __salt__['consul.put'](consul_url=consul_url,
                                     key=name, value=value)

        if res['res']:
            ret['changes'] = {
                'new': value,
                'old': old_value,
            }
            ret['comment'] = res['data']
        else:
            ret['result'] = False
            ret['comment'] = res['data']

    return ret


def key_absent(name, consul_url=None):
    """
    Remove a key from Consul's K/V store.

    :param name: The name of the key to remove.
    :param consul_url: The Consul server URL. (optional)

    .. code-block:: yaml

        /foo/bar/baz:
          consul.key_absent

    """

    ret = {
        'name': name,
        'comment': 'Key not present',
        'result': True,
        'changes': {}
    }

    res = __salt__['consul.get'](consul_url=consul_url, key=name, decode=True)

    if __opts__['test']:
        if res['res']:
            ret['comment'] = "Key {0} would have been deleted".format(name)
            ret['result'] = None
        return ret

    if res['res']:
        res = __salt__['consul.delete'](consul_url=consul_url, key=name)
        if res['res']:
            ret['changes'] = {
                name: 'Key deleted',
            }
            ret['comment'] = "Key {0} deleted".format(name)
        else:
            ret['result'] = False
            ret['comment'] = res['data']

    return ret
