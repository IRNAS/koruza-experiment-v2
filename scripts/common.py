from __future__ import print_function

import base64
import collections
import hashlib
import hmac
import json
import os

import requests
import yaml


# Determine experiment directory.
EXPERIMENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Reserved router identifiers.
RESERVED_ROUTER_IDS = [0, 254]


def dict_merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def get_config(location=None):
    """Load experiment configuration."""
    if hasattr(get_config, '_cache'):
        config = get_config._cache
    else:
        config = yaml.load(open(os.path.join(EXPERIMENT_DIR, 'config.yml'), 'r'))
        secrets = yaml.load(open(os.path.join(EXPERIMENT_DIR, 'secrets.yml'), 'r'))

        # Merge secrets into general config.
        dict_merge(config, secrets)

        validate_config(config)
        get_config._cache = config

    if location is not None:
        return reduce(lambda a, b: a[b], location.split('.'), config)

    return config


def validate_config(config):
    """Validate configuration."""
    def validate_link(links, link_id):
        """Validate if the given link identifier is valid."""
        if link_id is None:
            return

        if link_id not in links:
            raise ValueError("Link identifier '{}' not valid.".format(link_id))

    for router in config['routers']:
        if router['id'] in RESERVED_ROUTER_IDS:
            raise ValueError("Router identifier '{id}' is reserved.".format(**router))

        validate_link(config['links'], router['link_a'])
        validate_link(config['links'], router['link_b'])


def nodewatcher_uri_for_node(uuid):
    """Generate nodewatcher push URI for a specific node.

    :param uuid: node uuid
    """
    return 'http://{host}/push/http/{uuid}'.format(
        host=get_config('nodewatcher.host'),
        uuid=uuid,
    )


def nodewatcher_push(uuid, body, ignore_errors=True):
    """Push data to nodewatcher server.

    :param uuid: node uuid
    :param body: correctly formatted request body
    :param ignore_errors: whether errors should be silently ignored
    """
    body = json.dumps(body)
    signature = base64.b64encode(hmac.new(get_config('nodewatcher.key'), body, hashlib.sha256).digest())

    try:
        requests.post(
            nodewatcher_uri_for_node(uuid),
            data=body,
            headers={
                'X-Nodewatcher-Signature-Algorithm': 'hmac-sha256',
                'X-Nodewatcher-Signature': signature,
            }
        )
    except:
        if not ignore_errors:
            raise
