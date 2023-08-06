#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Subversion repos hooks plugin.

Basic classes used for Subversion hooks management.
"""

import re
import sys
import os
import StringIO
import logging
log = logging.getLogger(__name__)

from pylons import config
config_path = config["here"] + '/config'
if config_path not in sys.path:
    sys.path.insert(0, config_path)
from localconfig import LocalConfig as cfg

sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pysvnmanager.hooks import plugins
from pysvnmanager.model import repos

# i18n works only as pysvnmanager (a pylons app) model.
if config.get('package') and not config.has_key('unittest'):
    from pylons.i18n import _
else:
    def _(message): return message

#reload(sys) # in Python2.5, method sys.setdefaultencoding 
            #will be delete after initialize. we need reload it.
#sys.setdefaultencoding('utf-8')

class Hooks:
    
    def __init__(self, repos_path):
        self.__repos_path = os.path.abspath(repos_path)
        self.__repos_root = os.path.dirname(self.__repos_path)
        self.__repos_name = os.path.basename(self.__repos_path)
        self.repos = repos.Repos(self.__repos_root)
        assert self.repos.is_svn_repos(self.__repos_name)
        
        self.plugins = {}
        for m in plugins.modules:
            self.plugins[m] = plugins.getHandler(m)(self.__repos_path)
            self.plugins[m].id = m
        self.pluginnames = [ m.id for m in sorted(self.plugins.values()) ]
    
    def __get_applied_plugins(self):
        return [ m for m in self.pluginnames if self.plugins[m].enabled()]
    
    applied_plugins = property(__get_applied_plugins)

    def __get_unapplied_plugins(self):
        return [ m for m in self.pluginnames if not self.plugins[m].enabled()]
    
    unapplied_plugins = property(__get_unapplied_plugins)
    
    def __get_repos_root(self):
        return self.__repos_root
    
    repos_root = property(__get_repos_root)
    
    def __get_repos_name(self):
        return self.__repos_name
    
    repos_name = property(__get_repos_name)
        
    def __get_repos_path(self):
        return self.__repos_path
    
    repos_path = property(__get_repos_path)
        
 

if __name__ == '__main__':
    import doctest
    doctest.testmod()
