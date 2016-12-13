#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
    Description : manage config file $HOME/.broc.rc
    Authors     : zhousongsong(doublesongsong@gmail.com)
    Date        : 2015-09-18 10:28:23
"""

import os
import sys
import ConfigParser

broc_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
sys.path.insert(0, broc_dir)

from dependency import BrocModule_pb2

class BrocConfigError(Exception):
    """
    """
    def __init__(self, msg):
        """
        Args:
            msg : the error msg
        """
        self._msg = msg

    def __str__(self):
        """
        """
        return self._msg

class BrocConfig(object):
    """
    this class manages the .broc.rc in $HOME
    """
    class __impl(object):
        """Implementation of singleton interface"""
        def __init__(self):
            """
            """
            if os.path.exists(".broc.rc"):
                self._file = os.path.join(os.getcwd(), '.broc.rc')
            else:
                self._file = os.path.join(os.environ['HOME'], '.broc.rc')
            self._svn_repo_domain = 'https://svn.github.com'
            self._git_repo_domain = 'https://github.com'
            self._svn_postfix_branch = "BRANCH"
            self._svn_postfix_tag = "PD_BL"

        def __str__(self):
            """
            """
            return "svn repo domain: %s\ngit repo domain: %s\n \
svn     postfix branch: %s\nsvn postfix tag: %s"% (self._svn_repo_domain,
                                                   self._git_repo_domain,
                                                   self._svn_postfix_branch,
                                                   self._svn_postfix_tag)

        def Id(self):
            """
            test method, return singleton id
            """
            return id(self)

        def load(self):
            """
            load broc configurations
            Raise:
                if load config failed, raise BrocConfigError
            """
            try:
                # if configuration file does not exists in $HOME, create one
                if not os.path.isfile(self._file):
                    cfgfile = open(self._file, 'w')
                    conf = ConfigParser.ConfigParser()
                    conf.add_section('repo')
                    conf.set('repo', 'svn_repo_domain', self._svn_repo_domain)
                    conf.set('repo', 'git_repo_domain', self._git_repo_domain)
                    conf.set('repo', 'svn_postfix_branch', 'BRANCH')
                    conf.set('repo', 'svn_postfix_tag', 'PD_BL')
                    conf.write(cfgfile)
                    cfgfile.close()
                else:
                    cfgfile = open(self._file, 'r')
                    conf = ConfigParser.ConfigParser()
                    conf.read(self._file)
                    self._svn_repo_domain = conf.get('repo', 'svn_repo_domain')
                    self._git_repo_domain = conf.get('repo', 'git_repo_domain')
                    self._svn_postfix_branch = conf.get('repo', 'svn_postfix_branch')
                    self._svn_postfix_tag = conf.get('repo', 'svn_postfix_tag')
            except ConfigParser.Error as e:
                raise BrocConfigError(str(e))

        def RepoDomain(self, repo_type):
            """
            return repository domain
            Args:
                repo_type : BrocMode_pb2.Module.EnumRepo
            """
            if repo_type == BrocModule_pb2.Module.SVN:
                return self._svn_repo_domain
            elif repo_type == BrocModule_pb2.Module.GIT:
                return self._git_repo_domain

        def SVNPostfixBranch(self):
            """
            return postfix of svn branch
            """
            return self._svn_postfix_branch

        def SVNPostfixTag(self):
            """
            return postfix of svn tag
            """
            return self._svn_postfix_tag

        def Dump(self):
            """
            dump broc config
            """
            print("-- svn domain : %s" % self._svn_repo_domain)
            print("-- git domain : %s" % self._git_repo_domain)
            print("-- svn branch posfix : %s" % self._svn_postfix_branch)
            print("-- svn tag postfix   : %s" % self._svn_postfix_tag)

    # class BrocConfig
    __instance = None
    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if BrocConfig.__instance is None:
            # Create and remember instance
            BrocConfig.__instance = BrocConfig.__impl()
            BrocConfig.__instance.load()

        # Store instance reference as the only member in the handle
        self.__dict__['_BrocConfig__instance'] = BrocConfig.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
