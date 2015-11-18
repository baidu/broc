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
    Date:   2015/09/17 10:50:20
"""
import os
import sys
import Queue
import tempfile

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)

from dependency import PlanishUtil
from dependency import BrocModule_pb2
from util import Function
from util import RepoUtil


class BrocTreeError(Exception):
    """
    get CONFIGS from BROC file
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

class BrocNode(object):
    """
    one node representes one module
    """ 
    def __init__(self, module, parent, is_local):
        """
        Args:
            module : the BrocModule_pb2.Module object
            parent : the BrocNode object representing the parent node
            is_local : module code exists or not in local
        """
        self.module = module
        self._children = []
        self._parent = parent
        self._is_local = is_local

    def __str__(self):
        """
        """
        line = "node url: %s\n" % self.module.url
        line += "node level: %d\n" % self.module.dep_level
        line += "node is local: %s\n" % ('YES' if self._is_local else 'NO')
        return line

    def AddChild(self, kid):
        """
        add a new child node
        Args:
            kid : BrocNode object 
        """
        self._children.append(kid)

    def Children(self):
        """
        return the list of child nodes
        """
        return self._children

    def Parent(self):
        """
        return parent node
        """
        return self._parent

    def IsLocal(self):
        """
        return self._is_local
        """
        return self._is_local

    def SetLocal(self, local):
        """
        Args:
            local : bool value, set the local flag
        """
        self._is_local = local
 
    def Dump(self):
        """
        return a string object representing the dependent list
        """
        if self.module.is_main:
            deps = "=========BROC ORIGIN DEPENDENCY==========\n"
            deps += self.module.root_path + "\n"
        else:
            deps = "\t" * self.module.dep_level + self.module.origin_config + '\n'

        return deps          

       
