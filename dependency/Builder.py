#!/usr/bin/env python
# -*- coding: utf-8 -*-  

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
splice complie command for all kind of target file
Authors: zhousongsong(zhousongsong@baidu.com)
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
            #self._includes = "\t" + "\n\t".join(map(lambda x: "-I%s \ " % x, includes))
            self._includes = " ".join(map(lambda x: "-I%s" % x, includes))
        if opts: 
            #self._opts = "\t" + "\n\t".join(map(lambda x: "%s \\" % x, opts))
            self._opts = " ".join(map(lambda x: x, opts))
        if self._includes:
            #self.build_cmd = "mkdir -p %s && %s \\\n\t-c \\\n%s\n%s\n\t-o \\\n\t%s \\\n\t%s\n" % \
            #        (self.obj_dir, self.compiler, self._opts, self._includes, self.obj, infile)
            self.build_cmd = "mkdir -p %s && %s -c %s %s -o %s %s" % \
                    (self.obj_dir, self.compiler, self._opts, self._includes, self.obj, infile)
        else:
            #self.build_cmd = "mkdir -p %s && %s \\\n\t-c \\\n%s\n\t-o \\\n\t%s \\\n\t%s\n" % \
            #        (self.obj_dir, self.compiler, self._opts, self.obj, infile)
            self.build_cmd = "mkdir -p %s && %s -c %s -o %s %s" % \
                    (self.obj_dir, self.compiler, self._opts, self.obj, infile)
        include_paths = ""
        if self._includes:
            include_paths = self._includes[:-1]
        self._header_cmd = "%s \\\n\t-MM \\\n\t%s\n %s" % \
                            (self.compiler, self._infile, include_paths)

    def CalcHeaderFiles(self):
        """
        calculate the header files that source file dependends
        Returns:
            {ret : True | False, msg : 'error message' }
            calculate successfully ret is True; otherwise ret is False and msg contains failed reason   
        """
        result = dict()
        result['ret'] = False
        result['msg'] = ''
        retcode, msg = Function.RunCommand(self._header_cmd, ignore_stderr_when_ok=True)
        if retcode != 0:
            result['msg'] = '%s:%s' % (msg, self._header_cmd)
            return result

        files = msg.split()
        # file[0] : .o, file[1] : .cpp|.c
        #for f in files[2:]:
        #    if f and f not in ['\\\n', '\\', self._infile, files[:2]]:
        for f in files:
            if f.endswith(".h"):
                if self.workspace in f:
                    self._header_files.add(f[len(self.workspace):])
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
        libs = ""
        objs = ""
        if dep_objs:
            #objs = "\n\t" + "\n\t".join(map(lambda x: "%s/%s" % (self.workspace, x.strip()) + " \ ", sorted(dep_objs)))
            objs = " ".join(sorted(dep_objs))
        if dep_libs:
            #libs = "\n\t" + "\n\t".join(map(lambda x: "%s/%s" % (self.workspace, x.strip()) + " \ ", sorted(dep_libs)))
            libs = " ".join(sorted(dep_libs))
        #self.build_cmd = "mkdir -p %s && %s \\\n\trcs \\\n\t%s \\%s%s\n" % \
        #                 (self.obj_dir, self.compiler, self.obj, objs[:-2], libs[:-2])
        self.build_cmd = "mkdir -p %s && %s rcs %s %s %s" \
                         % (self.obj_dir, self.compiler, self.obj, objs, libs)

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
        objs = ""
        links = ""
        libs = ""
        # mkdir -p broc_out/et/tools/app/output/bin && g++ -DBROC -o broc_out/et/tools/app/output/bin/hello broc_out/et/tools/app/2_hello_hello.o -Xlinker "-(" broc_out/et/tools/app/output/lib/libperson.a /home/zss/zeus/protobuf/lib/libprotobuf.a  -Xlinker "-)"
        self.build_cmd = "mkdir -p %s && %s -DBROC -o %s" % (self.obj_dir, self.compiler, self.obj)
        if dep_objs:
            objs = " ".join(map(lambda x: x.strip(), sorted(dep_objs)))
            self.build_cmd += " %s" % objs 
        if dep_links:
            links = " ".join(map(lambda x: x.strip(), sorted(dep_links)))
            self.build_cmd += " %s" % links
        if dep_libs:
            self.build_cmd += " -Xlinker \"-(\" "
            libs = "" + " ".join(map(lambda x: x.strip(), sorted(dep_libs)))
            self.build_cmd += libs
            self.build_cmd += " -Xlinker \"-)\""
        # print(self.build_cmd)
        #TODO Add WholeArchive 
