import os
from datetime import datetime
import time
from base64 import b64encode, b64decode
from urllib import urlencode
from cgi import parse_qs

from django.conf import settings

from account.models import AuthKey

class InvalidKey(Exception):
    pass

def generate_key(**kwargs):
    """
    Create AuthKey object and return its ID.
    """

    key = AuthKey()
    key.uid = kwargs['uid']
    if 'expired' in kwargs:
        key.expired = kwargs.pop('expired')
    key.import_data(**kwargs)
    key.save()
    return key.id


def wrap_url(url, **kwargs):
    """
    Create new authorization key and append it to the url.
    """

    if not 'uid' in kwargs:
        raise Exception('wrap_url requires uid name argument')

    hash = generate_key(**kwargs)
    clue = '?' in url and '&' or '?'
    url = '%s%sauthkey=%s' % (url, clue, hash)
    return url


def decode_key(hash):
    try:
        key = AuthKey.objects.get(pk=hash)
    except AuthKey.DoesNotExist:
        raise InvalidKey('Key does not exist')
    if datetime.now() > key.expired:
        raise InvalidKey('Key is expired')
    return key.export_data()
