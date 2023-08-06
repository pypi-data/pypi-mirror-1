#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pysvnmanager.tests import *
from pysvnmanager import model
from pysvnmanager.model import repos
from pysvnmanager.model import hooks
from pysvnmanager.hooks import plugins

from pysvnmanager.lib.base import *

import StringIO
from pprint import pprint

class TestRepos(TestController):
    
    def __init__(self, *args):
        # self.repos_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/svnroot'
        self.repos_root = cfg.repos_root
        self.repos = repos.Repos(self.repos_root)
        super(TestRepos, self).__init__(*args)

    def setUp(self):
        #print '+'*40, 'setup'
        pass

    def tearDown(self):
        #print '+'*40, 'teardown'
        pass
    
    def testReposCreate(self):
        self.assertRaises(Exception, self.repos.create, 'repos3')
        self.repos.delete('repos3')
        self.repos.create('repos3')
        self.assert_(sorted(self.repos.repos_list) == [u'project1', u'project2', u'repos3'], self.repos.repos_list)

    def testReposDelete(self):
        self.assertRaises(Exception, self.repos.delete, 'project1')
    
    def testReposRoot(self):
        repos.Repos('/tmp')
        self.assertRaises(Exception, repos.Repos, '/tmp/svnroot.noexists')

    def testReposlist(self):
        self.assert_(sorted(self.repos.repos_list) == ['project1', 'project2', 'repos3'], u','.join(self.repos.repos_list).encode('utf-8'))

    def testSvnVersion(self):
        svnversion = self.repos.svnversion()
        self.assert_(svnversion[0]!='', svnversion[0])
        self.assert_(svnversion[1]!='', svnversion[1])

class TestReposPlugin(TestController):
    
    def __init__(self, *args):
        # self.repos_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/svnroot'
        self.repos_root = cfg.repos_root
        super(TestReposPlugin, self).__init__(*args)

    def setUp(self):
        #print '+'*40, 'setup'
        pass

    def tearDown(self):
        #print '+'*40, 'teardown'
        pass

    def testPluginList(self):
        self.assert_('CaseInsensitive' in plugins.modules, plugins.modules)
        self.assert_('EolStyleCheck' in plugins.modules, plugins.modules)
      
    def testPluginImport(self):
        self.assertRaises(Exception,  plugins.getHandler("CaseInsensitive"), "")
        module_ci = plugins.getHandler("CaseInsensitive")(self.repos_root + '/project1')
        self.assert_(module_ci.name=="Detect case-insensitive filename clashes", module_ci.name)
        self.assert_(module_ci.description!="", module_ci.description)
      
    def testPluginSetting(self):
        m = plugins.getHandler("CaseInsensitive")(self.repos_root + '/project1')
        self.assert_(m.enabled()==False)
        m.install()
        self.assert_(m.enabled()==True)
        m.uninstall()
        self.assert_(m.enabled()==False)
      
    def testHooks(self):
        # self.repos_root is not a repository.
        self.assertRaises(AssertionError, hooks.Hooks, self.repos_root)
        
        myhooks = hooks.Hooks(self.repos_root + '/project1')
        self.assert_('CaseInsensitive' in myhooks.pluginnames, myhooks.pluginnames)
        self.assert_('EolStyleCheck' in myhooks.pluginnames, myhooks.pluginnames)
        
        self.assert_('CaseInsensitive' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        self.assert_('EolStyleCheck' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        
        m = myhooks.plugins['CaseInsensitive']
        self.assert_(m.name=="Detect case-insensitive filename clashes", m.name)
        self.assert_(m.description!="", m.description)
    
    def testHooksSetting(self):
        myhooks = hooks.Hooks(self.repos_root + '/project1')

        m = myhooks.plugins['CaseInsensitive']
        self.assert_(m.enabled()==False)
        self.assert_('CaseInsensitive' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('EolStyleCheck' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('CaseInsensitive' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        self.assert_('EolStyleCheck' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)

        m.install()
        self.assert_(m.enabled()==True)
        self.assert_('CaseInsensitive' in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('EolStyleCheck' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('CaseInsensitive' not in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        self.assert_('EolStyleCheck' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)

        m.uninstall()
        self.assert_(m.enabled()==False)
        self.assert_('CaseInsensitive' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('EolStyleCheck' not in myhooks.applied_plugins, myhooks.applied_plugins)
        self.assert_('CaseInsensitive' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)
        self.assert_('EolStyleCheck' in myhooks.unapplied_plugins, myhooks.unapplied_plugins)


if __name__ == '__main__': 
    import unittest
    unittest.main()
