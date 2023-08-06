# -*- coding: utf8 -*-
import unittest
import sys
from copy import copy
from os.path import realpath, split, dirname, join
import os
from distutils.tests import support

current_dir = realpath(dirname(__file__))
pkg_dir = split(split(current_dir)[0])[0]
sys.path.insert(0, pkg_dir)

from extensions.entry_point import Requirement, EntryPoint
from extensions.reader import get_plugins, _ep_map
from extensions.registry import register

class TestUseEp(support.TempdirManager,
                support.LoggingSilencer,
                unittest.TestCase):

    def test_basic(self):
        r = Requirement('test', [], [])
        e = EntryPoint('name', 'modulename')
        eps = get_plugins(consume_entry_points=True)
        self.assert_(len(list(eps)) > 0)

    @staticmethod
    def _ok():
        return 1

    def test_register(self):
        register('mygroup', 'myplugin',
                 'extensions.tests.test_use_ep:TestUseEp._ok')

        plugins = list(get_plugins(group='mygroup'))
        self.assertEquals(len(plugins), 1)
        plugin = plugins[0]
        self.assertEquals(plugin.name, 'myplugin')
        self.assertEquals(plugin.group, 'mygroup')
        func = plugin.load()
        self.assertEquals(func(), 1)

        register('mygroup', 'myotherplugin',
                 'plugins.tests.test_use_ep:TestUseEp.test_register')

        plugins = list(get_plugins(group='mygroup'))
        self.assertEquals(len(plugins), 2)

        plugins = list(get_plugins(group='mygroup', name='myotherplugin'))
        self.assertEquals(len(plugins), 1)
        plug = plugins[0]
        self.assertEquals(plug.name, 'myotherplugin')

    def test_foobar_sdist(self):
        test_pkg_dir = join(current_dir, 'pkg')
        old = copy(sys.argv)
        old_dir = os.getcwd()
        old_path = copy(sys.path)
        os.chdir(test_pkg_dir)
        sys.path.insert(0, test_pkg_dir)
        install_dir = self.mkdtemp()
        sys.argv = ['setup.py', 'install', '--prefix', install_dir]
        try:
            __import__('setup')
        finally:
            sys.argv = copy(old)
            os.chdir(old_dir)
            sys.path = copy(old_path)

        # let's see what we have
        site_packages = join(install_dir, 'lib', 'python2.6', 'site-packages')
        egg_info = join(site_packages, 'foo-0.1-py2.6.egg-info')
        egg_info = os.listdir(egg_info)
        egg_info.sort()
        self.assertEquals(egg_info, ['PKG-INFO', 'PLUGINS'])

        # can we find the entry point ?
        ep = _ep_map(join(site_packages, 'foo-0.1-py2.6.egg-info'))
        self.assertNotEquals(ep, None)

        # let's filter other entry points and make sure we just jet on
        plugins = list(get_plugins(consume_entry_points=False))
        self.assertEquals(len(plugins), 1)

def test_suite():
    return unittest.makeSuite(TestUseEp)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

