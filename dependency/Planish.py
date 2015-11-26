#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
    This file gathers and plannishes the dependent modules
    Authors: zhousongsong(zhousongsong@baidu.com)
    Date:   2015/09/16 10:44:24

    ==================SVN EXAMPLE=========================
    CONFIGS("app/foo/sky@trunk")
    CONFIGS("app/foo/sky@trunk@12345") 
    CONFIGS("app/foo/sky@trunk@12346")
    
    CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH")
    CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH@12345")
    CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH@12346")

    CONFIGS("app/foo/sky@sky_1-0-0-1_BRANCH")
    CONFIGS("app/foo/sky@sky_1-0-0-1_BRANCH@1234")
    
    CONFIGS("app/foo/sky@sky_1-0-0-0_PD_BL")
    CONFIGS("app/foo/sky@sky_1-0-0-1_PD_BL")

    ==================GIT EXAMPLE=========================
    CONFIGS("sky@master")
    CONFIGS("sky@master@v1.0.0")

    CONFIGS("sky@dev")
    CONFIGS("sky@dev@v1.0.1")
    
    SVN Dependency conficting examples
    ==================================
    1. two different branches
       CONFIGS("app/foo/sky@sky_1-0-0-1_BRANCH")
       CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH")

    2. tag and branch
       CONFIGS("app/foo/sky@sky_1-0-0-0_PD_BL")
       CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH")

    3. trunk and branch
       CONFIGS("app/foo/sky@trunk")
       CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH")

    GIT Dependency conficting conditions
    ====================================
    1. two different branches
       CONFIGS("sky@master")
       CONFIGS("sky@dev")

       CONFIGS("sky@master")
       CONFIGS("sky@dev@v1.0.1")

       CONFIGS("sky@master@v1.0.0")
       CONFIGS("sky@dev")

       CONFIGS("sky@master@v1.0.0")
       CONFIGS("sky@dev@v1.0.1")