class BrocTree(object):
    """
    class for planishing dependent modules
    # FIX ME how to avoid the circle dependency
    """
    def __init__(self, root, repo_domain, logger, postfix):
        """
        Args:
            root : the BrocModule_pb2.Moduel object, the root of BrocTree
            repo_domain : the damain of repository 
            logger : the log facility object
            postfix : the list of postfix, [postfix_trunk, postfix_branche, postfix_tag]
        """
        self._root = BrocNode(root, None, True) 
        self._repo_domain = repo_domain
        self._logger = logger
        self._postfix = postfix
        self._node_queue = Queue.Queue() # the queue of BrocModule
        self._node_queue.put(self._root)
        self._all_nodes = dict()       # module cvspath ---> [BrocNode...], storing all of gathered modules
        self._broc_dir = tempfile.mkdtemp()
        self._done_broc = dict()       # module url --> [BrocNode...]
        self._checked_node = list()    #list to save the node which has been traversed.

    def __del__(self):
        """
        """
        Function.DelFiles(self._broc_dir)

    def Root(self):
        """
        return root node of tree
        """
        return self._root

    def AllNodes(self):
        """
        return all nodes
        """
        return self._all_nodes

    def ConstructTree(self):
        """
        to construct the broc tree 
        Raises:
            raise BrocTreeError
        """
        while not self._node_queue.empty():
            node = self._node_queue.get()
            self._handle_node(node)

    def _handle_node(self, node):
        """
        Args:
            node : BrocNode object of module
        Raises:
            if handle node failed, raise BrocTreeError
        """
        # if node.module.url has been handled in other module's BROC
        if node.module.url in self._done_broc:
            for kid_node in self._done_broc[node.module.url]:
                node.AddChild(kid_node)
            return 

        configs = None
        broc_file = os.path.join(node.module.workspace, node.module.module_cvspath, 'BROC')
        # node of main module
        if node.module.is_main:
            if not os.path.exists(broc_file):
                raise BrocTreeError('no BROC file in main moudle(%s)' % node.module.module_cvspath) 
            else:
                configs = PlanishUtil.GetConfigsFromBroc(broc_file)

        # nodes of dependent modules
        else:
            # to check whether the version of local BROC file equals Node's 
            if os.path.exists(broc_file) and self._is_same_node(node):
                try:
                    node.SetLocal(True)
                    configs = PlanishUtil.GetConfigsFromBroc(broc_file)
                except PlanishUtil.PlanishError as err:
                    raise BrocTreeError(str(err))
            # download from repository to temporary file
            else:
                try:
                    broc_file = self._download_broc(node)
                    configs = PlanishUtil.GetConfigsFromBroc(broc_file)
                except BaseException as err:
                    raise BrocTreeError(str(err))
        # to handle dependent modules
        try:
            kids = PlanishUtil.ParseConfigs(configs,
                                            node.module.workspace,
                                            node.module.dep_level + 1,
                                            node.module.repo_kind,
                                            self._repo_domain,
                                            self._postfix[0],
                                            self._postfix[1],
                                            self._postfix[2])
        except PlanishUtil.PlanishError as e:
            self._logger.LevPrint("ERROR", "parse BROC(%s) failed" % node.module.url)
            raise BrocTreeError(str(e))

        kid_nodes = []
        for kid in kids:
            kid_node = BrocNode(kid, node, False)
            kid_nodes.append(kid_node)
            node.AddChild(kid_node)
            self._add_node(kid_node)
            self._node_queue.put(kid_node)
        # record the done broc file to prevernt from parse again
        self._done_broc[node.module.url] = kid_nodes

    def _add_node(self, node):
        """
        add nodes
        Args:
            node : the object of BrocNode
        """
        if node.module.module_cvspath not in self._all_nodes:
            self._all_nodes[node.module.module_cvspath] = []
        
        self._all_nodes[node.module.module_cvspath].append(node)

    def _download_broc(self, node):
        """
        download BROC from node's repository 
        Args:
            node : BrocNode object of module
        Returns:
            return the path of temporary BROC
        Raises:
            raise BrocTree.Error
        """
        _file = Function.CalcMd5(node.module.url)
        tmp_file = os.path.join(self._broc_dir, 
                                _file + '_' + 'BROC')
        cmd = None
        url = os.path.join(node.module.url, 'BROC')
        if node.module.revision:
            url = "%s -r %s" % (url, node.module.revision)
        if node.module.repo_kind == BrocModule_pb2.Module.SVN:
            cmd = "svn export %s %s" % (url, tmp_file)
        else:
            #TODO FIX ME in git
            cmd = "git archive"
        # self._logger.LevPrint("MSG", "run command %s" % cmd)
        (ret, msg) = Function.RunCommand(cmd) 
        if ret != 0:
            raise BrocTreeError(msg)

        return tmp_file

    def _is_same_node(self, node):
        """
        to check the repo infos(url, revesion/commit_id) of local director equals to node's, 
        if both equals parse the local BROC file to get dependent modules, 
        otherwise download BROC from repository
        Args:
            node : BrocNode object of module
        Returns:
            return Ture | False
        Raises:
            raise BrocTreeError when encounter some errors
        """
        infos = None
        if node.module.repo_kind == BrocModule_pb2.Module.SVN:
            infos = RepoUtil.GetSvnUrlRevision(node.module.root_path, self._logger)
        else:    
            #TODO fetch commit id or tag name
            infos = RepoUtil.GetGitUrl(node.module.root_path, self._logger)

        if infos is None:
            raise BrocTreeError("parse module(%s) failed" % node.module.url)

        # check url
        if infos[0] != node.module.url:
            return False
        if node.module.repo_kind == BrocModule_pb2.Module.SVN:
            # check version
            if not node.module.revision: 
                # TODO fetch the newest version of module from svn url
                last_version = RepoUtil.GetSvnRevisionFromUrl(node.module.url, self._logger)
                if last_version and infos[1] == last_version:
                    return True
                else:
                    return False
            else:
                return True if infos[1] == node.module.revision else False
        else:
            #TODO to check git tag name
            return True

    def _dump(self, node, config_list):
        config_list.append(node.Dump())
        for n in node.Children():
            self._dump(n, config_list)

    def Dump(self):
        """
        save the infos of dependent module into file
        """
        config_list = []
        config_file = os.path.join(self._root.module.workspace,
                                   self._root.module.module_cvspath, 
                                   ".BROC.ORIGIN.DEPS")
        self._dump(self._root, config_list)
        
        try:
            with open(config_file, 'w') as f:
                f.write("".join(config_list))
        except IOError as err:
            self._logger.LevPrint('ERROR', 'save origin dependency failed(%s)' % err)

    def _has_circle(self, node):
        """
        Depth-First Traverse dependency graph.self._checked_node is the list of traversed nodes.
        if there is a node which appears twice in the list, the graph must have a circle.
        Args :
            node : Broc Tree Node
        Returns :
            True : dependency graph has circles
            False : dependency graph doesn't have circles
        """
        for kid in node.Children():
            #check is there a node which appears twice
            if kid.module.module_cvspath in self._checked_node:
                #store the node which appears twice, then we can get a path with circle in it.
                self._checked_node.append(kid.module.module_cvspath)
                return True
            #store the node which has been traversed.
            self._checked_node.append(kid.module.module_cvspath)
            ret = self._has_circle(kid)
            if ret:
                return True
            self._checked_node.pop()
        return False

    def HasCircle(self):
        """
        check the dependency graph has circles or not
        Returns :
            True : dependency graph has circles
            False : dependency graph doesn't has circles
        """
        root_node = self._root
        self._checked_node.append(root_node.module.module_cvspath)
        ret = self._has_circle(root_node)
        msg = ""
        if ret:
            msg = self._checked_node[0]
            for i in range(1, len(self._checked_node)):
                msg = msg + ' -> ' + self._checked_node[i]
        return ret, msg
