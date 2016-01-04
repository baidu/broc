#!/usr/bin/env python
# -*- coding: utf-8 -*-  

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
splice complie command for all kind of target file
Authors: zhousongsong(doublesongsong@gmail.com)
Date:    2015-09-23 13:33:49
"""
import os
import sys
broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)
from util import Function

class Builder(object):
    """
    base class for splicing the compile command
    """
    def __init__(self, obj, compiler, workspace):
        """
        init function
        Args:
            obj : the cvs path of object file
            compiler : the path of compiler
            workspace : the workspace path
        """
        self.obj = obj
        self.obj_dir = os.path.dirname(obj)
        self.compiler = compiler
        self.workspace = workspace
        self.build_cmd = None      # build cmd
        self.error = "OK"

    def __str__(self):
        """
        """
        return self.build_cmd
    
    def GetBuildCmd(self):
        """
        return the build cmd
        """
        return self.build_cmd

    def Error(self):
        """
        return the error message
        """
        return self.error


class ObjBuilder(Builder):
    """
    object file(.o) builder
    """
    def __init__(self, obj, infile, includes, opts, compiler, workspace):
        """
        Args:
            obj : the cvs path of .o file 
            infile : the cvs path of source file
            includes : a list including multiple head file search paths
            opts : a list of compile options
            compiler : the abs path of compiler
            workspace : the abs path of workspace
        """ 
        Builder.__init__(self, obj, compiler, workspace)
        self.workspace = workspace
        self._includes = ""
        self._opts = None
        self._infile = infile
        self._header_cmd = None
        self._header_files = set()
        if includes:
            self._includes += "\t".join(map(lambda x: "-I%s \\\n" % x, includes))
        if opts: 
            self._opts = " \\\n\t".join(map(lambda x: x, opts))

        self.build_cmd = "mkdir -p %s && %s \\\n\t-c \\\n\t%s \\\n\t%s\t-o \\\n\t%s \\\n\t%s" % \
                         (self.obj_dir, self.compiler, self._opts, self._includes, self.obj, infile)

        self._header_cmd = "%s \\\n\t-MM \\\n\t%s\t%s" % \
                            (self.compiler, self._includes, self._infile)

    def CalcHeaderFiles(self):
        """
        calculate the header files that source file dependends
        Returns:
            { ret : True | False, msg : 'error message' }
            calculate successfully ret is True; otherwise ret is False and msg contains error message
        """
        result = dict()
        result['ret'] = False
        result['msg'] = ''
        retcode, msg = Function.RunCommand(self._header_cmd, ignore_stderr_when_ok=True)
        if retcode != 0:
            result['msg'] = '%s:%s' % (msg, self._header_cmd)
            return result

        files = msg.split()
        for f in files:
            if f.endswith(".h"):
                if self.workspace in f:
                    self._header_files.add(f[len(self.workspace)+1:])
                else:
                    self._header_files.add(f)
        result['ret'] = True
        return result

    def GetHeaderCmd(self):
        """
        return cmd for caculating header files
        """
        return self._header_cmd

    def GetHeaderFiles(self):
        """
        return the header files
        Returns:
            return a list containing header files
        """
        return self._header_files


class LibBuilder(Builder):
    """
    static library builder
    """
    def __init__(self, obj, dep_objs, dep_libs, compiler, workspace):
        """
        Args:
            obj : the cvs path of .a file
            dep_objs : the list of cvs path of object files .o
            dep_libs : the list of cvs path of static library files .a
            compiler : the abs path of compiler
        """
        Builder.__init__(self, obj, compiler, workspace)
        self.build_cmd = "mkdir -p %s && %s \\\n\trcs \\\n\t%s" \
                         % (self.obj_dir, self.compiler, self.obj)
        if dep_objs:
            self.build_cmd += " \\\n\t" + " \\\n\t".join(sorted(dep_objs))
        if dep_libs:
            self.build_cmd += " \\\n\t" + " \\\n\t".join(sorted(dep_libs))

class BinBuilder(Builder):
    """
    exe file builder
    """
    def __init__(self, obj, dep_objs, dep_libs, dep_links, compiler, workspace):
        """
        Args:
            obj : the cvs path of .a file
            dep_objs : the list of cvs path of object files .o
            dep_libs : the list of cvs path of static library files .a
            dep_links : the list of link options
            compiler : the abs path of compiler
        """
        Builder.__init__(self, obj, compiler, workspace)
        # mkdir -p broc_out/et/tools/app/output/bin && g++ -DBROC -o broc_out/et/tools/app/output/bin/hello broc_out/et/tools/app/2_hello_hello.o -Xlinker "-(" broc_out/et/tools/app/output/lib/libperson.a /home/zss/zeus/protobuf/lib/libprotobuf.a  -Xlinker "-)"
        self.build_cmd = "mkdir -p %s && %s \\\n\t-DBROC \\\n\t-o \\\n\t%s \\\n\t" \
                         % (self.obj_dir, self.compiler, self.obj)
        if dep_objs:
            self.build_cmd += " \\\n\t".join(map(lambda x: x.strip(), sorted(dep_objs)))
        if dep_links:
            self.build_cmd += " \\\n\t"
            self.build_cmd += " \\\n\t".join(map(lambda x: x.strip(), sorted(dep_links)))
        if dep_libs:
            self.build_cmd += " \\\n\t-Xlinker \\\n\t\"-(\" \\\n\t\t"
            self.build_cmd += " \\\n\t\t".join(map(lambda x: x.strip(), sorted(dep_libs)))
            self.build_cmd += " \\\n\t-Xlinker \\\n\t\"-)\""
        #TODO Add WholeArchive 
