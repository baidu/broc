#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module manage source files(.c .cpp)

Authors: zhousongsong(zhousongsong@baidu.com)
Date:    2015/09/14 13:28:57
"""

import os
import sys
import copy

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)

from dependency import SyntaxTag
from dependency import Builder

class SourceType(object):
    """
    Source Type
    """
    SOURCE = 0
    C = 1
    CXX = 2
    

class Source(object):
    """
    base class
    """
    TYPE = SourceType.SOURCE
    EXTS = ()
    def __deepcopy__(self, memo):
        """
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __str__(self):
        """
        return infile, outfile, compiler, compile options infos
        """
        if self.builder:
            return self.builder.GetBuildCmd()
        else:
            return self.infile

    def __init__(self, infile, env, args):
        """
        Args:
            infile : the cvs path of source file
            env : Environment object
            args : the compile option args
        """
        self.infile = infile                     # the cvs path of source file
        self.outfile = ""                        # the cvs path of object file, ie .o  
        self.args = args                         # compile option args
        self.env = env
        self.target = None                       # Target object that Source belongs to

        # compile options
        self.includes = ['.', 'broc_out']
        self.cppflags = []
        self.cflags = []
        self.cxxflags = []

        # builder
        self.builder = None 

    def __eq__(self, v):
        """
        call when compare tow Source objects
        """
        return self.infile == v._infile

    def GetBuildCmd(self):
        """
        return build cmd
        """
        return self.builder.GetBuildCmd()

    def Compiler(self):
        """
        return the compiler cmd
        """
        pass

    def InFile(self):
        """
        return source file
        """
        return self.infile

    def Target(self):
        """
        return target object that source object belongs to 
        """
        return self.target

    def SetTarget(self, target):
        """
        set target that source object belongs to 
        """
        self.target = target

    def Env(self):
        """
        return the Envrionment object that source object belongs to
        """
        return self.env 

    def OutFile(self):
        """
        return the cvs path of result file
        """
        return self.outfile

    def CalcObjectName(self):
        """
        caculate the cvs path of result file
        cvs path = 'broc_out' + '/' + cvs path of infile + '/' + '%s_%s_%s.o' % (self.target.TYPE, self.target.name, file name)
        """
        cvs_dir = os.path.dirname(self.infile)
        root, _ = os.path.splitext(os.path.basename(self.infile))
        obj_file = os.path.join(cvs_dir,
                                "%s_%s_%s.o" % (self.target.TYPE, self.target.Name(), root))
        if not obj_file.startswith('broc_out'):
            self.outfile = os.path.join("broc_out", obj_file)
        else:
            self.outfile = obj_file

    def Action(self):
        """
        parser compile flags including include path, preprocess flags, 
        c compile flags and cxx compile flags
        """
        incpaths_flag = False
        cppflags_flag = False
        cflags_flag = False
        cxxflags_flag = False
        # parse all args and take arg as local flag
        for args in self.args:
            for arg in args:
                if isinstance(arg, SyntaxTag.TagInclude):
                    incpaths_flag = True
                    self.includes.extend(arg.V())
                elif isinstance(arg, SyntaxTag.TagCppFlags):
                    cppflags_flag = True 
                    self.cppflags.extend(arg.V())
                elif isinstance(arg, SyntaxTag.TagCFlags):
                    cflags_flag = True 
                    self.cflags.extend(arg.V())
                elif isinstance(arg, SyntaxTag.TagCxxFlags):
                    cxxflags_flag = True
                    self.cxxflags.extend(arg.V())
                else:
                    continue

        # if local flag is empty, use module global flag
        if not incpaths_flag:
            self.includes = self.env.IncludePaths().V()
        if not cxxflags_flag:
            self.cxxflags = self.env.CxxFlags().V()
        if not cppflags_flag:
            self.cppflags = self.env.CppFlags().V()
        if not cflags_flag:
            self.cflags = self.env.CFlags().V()

class CSource(Source):
    """
    C Source Code
    """
    TYPE = SourceType.C
    EXTS = ('.c',)
    def __init__(self, infile, env, args):
        """
        """
        Source.__init__(self, infile, env, args)

    def Compiler(self):
        """
        return the path of compiler
        """
        return self.env.CC()

    def Action(self):
        """
        parse compile options, and join all options as a string object       
        """
        Source.Action(self)
        self.CalcObjectName()
        options = ['-DZUES']
        options.extend(self.cppflags + self.cflags)
        self.builder = Builder.ObjBuilder(self.outfile, self.infile, self.includes, 
                                          options, self.env.CC(), self.env.Workspace())
        self.builder.CalcHeaderFiles()
        

class CXXSource(Source):
    """
    C++ Source Code
    """
    TYPE = SourceType.CXX
    EXTS = ('.cpp', '.cc', '.cxx')
    def __init__(self, infile, env, args):
        """
        """
        Source.__init__(self, infile, env, args)

    def Compiler(self):
        """
        return the path of Compiler
        """
        return self.env.CXX()

    def Action(self):
        """
        init builder
        """
        Source.Action(self)
        self.CalcObjectName()
        options = ['-DZUES']
        options.extend(self.cppflags + self.cxxflags)
        self.builder = Builder.ObjBuilder(self.outfile, self.infile, self.includes, 
                                          options, self.env.CXX(), self.env.Workspace())
        self.builder.CalcHeaderFiles()
