# !/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module manage info generate by BROC file.

Authors: zhousongsong(zhousongsong@baidu.com)
Date:    2015/09/09 17:23:06
"""

import os
import sys
import copy
import threading

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)

from dependency import SyntaxTag
from dependency import BrocModule_pb2
from util import Function


class Environment(object):    
    """
    one Environment represents one BROC file
    """
    def __deepcopy__(self, memo):
        """
        deep copy
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __str__(self):
        """
        """
        line = ''
        line += '******************************************\n'
        line += "compiler dir: %s\n" % self._compiler_dir
        line += 'cc: %s\n' % self._cc
        line += 'cxx: %s\n' % self._cxx
        line += '\n'
        line += 'cppflags: %s\n' % self._g_cppflags.V()
        line += 'cflags: %s\n' % self._g_cflags.V()
        line += 'cxxflags: %s\n' % self._g_cxxflags.V()
        line += 'linkflags: %s\n' % self._g_linkflags.V()
        line += '\n\n'
        line += 'sources: \n'
        line += 'targets: \n'
        line += '******************************************'
        return line

    def __init__(self, module):       
        """
        Args:
            module : BrocModule_pb.Module object
        """
        self._module = module
        self._build_mode = 'debug'       # debug | release 

        # compiler infos
        self._cc = 'gcc'
        self._cxx = 'g++'
        self._compiler_dir = ''

        # global preporcess and compile flags in one BROC file
        self._g_cppflags = SyntaxTag.TagCPPFLAGS()
        self._g_cflags = SyntaxTag.TagCFLAGS()
        self._g_cxxflags = SyntaxTag.TagCXXFLAGS()
        self._g_incpaths = SyntaxTag.TagINCLUDE()
        self._g_incpaths.AddV('. broc_out')
        self._g_linkflags = SyntaxTag.TagLDFLAGS()

        # for tag PUBLISH
        self._publish_cmd = []

        self._sources = []
        self._targets = []

    def DisableDebug(self):
        """
        set build mode as release
        """
        self._build_mode = 'release'

    def BuildMode(self):
        """
        return build mode
        """
        return self._build_mode

    def Workspace(self):
        """
        return abs path of workspace
        """
        return self._module.workspace

    def ModulePath(self):
        """
        return abs path of module's directory
        """
        return os.path.join(self._module.workspace, self._module.module_cvspath)

    def ModuleCVSPath(self):
        """
        return the cvs path of module
        """
        return self._module.module_cvspath

    def BrocDir(self):
        """
        return the directory's abs path of broc file
        """
        return os.path.dirname(os.path.join(self._module.workspace, self._module.broc_cvspath))

    def BrocCVSDir(self):
        """
        return the directory's cvs path of broc file
        """
        return os.path.dirname(self._module.broc_cvspath) 

    def BrocCVSPath(self):
        """
        return the cvs path of directory of broc file
        """
        return self._module.broc_cvspath

    def BrocPath(self):
        """
        the abs path of broc file
        """
        return os.path.join(self._module.workspace, self._module.broc_cvspath)

    def OutputPath(self):
        """
        return abs path of module's output, ie $OUT
        """
        return os.path.join(self._module.workspace, 
                            "broc_out", 
                            self._module.module_cvspath,
                            "output")

    def OutputRoot(self):
        """
        return the root directory of output path, ie $OUT_ROOT
        """
        return os.path.join(self._module.workspace, 'broc_out')

    def SvnPath(self):
        """
        return module svn path
        """
        return self._module.root_path

    def SvnUrl(self):
        """
        return module svn url
        """
        return self._module.url

    def SvnRevision(self):
        """
        return svn revision
        """
        return self._module.revision

    def SvnLastChangedRev(self):
        """
        return the last changed revision of svn
        """
        return self._module.last_changed_rev

    def GitPath(self):
        """
        Returns:
            a string, the local path of module
        """
        return self._module.root_path

    def GitUrl(self):
        """
        Returns:
            a stirng, the git url of module
        """
        return self._module.url
    
    def GitCommitID(self):
        """
        Returns:
            a stirng, the id of last commition
        """
        return self._module.commit_id

    def GitBranch(self):
        """
        Returns:
            a string, the branch name of moudle
        """
        return self._module.br_name

    def GitTag(self):
        """
        Returns:
            a string, the tag name of module
        """
        return self._module.tag_name

    def CompilerDir(self):
        """
        return compiler dir
        """
        return self._compiler_dir

    def CC(self):
        """
        return the path of c compiler
        """
        return os.path.join(self._compiler_dir, 'gcc')

    def CXX(self):
        """
        return the path of cxx compiler
        """
        return os.path.join(self._compiler_dir, 'g++')

    def SetCompilerDir(self, k):
        """
        set compiler directory
        """
        self._compiler_dir = k

    def LDFlags(self):
        """
        return global link flags
        """
        return self._g_linkflags

    def CppFlags(self):
        """
        return global CppFlags
        """
        return self._g_cppflags

    def CFlags(self):
        """
        return global CFlags
        """
        return self._g_cflags

    def CxxFlags(self):
        """
        return global CxxFlags
        """
        return self._g_cxxflags

    def IncludePaths(self):
        """
        return global include paths
        """
        return self._g_incpaths

    def Sources(self):
        """
        return all source objects
        """
        return self._sources

    def Targets(self):
        """
        return the list of all target objects
        """
        return self._targets

    def AddPublish(self, src, dst):
        """
        add publish cmd 
        Args:
            src : source files
            dst : the destination starting with $OUT
        """
        _dst = os.path.normpath(dst.replace("$OUT", self.OutputPath()))
        srcs = src.split()
        for s in srcs:
            _src = os.path.normpath(os.path.join(self.BrocCVSDir(), s))
            cmd = "mkdir -p %s && cp -rf %s %s" % (_dst, _src, _dst)
            self._publish_cmd.append(cmd)

    def AppendSource(self, v):
        """
        add source object
        """
        self._sources.append(v)

    def AppendTarget(self, v):
        """
        add target object
        """
        # to avoid targets with same name and same type
        for t in self._targets:
            if t.Name() == v.Name() and t.TYPE == v.TYPE:
                return False

        self._targets.append(v)
        return True

    def Action(self):
        """
        parse target's compile options
        """
        for target in self._targets:
            target.Action()

    def DoPublish(self):
        """
        do publish cmd
        """
        for cmd in self._publish_cmd:
            ret, msg = Function.RunCommand(cmd)
            if ret != 0:
                return (False, msg)

        return (True, '')
        


#GLOBAL VARIABLES.                    
ENV = dict()
def SetCurrent(env):
    """
    set current env object, one env one thread
    """
    global ENV
    ENV[threading.current_thread().ident] = env


def GetCurrent():
    """
    return current evn object
    """
    global ENV
    return ENV[threading.current_thread().ident] 