"""
import os
import sys
import time

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)

from dependency import PlanishUtil
from dependency import BrocTree
from dependency import BrocModule_pb2
from util import Function

 
class Planish(object):
    """
    class for planishing dependent modules
    """

    def __init__(self, main_module, repo_domain, logger, postfix):
        """
        Args:
            main_module : the BrocModule_pb2.Moduel object representing the main module
            repo_domain : the domain name of repository
            logger : the log facility object
            postfix : the list of postfix, [postfix_trunk, postfix_branche, postfix_tag]
        """
        self._dep_tree = BrocTree.BrocTree(main_module,
                                           repo_domain,
                                           logger,
                                           postfix)
        self.logger = logger
        self.planished_nodes = dict()  # module cvspath --> BrocNode

    def PlanishedNodes(self):
        """
        return the list of plainised BrocNode
        """
        return [x for k, x in self.planished_nodes.iteritems()]

    def DoPlanish(self, download_flag=True):
        """
        choose one version from multiple version of module
        Args:
            download_flag : whether download the code of module, if it is set True download code, and vice versa
        Returns:
            True if planish successfully, otherwise return False
        """
        self.logger.LevPrint('MSG', 'Analyzing dependency ...')
        # create dependent tree
        try:
            self._dep_tree.ConstructTree()
        except BrocTree.BrocTreeError as err:
            self.logger.LevPrint('ERROR', '%s' % err)
            return False
        #check graph has circles
        (ret, msg) = self._dep_tree.HasCircle()
        if ret:
            self.logger.LevPrint("ERROR",
                    "There is a circle in dependency graph\nCircle is [%s]" % msg, False)
            return False
        # dump origin dependency tree
        self._dep_tree.Dump() 

        nodes = self._dep_tree.AllNodes()
        for k, nodes in nodes.iteritems():
            for node in nodes: 
                # jump main module itself
                if node.module.is_main:
                    continue
                if node.module.module_cvspath not in self.planished_nodes:
                    self.planished_nodes[node.module.module_cvspath] = node
                else:
                    reserved_node = self.planished_nodes[node.module.module_cvspath]
                    ret = self._filter_dep_nodes(reserved_node, node)
                    if ret == 1:
                        self.planished_nodes[node.module.module_cvspath] = node
                    if ret == -1:
                        self.logger.LevPrint("ERROR", "dependent conficts(%s PK %s)" % \
                                             (reserved_node.module.origin_config, \
                                             node.module.origin_config), False)
                        return False

        self.logger.LevPrint('MSG', 'Analyzing dependency success')
        # dump planished dependency tree
        self.Dump()
        if download_flag:
            return self._download_modules()
        else:
            return True

    def _download_modules(self):
        """
        dnowload dependent module from repository
        Returns:
            download all modules successfully return True, otherwise return False
        """
        for k, node in self.planished_nodes.iteritems():
            if node.module.repo_kind == BrocModule_pb2.Module.SVN: 
                # the infos of local code equal Node's info
                if os.path.exists(node.module.root_path):
                    if self._dep_tree.SameSvnNode(node):
                        continue
                    else:
                        dst = "%s-%f" % (node.module.root_path, time.time())
                        self.logger.LevPrint("WARNING", "local code doesn't match BROC, \
reload it(%s)" % (node.module.origin_config))
                        Function.MoveFiles(node.module.root_path, dst)

                # generate command donwloading code from repository
                cmd = None
                url = node.module.url
                if node.module.revision:
                    url = "%s -r %s --force" % (url, node.module.revision)
                else:
                    url = "%s --force" % url
                cmd = "svn checkout %s %s" % (url, node.module.root_path)
            else:
                # for git
                cmd = "cd %s && git fetch --all" % node.module.module_cvspath
                if node.module.tag_name:
                    cmd += " && git checkout %s" % node.module.tag_name
                else:
                    cmd += " && git checkout %s" % node.module.branch_name

            self.logger.LevPrint("MSG", "%s" % cmd)
            ret, msg = Function.RunCommand(cmd)
            if ret != 0:
                self.logger.LevPrint("ERROR", "%s failed(%s)" % (cmd, msg))
                return False
        return True

    def _filter_dep_nodes(self, reserved, coming):
        """
        choose one module from the reserved and the coming node 
        1. level one module's priority is higher than other levels' modules
        2. modules with same branch can be compared
        3. modules with different branches couldn't be compared
        4. if one module is branch and the other is tag, they couldn't be compared
        Args:
            reserved : a BrocNode object left in self.planished_nodes already
            coming : a BrocNode object needed to check left or discard
        Returns:
            0 : reservered node is left
            1 : comming node is left
            -1 : conficts to determin which one node should be left
        """
        if reserved.module.dep_level <= 1 and coming.module.dep_level > 1:
            return 0

        if reserved.module.dep_level > 1 and coming.module.dep_level <= 1:
            return 1

        # branche and tag confict
        if reserved.module.br_kind != coming.module.br_kind:
            return -1

        # branches
        if reserved.module.br_kind == BrocModule_pb2.Module.BRANCH:
            # different branches confict
            if reserved.module.br_name != coming.module.br_name:
                return -1
            if int(reserved.module.revision) > int(coming.module.revision):
                return 0
            else:
                return 1
        # tags
        if reserved.module.br_kind == BrocModule_pb2.Module.TAG:
            #module.tag_name is like "ub_1-0-0-1_PD_BL"
            #TODO change other ways to get version
            reserved_version = reserved.module.tag_name.split('_')[1].split('-')
            coming_version = coming.module.tag_name.split('_')[1].split('-')
            for index in range(0, len(reserved_version)):
                if int(reserved_version[index]) > int(coming_version[index]):
                    return 0
                elif int(reserved_version[index]) < int(coming_version[index]):
                    return 1
                else:
                    continue
            return 0

    def Dump(self):
        """
        save the infos of dependent modules that have planished into file
        """
        config_file = os.path.join(self._dep_tree.Root().module.workspace, 
                                   self._dep_tree.Root().module.module_cvspath,
                                   ".BROC.PLANISHED.DEPS")
        config_list = []
        for k in self.planished_nodes:
            config_list.append(self.planished_nodes[k].module.origin_config)
        try:
            with open(config_file, 'w') as f:
                f.write("=========BROC PLANISNHED DEPENDENCY==========\n")
                f.write(self._dep_tree.Root().module.root_path + "\n\t")
                f.write("\n\t".join(config_list))
        except IOError as err:
            self.logger.LevPrint('ERROR', 'save planished dependency failed(%s)' % err)
