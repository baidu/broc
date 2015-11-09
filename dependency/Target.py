#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module manage the bin/.a

Authors: zhousongsong(zhousongsong@baidu.com)
Date:    2015/09/15 10:34:31
"""

import os
import sys
import copy

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)
from dependency import Source
from dependency import Builder
from util import Function
from util import Log

class TargetType(object):
    """
    enum of target type
    """
    TARGET = 1      # TARGET, not used
    APP = 2         # APPLICATION
    UT_APP = 3      # UT_APPLICAATION
    LIB = 4         # STATIC_LIBRARY
    PROTO_LIB = 5   # PROTO_LIBRARY


class Target(object):
    """
    target base class
    """
    TYPE = TargetType.TARGET
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
        """
        if self.builder:
            return self.builder.__str__() 
        else:
            return ""

    def __init__(self, name, env, tag_sources, tag_libs):
        """
        Args:
            name : the name of target, name composes of [A-Z a-z 0-9 _]
            env : the Environment object that target belongs to
            tag_sources : the object of SyntaxTag.TagSources
            tag_libs : the object of SyntaxTag.TagLibs
        """
        self.name = name                # name
        self.env = env                  # Environment object
        self.tag_sources = tag_sources  # TagSource object
        self.tag_libs = tag_libs        # TagLbs object

        self.compiler = env.CC()        # default compiler is gcc, if there is one source whose TYPE is Source.SourceType.CXX,
                                        # in self._tag_srouces, the compiler will become g++
        self.outfile = ''               # the cvspath of output file  "$OUT" + "/" + [bin|lib|test] + "/" + [prefix] + self.name + [postfix]
        # all infile of Source objects 
        if self.tag_sources:
            self.infiles = set(sorted(
                           map(lambda x: os.path.normpath(x.InFile()), self.tag_sources.V())))
        else:
            self.infiles = set()
        self.objects = None             # set of all .o file
        # all cvs path of .a files
        if tag_libs:
            self.libs = set(sorted(map(lambda x: x, self.tag_libs.V())))
        else:
            self.libs = set()

        self.builder = None
        
    def Name(self):
        """
        return the name of target
        """
        return self.name

    def OutFile(self):
        """
        return the cvs path of result file
        """
        return self.outfile

    def InFiles(self):
        """
        return the set of cvs path of all source objct's infile
        """
        return self.infiles

    def Env(self):
        """
        return the env object that target belongs to
        """
        return self.env

    def Compiler(self):
        """
        return the abs path of Compiler
        """
        return self.compiler

    def Sources(self):
        """
        return the list of Source object
        """
        return self.tag_sources.V()

    def Objects(self):
        """
        return the set of .o files
        """
        return self.objects    

    def Libs(self):
        """
        return the set of .a files
        """
        return self.libs

    def Action(self):
        """
        parse all Source objects
        """
        # gather 
        objects = set()
        for source in self.tag_sources.V():
            source.SetTarget(self)
            source.Action()
            objects.add(source.OutFile())
            # if there is one CXX Source, use g++ 
            if source.TYPE == Source.SourceType.CXX:
                self.compiler = self.env.CXX()
        
        self.objects = set(sorted(objects))

        
class Application(Target):
    """
    for tag APPLICATION
    """
    TYPE = TargetType.APP
    def __init__(self, name, env, tag_sources, links, tag_libs):
        """
        Args:
            name : the name of binary file
            env : the object of Environment
            sources : the tag Syntaxtag.TagSource object
            links : the SyntaxTag.TagLDFlags object
            libs : the SyntaxTag.TagLibs object
        """
        Target.__init__(self, name, env, tag_sources, tag_libs)
        if links:
            self.link_options = links.V() # list[flag1, flag2 ...]
        self.outfile = os.path.normpath(os.path.join('broc_out', 
                                                      self.env.ModuleCVSPath(), 
                                                      'output',
                                                      'bin',
                                                      self.name))
    
    def Action(self):
        """
        parse all Source objects, link flags and libs
        """
        Target.Action(self)
        # if local flags is empty, use global flags of module(env)
        if not self.link_options:
            self.link_options = self.env.LDFlags().V()

        self.builder = Builder.BinBuilder(self.outfile, 
                                          self.objects, 
                                          self.libs,
                                          self.link_options,
                                          self.compiler,
                                          self.env.Workspace())


