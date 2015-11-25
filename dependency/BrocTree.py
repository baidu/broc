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
            is_local : whether module code exists in local system
        """
        self.module = module
        self._children = []    # the list of kid nodes
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

    def EnableLocal(self):
        """
        mark the code of module exists in local system
        """
        self._is_local = True
 
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
    the dependent tree of all modules
    """
    def __init__(self, root, repo_domain, logger, postfix):
        """
        Args:
            root : the BrocModule_pb2.Moduel object, the root of BrocTree
            repo_domain : the damain of repository 
            logger : Log.Log object, the log facility object
            postfix : the list of postfix like [postfix_trunk, postfix_branche, postfix_tag]
        """
        self._root = BrocNode(root, None, True) 
        self._repo_domain = repo_domain
        self._logger = logger
        self._postfix = postfix
        self._node_queue = Queue.Queue() # the queue of BrocModule_pb2
        self._node_queue.put(self._root)
        self._all_nodes = dict()       # { module cvspath : [BrocNode...] }  storing all of gathered modules
        self._broc_dir = tempfile.mkdtemp() # the temporary directory storing all BROC files 
        self._done_broc = dict()       # module url --> [BrocNode...]
        self._checked_node = list()    # list to save the node which has been traversed.
        self._need_broc_list = list()  # list of no BROC modules

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
        to construct the denpendent tree 
        Raises:
            raise BrocTreeError
        """
        while not self._node_queue.empty():
            node = self._node_queue.get()
            self._handle_node(node)

        if len(self._need_broc_list) > 0:
            module_list = "There is no BROC in these modules:\n"
            for module_name in self._need_broc_list:
                module_list += module_name + '\n'
            raise BrocTreeError(module_list)

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

        try:
            # to fetch BROC file
            broc_path = self._check_broc(node)
            if broc_path is None:
                self._logger.LevPrint("ERROR", "fetch BROC failed")
                return 
            # get CONFIGS from BROC
            configs = PlanishUtil.GetConfigsFromBroc(broc_path) 
            kids = PlanishUtil.ParseConfigs(configs,
                                            node.module.workspace,
                                            node.module.dep_level + 1,
                                            node.module.repo_kind,
                                            self._repo_domain,
                                            self._postfix[0],
                                            self._postfix[1],
                                            self._postfix[2])
        except BaseException as err:
            self._logger.LevPrint("ERROR", "parse BROC(%s) failed" % node.module.url)
            raise BrocTreeError(str(err))

        kid_nodes = []
        for kid in kids:
            kid_node = BrocNode(kid, node, False)
            kid_nodes.append(kid_node)
            node.AddChild(kid_node)
            self._add_node(kid_node)
            self._node_queue.put(kid_node)
        # record the done broc file to prevernt from parse again
        self._done_broc[node.module.url] = kid_nodes

    def _check_broc(self, node):
        """
        to check BROC file
        Args:
            node : the object of BrocNode
        Returns:
            return the abs path of BROC file if check successfully
            return None if fail to check BROC file
        """
        broc_path = os.path.join(node.module.workspace, node.module.module_cvspath, 'BROC')
        # BROC exists in local file system
        if os.path.exists(broc_path):
            if node.module.repo_kind == BrocModule_pb2.Module.SVN:
                if self.SameSvnNode(node):
                    return broc_path
                else:
                    return self._download_broc(node)
            else:
                broc_dir = os.path.join(node.module.workspace, node.module.module_cvspath)
                cmd += "cd %s && git fetch --all && git checkout %s" \
                        % (broc_dir, node.module.br_name)
                if node.module.tag_name:
                    cmd += " && git checkout %s" % node.module.tag_name
                # to run cmd
                ret, msg = Function.RunCommand(cmd)
                if ret != 0:
                    self._logger.LevPrint("ERROR", "fail to find BROC(%s) failed(%s)" % (cmd, msg))
                    # FIX ME, maybe return None is better
                    raise BrocTreeError("%s\n%s" % (cmd, msg))
                else:
                    return broc_path
        # to dowonload BROC 
        else:
            return self._download_broc(node)


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
            return the path of BROC file if download successfully;
            return None if fail to download BROC
        """
        broc_path = None
        cmd = None
        if node.module.repo_kind == BrocModule_pb2.Module.SVN:
            _file = Function.CalcMd5(node.module.url)
            broc_url = os.path.join(node.module.url, 'BROC')
            broc_path = os.path.join(self._broc_dir, "%s_BROC" % _file)
            if node.module.revision:
                broc_url = "%s -r %s" % (broc_url, node.module.revision)
            cmd = "svn export %s %s" % (broc_url, broc_path)
        else:
            # for GIT
            broc_path = os.path.join(node.module.workspace, node.module.module_cvspath, 'BROC')
            cmd = "git clone %s %s && cd %s && git fetch --all " \
                  % (node.module.url, node.module.name, node.module.name)
            if node.module.br_name is not "master":
                cmd += " && cd %s && git checkout -b %s origin/%s" % (node.module.name, 
                                                                    node.module.br_name, 
                                                                    node.module.br_name)
            if node.module.tag_name:
                if "&&" in cmd:
                    cmd += " && git checkout %s" % node.module.tag_name
                else:
                    cmd += " && cd %s && git checkout %s" % (node.module.name,
                                                             node.module.tag_name)
 
        self._logger.LevPrint("MSG", "run command %s" % cmd)
        ret, msg = Function.RunCommand(cmd) 
        if ret != 0:
            self._logger.LevPrint("ERROR", "%s" % msg)
            self._need_broc_list.append(node.module.url)
            return None

        return broc_path

    def SameSvnNode(self, node):
        """
        to check whether the repo infos(url, revesion/commit_id) of local directroy equals to node's
        Args:
            node : BrocNode object of module
        Returns:
            return Ture | False
        Raises:
            raise BrocTreeError when encounter some errors
        """
        infos = RepoUtil.GetSvnUrlRevision(node.module.root_path, self._logger)
        if infos is None:
            raise BrocTreeError("parse module(%s) failed" % node.module.url)
        # check url
        if infos[0] != node.module.url:
            return False

        # check version
        if not node.module.revision: 
            last_version = RepoUtil.GetSvnRevisionFromUrl(node.module.url, self._logger)
            if last_version and infos[1] == last_version:
                return True
            else:
                return False
        else:
            return True if infos[1] == node.module.revision else False

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
        depth-First traverse dependency graph. self._checked_node is the list of traversed nodes.
        if there is a node which appears twice in the list, the graph must have a dependent circle.
        Args :
            node : Broc Tree Node
        Returns :
            True : dependency graph has circles
            False : dependency graph doesn't have circles
        """
        for kid in node.Children():
            # check is there a node which appears twice
            if kid.module.module_cvspath in self._checked_node:
                # store the node which appears twice, then we can get a path with circle in it.
                self._checked_node.append(kid.module.module_cvspath)
                return True
            # store the node which has been traversed.
            self._checked_node.append(kid.module.module_cvspath)
            ret = self._has_circle(kid)
            if ret:
                return True
            self._checked_node.pop()

        return False

    def HasCircle(self):
        """
        check whether the dependency graph has circles 
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
