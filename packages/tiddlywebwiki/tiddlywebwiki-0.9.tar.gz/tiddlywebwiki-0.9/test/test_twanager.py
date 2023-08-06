"""
Test twanager commands.
"""

import sys
sys.path.insert(0, '.')

import os

from shutil import rmtree

from tiddlyweb.config import config
from tiddlyweb.store import Store
from tiddlyweb.model.bag import Bag

import tiddlywebwiki.instancer as instancer
import tiddlywebwiki.twanager as twanager


instance_dir = 'test_instance'


def setup_module(module):
    instancer.init(config)
    twanager.init(config)
    try:
        rmtree(instance_dir)
    except:
        pass


class TestInstance(object):

    def setup_method(self, module):
        env = { 'tiddlyweb.config': config }
        self.store = Store(config['server_store'][0], environ=env) # XXX: use module.store?

    def teardown_method(self, module):
        os.chdir('..')
        rmtree(instance_dir)

    def test_create_tiddlywebwiki_instance(self):
        twanager.instance([instance_dir])

        contents = _get_file_contents('../%s/tiddlywebconfig.py' % instance_dir)

        assert "'system_plugins': ['tiddlywebwiki', 'status']" in contents
        assert "'twanager_plugins': ['tiddlywebwiki']" in contents

    def test_create_bag_policies(self):
        twanager.instance([instance_dir])

        policy_location = '../%s/store/bags/%%s/policy' % instance_dir

        bag = Bag('system')
        system_policy = self.store.get(bag).policy
        bag = Bag('common')
        common_policy = self.store.get(bag).policy

        assert system_policy.read == []
        assert system_policy.write == ['R:ADMIN']
        assert system_policy.create == ['R:ADMIN']
        assert system_policy.manage == ['R:ADMIN']
        assert system_policy.accept == ['R:ADMIN']
        assert system_policy.delete == ['R:ADMIN']

        assert common_policy.read == []
        assert common_policy.write == []
        assert common_policy.create == []
        assert common_policy.manage == []
        assert common_policy.accept == []
        assert common_policy.delete == ['R:ADMIN']


def _get_file_contents(filepath):
    f = open(filepath)
    contents = f.read()
    f.close()
    return contents