class UTApplication(Application):
    """
    for tag UT_APPLICATION
    """
    TYPE = TargetType.UT_APP
    def __init__(self, name, env, tag_sources, links, tag_libs, ut_args):
        """
        Args:
            name : the name of ut_application
            env : the object of Environment that self belongs to
            tag_sources : the Syntaxtag.TagSource object
            links: the SyntaxTag.TagLinks object
            tag_libs : the SyntaxTag.Taglibs object
            ut_args : the SyntaxTag.TagUTArgs object
        """
        Application.__init__(self, name, env, tag_sources, links, tag_libs)
        if ut_args:
            self._ut_args = ut_args.V()   # list of arguments
        self.outfile = os.path.normpath(os.path.join('broc_out', 
                                                      self.env.ModuleCVSPath(), 
                                                      'output/test',
                                                      self.name))

    def Action(self):
        """
        """
        Application.Action(self)
        #TODO ug_args


class StaticLibrary(Target):
    """
    for tag STATIC_LIBRARY
    """
    TYPE = TargetType.LIB
    def __init__(self, name, env, tag_sources, tag_libs):
        """
        Args:
            name : the name of ut_application
            env : the object of Environment that self belongs to
            tag_sources : the SyntaxTag.TagSource object
            tag_libs : the SyntaxTag.Taglibs object
        """
        Target.__init__(self, name, env, tag_sources, tag_libs)
        root, _ = os.path.splitext(self.name)
        self.outfile = os.path.normpath(os.path.join('broc_out',
                                                     self.env.ModuleCVSPath(),
                                                     'output/lib',
                                                     'lib%s%s' % (root, '.a')))

    def Action(self):
        """
        """
        Target.Action(self)
        self.builder = Builder.LibBuilder(self.outfile, 
                                          self.objects, 
                                          self.libs,
                                          'ar',
                                          self.env.Workspace())

    def DoCopy(self):
        """
        if lib files are built already, just copy it from code directory to output directory
        Returns:
            return True if copy success
            return False if fail to copy
        """
        if len(self.tag_sources.V()):
            Log.Log().LevPrint("ERROR", 'StaticLibrary(%s) can not copy because \
                                its source is not empty' % self.name)
            return False
       
        root, _ = os.path.splitext(self.name)
        frm = os.path.join(self.env.ModuleCVSPath(), 'lib', 'lib%s%s' % (root, '.a'))
        to = os.path.join("broc_out", self.env.ModuleCVSPath(), 'output/lib')
        cmd = "mkdir -p %(to)s && cp -Rp %(frm)s %(to)s" % (locals())
        Log.Log().LevPrint('MSG', '[PreCopy] %s' % cmd)
        ret, msg = Function.RunCommand(cmd)
        if ret != 0:
            Log.Log().LevPrint("ERROR", "[ERROR] %s\n%s" % (cmd, msg))
            return False
        else:
            return True 


class ProtoLibrary(object):
    """
    for tag PROTO_LIBRARY
    """
    TYPE = TargetType.PROTO_LIB
    def __init__(self, env, protos, tag_include, protoflags):
        """
        Args:
            env : the Environment objet
            protos : a string spereated by blank character, representing the relative path of a group of proto files
            tag_includes: SyntaxTag.TagInclude object
            protoflags : SyntaxTag.TagProtoFlags object
            tag_libs : the SyntaxTag.Tag
        """
        self.env = env
        self._protos = protos
        self._tag_include = tag_include
        self._tag_protoflags = protoflags
        self._proto_cmds = set()

    def PreAction(self):
        """
        parse proto flags and gernerate the command to handle proto file
        Returns:
            return (True, '') if deal with proto files successfully, otherwise return (False, 'error msg')
        """
        proto_dirs = set()
        # find the cvs path of directory of all proto files
        for proto in self._protos.split():
            proto_dirs.add(os.path.join(self.env.BrocCVSDir(), os.path.dirname(proto)))
        proto_flags = " ".join(self._tag_protoflags.V())
        # add protobuf include set from PROTO_LIBRARY
        cvs_dirs = " ".join(map(lambda x: "-I=%s " % x, self._tag_include.V()))
        # add cvs path of directory of BROC
        cvs_dirs += "-I=%s " % self.env.BrocCVSDir()
        protoc = os.path.join(os.environ['HOME'], "broc/protobuf/bin/protoc")
        for _dir in proto_dirs:
            # cvs_out_dir = os.path.normpath(os.path.join('broc_out', _dir))
            cvs_out_dir = os.path.normpath(os.path.join('broc_out', self.env.BrocCVSDir()))
            cmd = "mkdir -p %(cvs_out_dir)s && %(protoc)s --cpp_out=%(cvs_out_dir)s %(proto_flags)s %(cvs_dirs)s \
-I=. %(_dir)s/*.proto" % (locals())
            # 执行protoc的目录，在output下
            self._proto_cmds.add(cmd)

        # run protoc
        for cmd in self._proto_cmds:
            Log.Log().LevPrint("MSG", "%s" % cmd)
            ret, msg = Function.RunCommand(cmd, True)
            if ret != 0:
                return (False, "%s%s" % (cmd, msg))
 
        return (True, '')
