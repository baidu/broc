#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
    This file gathers and plannishes the dependent modules
    Authors: zhousongsong(doublesongsong@gmail.com)
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
from dependency import BrocConfig
from util import Function
from util import RepoUtil
from util import Log


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
            is_local : to mark whether module code exists in local file system
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
        set the code of module exists in local system
        """
        self._is_local = True
 
    def Dump(self, level):
        """
        return a string object representing the dependent list
        """
        if self.module.is_main:
            deps = "=========BROC ORIGIN DEPENDENCY==========\n"
            deps += self.module.root_path + "\n"
        else:
            deps = "\t" * level + self.module.origin_config + '\n'

        return deps          

       
class BrocTree(object):
    """
    the dependent tree of all modules
    """
    class __impl(object):
        """Implementation of singleton interface"""
        def __init__(self):
            """
            """
            self._root = None

        def __del__(self):
            """
            """
            pass

        def Id(self):
            """
            Test method, return singleton object id
            """
            return id(self)

        def Root(self):
            """
            return root node of tree
            """
            return self._root

        def SetRoot(self, root):
            """
            Set root node that represents main module
            Args:
                root : the BrocNode object representing main module
            """
            if not self._root:
                self._root = root
                broc_config = BrocConfig.BrocConfig()
                self._repo_damain = broc_config.RepoDomain(root.module.repo_kind)
                self._postfix = [broc_config.SVNPostfixBranch(), broc_config.SVNPostfixTag()]
                broc_file = os.path.join(root.module.workspace, root.module.broc_cvspath)

        def GetNodeHash(self, node):
            """
            return the hash value of node
            node hash value = hash(module_cvspath) + hash(BROC) + hash(module tag/branch type) + hash(module tag/branch name)
            Args:
                node : the BrocNode object
            """
            key = None
            if node.module.br_kind == BrocModule_pb2.Module.TAG:
                key = node.module.module_cvspath + str(node.module.br_kind) + node.module.tag_name
            else:
                key = node.module.module_cvspath + str(node.module.br_kind) + node.module.br_name

            return Function.CalcHash(key)

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
            infos = RepoUtil.GetSvnUrlRevision(node.module.root_path, Log.Log())
            if infos is None:
                raise BrocTreeError("parse module(%s) failed" % node.module.url)
            # check url
            if infos[0] != node.module.url:
                return False

            # check version
            if not node.module.revision: 
                last_version = RepoUtil.GetSvnRevisionFromUrl(node.module.url, Log.Log())
                if last_version and infos[1] == last_version:
                    return True
                else:
                    return False
            else:
                return True if infos[1] == node.module.revision else False

        def _dump(self, node, config_list, level):
            config_list.append(node.Dump(level))
            for n in node.Children():
                self._dump(n, config_list, level + 1)

        def Dump(self):
            """
            save the infos of dependent module into file
            """
            config_list = []
            config_file = os.path.join(self._root.module.workspace,
                                       self._root.module.module_cvspath, 
                                       ".BROC.ORIGIN.DEPS")
            self._dump(self._root, config_list, 0)
            
            try:
                with open(config_file, 'w') as f:
                    f.write("".join(config_list))
            except IOError as err:
                Log.Log().LevPrint('ERROR', 'save origin dependency failed(%s)' % err)

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


    # class BrocTree
    __instance = None
    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if BrocTree.__instance is None:
            # Create and remember instance
            BrocTree.__instance = BrocTree.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_BrocTree__instance'] = BrocTree.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
    
