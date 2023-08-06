# -*- coding: utf-8 -*-
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from wsgioauth.mock import Storage
from wsgioauth.provider import (
    Application,
    Consumer as BaseConsumer,
    Middleware,
    Token as BaseToken,
    )
from repoze.zodbconn.finder import PersistentApplicationFinder

class Consumer(BaseConsumer, Persistent):
    """This class makes the wsgioauth.provider.Consumer class ZODB
    persistent."""


class Token(BaseToken, Persistent):
    """This class makes the wsgioauth.provider.Token class ZODB
    persistent."""


class ZODBStorage(Storage):

    def __init__(self, root, config):
        super(ZODBStorage, self).__init__(config)
        self._consumers = root['consumers']
        self._request_tokens = root['request_tokens']
        self._access_tokens = root['access_tokens']


def app_maker(zodb_root):
    """Creates the root structure for the zodb and returns the root object.
    """
    root_id = 'oauth_root'
    if not root_id in zodb_root:
        data = {
            'consumers': OOBTree(),
            'request_tokens': OOBTree(),
            'access_tokens': OOBTree(),
            }
        oauth_root = OOBTree(data)
        zodb_root[root_id] = oauth_root
        import transaction
        transaction.commit()
    return zodb_root[root_id]

def admin_app(*global_conf, **local_conf):
    """This function returns a wsgioauth.provider.Application object.
    It is usually called by the PasteDeploy framework during ``paster serve``.
    """
    zodb_uri = local_conf.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError("No 'zodb_uri' in application configuration.")

    # setup the calls
    from wsgioauth.mock import ROUTES
    from wsgioauth.utils import CALLS
    CALLS.update(ROUTES)

    # setup the Classes to use
    from wsgioauth.provider import OAUTH_CLASSES
    OAUTH_CLASSES['consumer'] = Consumer
    OAUTH_CLASSES['request_token'] = Token

    get_root = PersistentApplicationFinder(zodb_uri, app_maker, connection_key='oauth_db_connection')
    def storage_factory(environ, config):
        """returns a Storage object"""
        return ZODBStorage(get_root(environ), config)
    return Application(storage_factory, **local_conf)

def middleware(app, *global_conf, **local_conf):
    """The function returns a wsgioauth.provider.Filter object."""
    zodb_uri = local_conf.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError("No 'zodb_uri' in application configuration.")

    # setup the Classes to use
    from wsgioauth.provider import OAUTH_CLASSES
    OAUTH_CLASSES['consumer'] = Consumer
    OAUTH_CLASSES['request_token'] = Token

    get_root = PersistentApplicationFinder(zodb_uri, app_maker, connection_key='oauth_db_connection')
    def storage_factory(environ, config):
        """returns a Storage object"""
        return ZODBStorage(get_root(environ), config)
    return Middleware(app, storage_factory, **local_conf)
