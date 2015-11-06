#!/usr/bin/env python
# -*- coding: utf-8 -*- 

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
    Description : manage config file $HOME/.broc.rc
    Authors     : zhousongsong(zhousongsong@baidu.com)
    Date        : 2015-09-18 10:28:23
"""

import os
import sys
import ConfigParser

broc_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
sys.path.insert(0, broc_dir)

from dependency import BrocModule_pb2

class BrocConfig(object):
    """
    this class manages the .broc.rc in $HOME 
    """
    def __init__(self):
        """
        """
        self._file = os.path.join(os.environ['HOME'], '.broc.rc')
        self._svn_repo_domain = 'https://svn.baidu.com'
        self._git_repo_domain = 'https://git.baidu.com'
        self._svn_postfix_trunk = "trunk"
        self._svn_postfix_branch = "BRANCH"
        self._svn_postfix_tag = "PD_BL"

    def __str__(self):
        """
        """
        return "svn repo domain: %s\ngit repo domain: %s\nsvn postfix trunk: %s \
svn postfix branch: %s\nsvn postfix tag: %s"% (self._svn_repo_domain, 
                                               self._git_repo_domain, 
                                               self._svn_postfix_trunk,
                                               self._svn_postfix_branch,
                                               self._svn_postfix_tag)

    def load(self):
        """
        load broc configurations
        Returns:
            return (ret, msg)
            if load successfully, ret is True
            if load failed, ret is False and msg is detail content
        """
        try:
            # if configuration file does not exists in $HOME, create one
            if not os.path.isfile(self._file):
                cfgfile = open(self._file, 'w')
                conf = ConfigParser.ConfigParser()
                conf.add_section('repo')
                conf.set('repo', 'svn_repo_domain', self._svn_repo_domain)
                conf.set('repo', 'git_repo_domain', self._git_repo_domain)
                conf.set('repo', 'svn_postfix_trunk', 'trunk')
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
                self._svn_postfix_trunk = conf.get('repo', 'svn_postfix_trunk')
                self._svn_postfix_branch = conf.get('repo', 'svn_postfix_branch')
                self._svn_postfix_tag = conf.get('repo', 'svn_postfix_tag')
        except ConfigParser.Error as e:
            return (False, str(e))

        return (True, '') 

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

    def SVNPostfixTrunk(self):
        """
        return postfix of svn trunk
        """
        return self._svn_postfix_trunk

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
