#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
    test case for Syntax
    Authors: liruihao(liruihao01@gmail.com)
    Date:   2015/11/11 16:24:42
"""
import os
import sys
import tempfile
import unittest

broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)

from dependency import Syntax
from dependency import Target
from dependency import Source
from dependency import SyntaxTag
from dependency import Environment
from util import Function
from dependency import BrocModule_pb2 
from dependency import BrocTree
from util import Log

class TestSyntax(unittest.TestCase):
    """
    unit test for Syntax
    """
    def setUp(self):
        """
        init
        """
        sys.argv = ['NOT PLANISH']
        module = BrocModule_pb2.Module()
        module.name = 'broc'
        module.module_cvspath = 'baidu/broc'
        module.broc_cvspath = 'baidu/broc/BROC'
        module.is_main = True
        module.repo_kind = BrocModule_pb2.Module.GIT
        module.revision = "1234"
        module.last_changed_rev = "1236"
        module.dep_level = 0
        #get home dir
        home = os.environ['HOME']
        module.workspace = '%s/unittest_broc/workspace' % home
        module.root_path = '%s/unittest_broc/workspace/baidu/broc' % home
        module.url = 'https://github.com/baidu/broc'
        module.br_kind = BrocModule_pb2.Module.BRANCH
        module.br_name = 'trunk'
        #module.commit_id = '5d9819900c2781873aa0ffce285d5d3e75b072a8'
        self._module = module
        Function.RunCommand("mkdir -p %s" % module.root_path, ignore_stderr_when_ok = True)
        Function.RunCommand("touch %s/hello.cpp" % module.root_path, ignore_stderr_when_ok = True)
        Function.RunCommand("touch %s/hello.h" % module.root_path, ignore_stderr_when_ok = True)
        self._env = Environment.Environment(module)
        Environment.SetCurrent(self._env)

    def tearDown(self):
        """
        teardown
        """
        Function.RunCommand("rm -rf ~/unittest_broc", ignore_stderr_when_ok = True)

    def test_COMPILER_PATH(self):
        """
        test Syntax.COMPILER_PATH
        """
        Syntax.COMPILER_PATH('/usr/bin/')
        self.assertEqual('/usr/bin/', self._env.CompilerDir())

    def test_CPPFLAGS(self):
        """
        test Syntax.CPPFLAGS
        """
        #test case of debug mode
        self._env._build_mode = 'debug'
        Syntax.CPPFLAGS("-g -Wall", "-g -O2")
        self.assertTrue("-g -Wall" in self._env._g_cppflags.V() \
                and "-g -O2" not in self._env._g_cppflags.V())

        #test case of muti CPPFLAGS
        Syntax.CPPFLAGS("-W -Wshadow", "-g -O2")
        Syntax.CPPFLAGS("-finline-functions", "-g -O2")
        self.assertTrue("-g -Wall" in self._env._g_cppflags.V() \
                and "-g -O2" not in self._env._g_cppflags.V())
        self.assertTrue("-W -Wshadow" in self._env._g_cppflags.V() \
                and "-g -O2" not in self._env._g_cppflags.V())
        self.assertTrue("-finline-functions" in self._env._g_cppflags.V() \
                and "-g -O2" not in self._env._g_cppflags.V())

        #reset g_cppflags
        self._env._g_cppflags = SyntaxTag.TagCPPFLAGS()

        #test case of release mode
        self._env._build_mode = 'release'
        Syntax.CPPFLAGS("-g -Wall", "-g -O2")
        self.assertTrue("-g -O2" in self._env._g_cppflags.V() \
                and "-g -Wall" not in self._env._g_cppflags.V())

    def test_CppFlags(self):
        """
        test Syntax.CppFlags
        """
        #test case of debug mode
        self._env._build_mode = 'debug'
        tag = Syntax.CppFlags("-g -Wall", "-g -O2")
        self.assertTrue("-g -Wall" in tag._v and "-g -O2" not in tag.V())
        
        #test case of release mode
        self._env._build_mode = 'release'
        tag2 = Syntax.CppFlags("-g -Wall", "-g -O2")
        self.assertTrue("-g -O2" in tag2.V() and "-g -Wall" not in tag2.V())

    def test_CFLAGS(self):
        """
        test Syntax.CFLAGS
        """ 
        #test case of debug mode
        self._env._build_mode = 'debug'
        Syntax.CFLAGS("-g -Wall", "-g -O2")
        self.assertTrue("-g -Wall" in self._env._g_cflags.V() \
                and "-g -O2" not in self._env._g_cflags.V())
        
        #test case of muti CPPFLAGS
        Syntax.CFLAGS("-W -Wshadow", "-g -O2")
        Syntax.CFLAGS("-finline-functions", "-g -O2")
        self.assertTrue("-g -Wall" in self._env._g_cflags.V() \
                and "-g -O2" not in self._env._g_cflags.V())
        self.assertTrue("-W -Wshadow" in self._env._g_cflags.V() \
                and "-g -O2" not in self._env._g_cflags.V())
        self.assertTrue("-finline-functions" in self._env._g_cflags.V() \
                and "-g -O2" not in self._env._g_cflags.V())

        #reset g_cflags
        self._env._g_cflags = SyntaxTag.TagCFLAGS()

        #test case of release mode
        self._env._build_mode = 'release'
        Syntax.CFLAGS("-g -Wall", "-g -O2")
        self.assertTrue("-g -O2" in self._env._g_cflags.V() \
                and "-g -Wall" not in self._env._g_cflags.V())

    def test_CFlags(self):
        """
        test Syntax.CFlags
        """
        #test case of debug mode
        Environment.SetCurrent(self._env)
        self._env._build_mode = 'debug'
        tag = Syntax.CFlags("-g -Wall", "-g -O2")
        self.assertTrue("-g -Wall" in tag._v and "-g -O2" not in tag.V())
        
        #test case of release mode
        self._env._build_mode = 'release'
        self._env._build_mode = 'release'
        tag2 = Syntax.CFlags("-g -Wall", "-g -O2")
        self.assertTrue("-g -O2" in tag2.V() and "-g -Wall" not in tag2.V())

    def test_CXXFLAGS(self):
        """
        test Syntax.CXXFLAGS
        """
        #test case of debug mode
        Environment.SetCurrent(self._env)
        self._env._build_mode = 'debug'
        Syntax.CXXFLAGS("-g -Wall", "-g -O2")
        self.assertTrue("-g -Wall" in self._env._g_cxxflags.V() \
                and "-g -O2" not in self._env._g_cxxflags.V())
        
        #test case of muti CPPFLAGS
        Syntax.CXXFLAGS("-W -Wshadow", "-g -O2")
        Syntax.CXXFLAGS("-finline-functions", "-g -O2")
        self.assertTrue("-g -Wall" in self._env._g_cxxflags.V() \
                and "-g -O2" not in self._env._g_cxxflags.V())
        self.assertTrue("-W -Wshadow" in self._env._g_cxxflags.V() \
                and "-g -O2" not in self._env._g_cxxflags.V())
        self.assertTrue("-finline-functions" in self._env._g_cxxflags.V() \
                and "-g -O2" not in self._env._g_cxxflags.V())

        #reset g_cxxflags
        self._env._g_cxxflags = SyntaxTag.TagCXXFLAGS()

        #test case of release mode
        self._env._build_mode = 'release'
        Syntax.CXXFLAGS("-g -Wall", "-g -O2")
        self.assertTrue("-g -O2" in self._env._g_cxxflags.V() \
                and "-g -Wall" not in self._env._g_cxxflags.V())

    def test_CxxFlags(self):
        """
        test Syntax.CxxFlags
        """
        #test case of debug mode
        Environment.SetCurrent(self._env)
        self._env._build_mode = 'debug'
        tag = Syntax.CxxFlags("-g -Wall", "-g -O2")
        self.assertTrue("-g -Wall" in tag._v and "-g -O2" not in tag.V())

        #test case of release mode
        self._env._build_mode = 'release'
        tag2 = Syntax.CxxFlags("-g -Wall", "-g -O2")
        self.assertTrue("-g -O2" in tag2.V() and "-g -Wall" not in tag2.V())

    def test_CONVERT_OUT(self):
        """
        test Syntax.CONVERT_OUT
        """
        self.assertEqual("broc_out/baidu/broc/hello.h", Syntax.CONVERT_OUT("./hello.h"))
        #test CONVERT_OUT can raise Syntax.NotInSelfModuleError or not
        flag = False
        try:
            Syntax.CONVERT_OUT("../hello.h")
        except Syntax.NotInSelfModuleError as er:
            flag = True
        self.assertTrue(flag)

    def test_INCLUDE(self):
        """
        test Syntax.INCLUDE
        """
        Environment.SetCurrent(self._env)
        # arg starts with $WORKSPACE
        Syntax.INCLUDE("$WORKSPACE/baidu/broc")
        self.assertTrue("baidu/broc" in self._env.IncludePaths().V())
        self.assertTrue("baidu/agile" not in self._env.IncludePaths().V())
        
        # arg starts with broc_out
        Syntax.INCLUDE("broc_out/baidu/broc")
        self.assertTrue("broc_out/baidu/broc" in self._env.IncludePaths().V())
        self.assertTrue("broc_out/baidu/agile" not in self._env.IncludePaths().V())

        # arg is abs path
        Syntax.INCLUDE("/opt/include")
        self.assertTrue("/opt/include" in self._env.IncludePaths().V())
        self.assertTrue("/home/include" not in self._env.IncludePaths().V())

        # arg in self module
        Syntax.INCLUDE("./include")
        incpath = os.path.normpath(os.path.join(self._module.workspace, \
                self._module.module_cvspath, "include"))
        self.assertTrue(incpath in self._env.IncludePaths().V())

    def test_Include(self):
        """
        test Syntax.Include
        """
        Environment.SetCurrent(self._env)
        # arg starts with $WORKSPACE
        tag = Syntax.Include("$WORKSPACE/baidu/broc")
        self.assertTrue("baidu/broc" in tag.V())
        self.assertTrue("baidu/agile" not in tag.V())
        
        # arg starts with broc_out
        tag = Syntax.Include("broc_out/baidu/broc")
        self.assertTrue("broc_out/baidu/broc" in tag.V())
        self.assertTrue("broc_out/baidu/agile" not in tag.V())
        
        # arg is abs path
        tag = Syntax.Include("/opt/include")
        self.assertTrue("/opt/include" in tag.V())
        self.assertTrue("/home/include" not in tag.V())

        # arg in self module
        tag = Syntax.Include("./include")
#incpath = os.path.normpath(os.path.join(self._module.workspace, \
#                self._module.module_cvspath, "include"))
        incpath=os.path.join(self._module.module_cvspath, 'include')
        self.assertTrue(incpath in tag.V())

    def test_Libs(self):
        """
        test Syntax.Libs
        """
        #one lib in arg
        tag = Syntax.Libs("$OUT_ROOT/baidu/broc/lib/libbroc.a")
        self.assertTrue("broc_out/baidu/broc/lib/libbroc.a" in tag.V())

        #more than one libs in args
        flag = True
        tag = Syntax.Libs("$OUT_ROOT/baidu/broc/lib/libbroc.a", \
                "$OUT_ROOT/protobuf/lib/libprotobuf.a", \
                "$OUT_ROOT/ccode/lib/libccode.a" \
                "$OUT_ROOT/dict/lib/libdict.a")
        lib_list = ["broc_out/baidu/broc/lib/libbroc.a", \
                "broc_out/protobuf/lib/libprotobuf.a", \
                "broc_out/ccode/lib/libccode.a" \
                "broc_out/dict/lib/libdict.a"]
        for lib in lib_list:
            if lib not in tag.V():
                flag = False

        self.assertTrue(flag)

        #arg not start with $OUT_ROOT
        flag = False
        try:
            tag = Syntax.Libs("baidu/broc/lib/libbroc.a")
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

    def test_LDFLAGS(self):
        """
        test Syntax.LDFLAGS
        """
        #test case of debug mode
        Environment.SetCurrent(self._env)
        self._env._build_mode = 'debug'
        Syntax.LDFLAGS("-lpthread -lcrypto", "-lprotobuf -lpthread")
        self.assertTrue("-lpthread -lcrypto" in self._env._g_linkflags.V() \
                and "-lprotobuf -lpthread" not in self._env._g_linkflags.V())

        #reset g_linkflags
        self._env._g_linkflags = SyntaxTag.TagCPPFLAGS()

        #test case of release mode
        self._env._build_mode = 'release'
        Syntax.LDFLAGS("-lpthread -lcrypto", "-lprotobuf -lpthread")
        self.assertTrue("-lprotobuf -lpthread" in self._env._g_linkflags.V() \
                and "-lpthread -lcrypto" not in self._env._g_linkflags.V())

    def test_LDFlags(self):
        """
        test Syntax.LDFlags
        """
        #test case of debug mode
        Environment.SetCurrent(self._env)
        self._env._build_mode = 'debug'
        tag = Syntax.LDFlags("-lpthread -lcrypto", "-lprotobuf -lpthread")
        self.assertTrue("-lpthread -lcrypto" in tag.V() \
                and "-lprotobuf -lpthread" not in tag.V())

        #reset g_linkflags
        self._env._g_linkflags = SyntaxTag.TagLDFLAGS()

        #test case of release mode
        self._env._build_mode = 'release'
        tag = Syntax.LDFlags("-lpthread -lcrypto", "-lprotobuf -lpthread")
        self.assertTrue("-lprotobuf -lpthread" in tag.V() \
                and "-lpthread -lcrypto" not in tag.V())

    def test_GLOB(self):
        """
        test Syntax.GLOB
        """
        #test case of one file
        files = Syntax.GLOB("./*.cpp")
        self.assertEqual(files, "hello.cpp")

        #test case of more files and those files must in the lexicographical order
        module = self._module
        Function.RunCommand("touch %s/hello1.h" % module.root_path, ignore_stderr_when_ok = True)
        Function.RunCommand("touch %s/hello2.h" % module.root_path, ignore_stderr_when_ok = True)
        Function.RunCommand("touch %s/hello3.h" % module.root_path, ignore_stderr_when_ok = True)
        Function.RunCommand("touch %s/hello10.h" % module.root_path, ignore_stderr_when_ok = True)
        files = Syntax.GLOB("./*.h")
        self.assertEqual(files, "hello.h hello1.h hello10.h hello2.h hello3.h")

        #test case of files not in self module
        Function.RunCommand("touch %s/../README" % module.root_path, ignore_stderr_when_ok = True)
        flag = False
        try:
            Syntax.GLOB("../README")
        except Syntax.NotInSelfModuleError as e:
            flag = True
        self.assertTrue(flag)

        #test case of no such files
        flag = False
        try:
            Syntax.GLOB("./just_test.cpp")
        except Syntax.BrocArgumentIllegalError as e:
            flag = True
        self.assertTrue(flag)

    def test_ParseNameAndArgs(self):
        """
        test Syntax._ParseNameAndArgs
        """
        #only has name
        files, args = Syntax._ParseNameAndArgs("broc")
        self.assertEqual(files, ["broc"])
        self.assertEqual(args, [])

        #more args
        inctag = Syntax.Include("./ ./include")
        cpptag = Syntax.CppFlags("-DDEBUG", "-DBROC")
        ctag = Syntax.CFlags("-O2", "-O0")
        cxxtag = Syntax.CxxFlags("-Werror", "-Wall")
        files, args = Syntax._ParseNameAndArgs("./*.cpp", inctag)
        self.assertEqual(files, ["./*.cpp"])
        self.assertEqual(args, [inctag])
        files, args = Syntax._ParseNameAndArgs("./*.cpp", inctag, cpptag)
        self.assertEqual(files, ["./*.cpp"])
        self.assertEqual(args, [inctag, cpptag])
        files, args = Syntax._ParseNameAndArgs("./*.cpp", cpptag, ctag)
        self.assertEqual(files, ["./*.cpp"])
        self.assertEqual(args, [cpptag, ctag])
        files, args = Syntax._ParseNameAndArgs("./*.cpp", "./*.c", cxxtag, ctag)
        self.assertEqual(files, ["./*.cpp", "./*.c"])
        self.assertEqual(args, [cxxtag, ctag])
        files, args = Syntax._ParseNameAndArgs("./*.cpp", "./*.c", inctag, cpptag, cxxtag, ctag)
        self.assertEqual(files, ["./*.cpp", "./*.c"])
        self.assertEqual(args, [inctag, cpptag, cxxtag, ctag])

    def test_Sources(self):
        """
        test Syntax.Sources
        """
        #get local flags tag
        cpptags = Syntax.CppFlags("-DDEBUG_LOCAL", "-DRELEASE_LOCAL")
        cxxtags = Syntax.CxxFlags("-Wwrite-strings", "-Wswitch")
        ctags = Syntax.CFlags("-Wwrite-strings", "-Wswitch")
        incflags = Syntax.Include("$WORKSPACE/baidu/bcloud")
        
        tag = Syntax.Sources("hello.cpp", cpptags, cxxtags, ctags, incflags)
        
        src = tag.V()[0]
        Source.Source.Action(src)
        self.assertEqual(src.cppflags, ["-DDEBUG_LOCAL"])
        self.assertEqual(src.cxxflags, ["-Wwrite-strings"])
        self.assertEqual(src.cflags, ["-Wwrite-strings"])
        self.assertEqual(src.includes, [".", "broc_out", "baidu/bcloud"])
        self.assertEqual(src.infile, "baidu/broc/hello.cpp")
 

    def test_CreateSources(self):
        """
        test Syntax._CreateSource
        """
        #init env global flags
        self._env._g_cppflags = SyntaxTag.TagCPPFLAGS()
        self._env._g_cflags = SyntaxTag.TagCFLAGS()
        self._env._g_cxxflags = SyntaxTag.TagCXXFLAGS()
        self._env._g_incflags = SyntaxTag.TagINCLUDE()
        self._env._g_incflags.AddV('. broc_out')
        self._env._build_mode = 'debug'

        #set local flags tag
        cpptags = Syntax.CppFlags("-DDEBUG_LOCAL", "-DRELEASE_LOCAL")
        cxxtags = Syntax.CxxFlags("-Wwrite-strings", "-Wswitch")
        ctags = Syntax.CFlags("-Wwrite-strings", "-Wswitch")
        incflag = Syntax.Include("$WORKSPACE/baidu/bcloud")

        #no flags
        src = Syntax._CreateSources("baidu/broc/hello.cpp", [])
        Source.Source.Action(src)
        self.assertEqual(src.cppflags, [])
        self.assertEqual(src.cxxflags, [])
        self.assertEqual(src.cflags, [])
        self.assertEqual(src.includes, [".", "broc_out"])
        self.assertEqual(src.infile, "baidu/broc/hello.cpp")

        #only local flags
        src = Syntax._CreateSources("baidu/broc/hello.cpp", \
                [cpptags, cxxtags, ctags, incflag])
        Source.Source.Action(src)
        self.assertEqual(src.cppflags, ["-DDEBUG_LOCAL"])
        self.assertEqual(src.cxxflags, ["-Wwrite-strings"])
        self.assertEqual(src.cflags, ["-Wwrite-strings"])
        self.assertEqual(src.includes, [".", "broc_out", "baidu/bcloud"])
        
        #only global flags
        Syntax.CFLAGS("-Werror -O2", "-W")
        Syntax.CXXFLAGS("-Werror -O2", "-W")
        Syntax.CPPFLAGS("-DDEBUG", "-DRELEASE")
        Syntax.INCLUDE("$WORKSPACE/baidu/broc")
        src = Syntax._CreateSources("baidu/broc/hello.cpp", [])
        Source.Source.Action(src)
        self.assertEqual(src.cppflags, ["-DDEBUG"])
        self.assertEqual(src.cxxflags, ["-Werror -O2"])
        self.assertEqual(src.cflags, ["-Werror -O2"])
        self.assertEqual(src.includes, [".", "broc_out", "baidu/broc"])
        self.assertEqual(src.infile, "baidu/broc/hello.cpp")

        #more value of global flags
        Syntax.CFLAGS("-Wall", "-Wall")
        Syntax.CXXFLAGS("-Wall", "-Wall")
        Syntax.CPPFLAGS("-DBROC", "-DBROC")
        src = Syntax._CreateSources("baidu/broc/hello.cpp", [])
        Source.Source.Action(src)
        self.assertEqual(src.cppflags, ["-DDEBUG", "-DBROC"])
        self.assertEqual(src.cxxflags, ["-Werror -O2", "-Wall"])
        self.assertEqual(src.cflags, ["-Werror -O2", "-Wall"])
        self.assertEqual(src.includes, [".", "broc_out", "baidu/broc"])
        self.assertEqual(src.infile, "baidu/broc/hello.cpp")

        #local flags cover golbal flags
        src = Syntax._CreateSources("baidu/broc/hello.cpp", [cpptags, cxxtags])
        Source.Source.Action(src)
        self.assertEqual(src.cppflags, ["-DDEBUG_LOCAL"])
        self.assertEqual(src.cxxflags, ["-Wwrite-strings"])
        self.assertEqual(src.cflags, ["-Werror -O2", "-Wall"])
        self.assertEqual(src.includes, [".", "broc_out", "baidu/broc"])
        self.assertEqual(src.infile, "baidu/broc/hello.cpp")

    def test_APPLICATION(self):
        """
        test Syntax.APPLICATION
        """
        #set local flags tag
        ldflag = Syntax.LDFlags("-lpthread", "-lcrypto")
        libs = Syntax.Libs("$OUT_ROOT/baidu/broc/libhello.a")
        cpptags = Syntax.CppFlags("-DBROC", "-DRELEASE")

        #set global flags
        Syntax.LDFLAGS("-lmcpack", "-lrt")
        src = Syntax.Sources("hello.cpp")
        
        #an error name of application
        flag = False
        try:
            Syntax.APPLICATION("^*^&*!*$^", src)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #an error args of application
        flag = False
        try:
            Syntax.APPLICATION("hello", src, cpptags)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #global ldflags
        Syntax.APPLICATION("hello", src)
        app = self._env.Targets()[0]
        app.Action()
        self.assertEqual(app.link_options, ["-lmcpack"])
        self.assertEqual(app.tag_libs.V(), [])
        
        #two samename target
        flag = False
        try:
            Syntax.APPLICATION("hello", src)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #local ldflags
        Syntax.APPLICATION("hello2", src, ldflag)
        app = self._env.Targets()[1]
        app.Action()
        self.assertEqual(app.link_options, ["-lpthread"])
        self.assertEqual(app.tag_libs.V(), [])

        #Libs
        Syntax.APPLICATION("hello3", src, ldflag, libs)
        app = self._env.Targets()[2]
        app.Action()
        self.assertEqual(app.link_options, ["-lpthread"])
        self.assertEqual(app.tag_libs.V(), ["broc_out/baidu/broc/libhello.a"])

    def test_STATIC_LIBRARY(self):
        """
        test Syntax.STATIC_LIBRARY
        """
        #set local flags tag
        libs = Syntax.Libs("$OUT_ROOT/baidu/broc/libhello.a")
        cpptags = Syntax.CppFlags("-DBROC", "-DRELEASE")
        src = Syntax.Sources("hello.cpp")
        
        #an error name of application
        flag = False
        try:
            Syntax.STATIC_LIBRARY("^*^&*!*$^", src)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #an error args of application
        flag = False
        try:
            Syntax.STATIC_LIBRARY("hello", src, cpptags)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #Libs
        Syntax.STATIC_LIBRARY("hello", src, libs)
        library = self._env.Targets()[0]
        library.Action()
        self.assertEqual(library.tag_libs.V(), ["broc_out/baidu/broc/libhello.a"])

        #two samename target
        flag = False
        try:
            Syntax.STATIC_LIBRARY("hello", src)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #library DoCopy
        Function.RunCommand("mkdir -p %s/lib" % self._module.root_path, \
                ignore_stderr_when_ok = True)
        Function.RunCommand("touch %s/lib/libhello1.a" % self._module.root_path, \
                ignore_stderr_when_ok = True)
        now_dir = os.getcwd()
        os.chdir(self._module.workspace)
        Syntax.STATIC_LIBRARY("hello1")
        lib_paths = os.path.join(self._module.workspace, "broc_out", \
                self._module.module_cvspath, "output/lib/libhello1.a")
        self.assertTrue(os.path.exists(lib_paths))
        os.chdir(now_dir)

    def test_UT_APPLICATION(self):
        """
        test Syntax.UT_APPLICATION
        """
        #set local flags tag
        ldflag = Syntax.LDFlags("-lpthread", "-lcrypto")
        libs = Syntax.Libs("$OUT_ROOT/baidu/broc/libhello.a")
        cpptags = Syntax.CppFlags("-DBROC", "-DRELEASE")
        utargs = Syntax.UTArgs("--log=a.log --conf=a.conf")

        #set global flags
        Syntax.LDFLAGS("-lmcpack", "-lrt")
        src = Syntax.Sources("hello.cpp")
        
        #an error name of utapplication
        flag = False
        try:
            Syntax.UT_APPLICATION("^*^&*!*$^", src)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #an error args of utapplication
        flag = False
        try:
            Syntax.UT_APPLICATION("hello", src, cpptags)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #global ldflags
        Syntax.UT_APPLICATION("hello", src)
        utapp = self._env.Targets()[0]
        utapp.Action()
        self.assertEqual(utapp.link_options, ["-lmcpack"])
        self.assertEqual(utapp.tag_libs.V(), [])
        self.assertEqual(utapp._ut_args, [])

        #two samename target
        flag = False
        try:
            Syntax.UT_APPLICATION("hello", src)
        except Syntax.BrocArgumentIllegalError as ex:
            flag = True
        self.assertTrue(flag)

        #local ldflags
        Syntax.UT_APPLICATION("hello2", src, ldflag)
        utapp = self._env.Targets()[1]
        utapp.Action()
        self.assertEqual(utapp.link_options, ["-lpthread"])
        self.assertEqual(utapp.tag_libs.V(), [])
        self.assertEqual(utapp._ut_args, [])

        #Libs
        Syntax.UT_APPLICATION("hello3", src, ldflag, libs)
        utapp = self._env.Targets()[2]
        utapp.Action()
        self.assertEqual(utapp.link_options, ["-lpthread"])
        self.assertEqual(utapp.tag_libs.V(), ["broc_out/baidu/broc/libhello.a"])
        self.assertEqual(utapp._ut_args, [])
        
        #UTArgs
        Syntax.UT_APPLICATION("hello4", src, ldflag, libs, utargs)
        utapp = self._env.Targets()[3]
        utapp.Action()
        self.assertEqual(utapp.link_options, ["-lpthread"])
        self.assertEqual(utapp.tag_libs.V(), ["broc_out/baidu/broc/libhello.a"])
        self.assertEqual(utapp._ut_args, ["--log=a.log", "--conf=a.conf"])

    def test_PROTO_LIBRARY(self):
        """
        test Syntax.PROTO_LIBRARY
        """
        #make a new proto file
        Function.RunCommand("touch %s/hello.proto" % self._module.root_path, \
                ignore_stderr_when_ok = True)
        #set local flags
        cpptags = Syntax.CppFlags("-DDEBUG_LOCAL", "-DRELEASE_LOCAL")
        cxxtags = Syntax.CxxFlags("-Wwrite-strings", "-Wswitch")
        incflag = Syntax.Include("")
        libflag = Syntax.Libs("$OUT_ROOT/baidu/broc/output/lib/libhello.a")

        now_dir = os.getcwd()
        os.chdir(self._module.workspace)
        protos = Syntax.PROTO_LIBRARY("hello", "*.proto", cpptags, cxxtags, incflag, libflag)
        proto_library = self._env.Targets()[0]
        src = proto_library.tag_sources.V()[0]
        proto_library.Action()
        os.chdir(now_dir)
        
        #check result
        proto_cmd = """mkdir -p broc_out/baidu/broc && protoc \
--cpp_out=broc_out/baidu/broc  -I=baidu/broc \
-I=. baidu/broc/*.proto\n"""
        self.assertEqual(' '.join(protos.__str__().split()), ' '.join(proto_cmd.split()))
        self.assertEqual(src.cppflags, ["-DDEBUG_LOCAL"])
        self.assertEqual(src.cxxflags, ["-Wwrite-strings"])
        self.assertEqual(src.includes, [".", "broc_out", 'baidu/broc', 
                u'broc_out/baidu/broc'])
        self.assertEqual(src.infile, "broc_out/baidu/broc/hello.pb.cc")
        self.assertEqual(proto_library.tag_libs.V(), \
                ["broc_out/baidu/broc/output/lib/libhello.a"])

    def test_UTArgs(self):
        """
        test Syntax.UTArgs
        """
        tag = Syntax.UTArgs("--conf=a.conf --log=a.log")
        self.assertTrue("--conf=a.conf" in tag.V())
        self.assertTrue("--log=a.log" in tag.V())
        self.assertTrue("--help" not in tag.V())

    def test_PUBLISH(self):
        """
        test Syntax.PUBLISH
        """
        #src has one file
        Syntax.PUBLISH("conf/a.conf", "$OUT/conf")
        dst = os.path.join(self._env.OutputPath(), "conf")
        src = os.path.join(self._module.module_cvspath, "conf/a.conf")
        self.assertTrue("mkdir -p %s && cp -rf %s %s" % (dst, src, dst))
        
        #src has more files
        Syntax.PUBLISH("conf/a1.conf conf/a2.conf", "$OUT/conf")
        dst = os.path.join(self._env.OutputPath(), "conf")
        for s in "conf/a1.conf conf/a2.conf".split(' '):
            src = os.path.join(self._module.module_cvspath, s)
            self.assertTrue("mkdir -p %s && cp -rf %s %s" % (dst, src, dst))

        #out_dir doesn't start with $OUT
        flag = False
        try:
            Syntax.PUBLISH("conf/a3.conf", "conf")
        except Syntax.BrocArgumentIllegalError as e:
            flag = True
        self.assertTrue(flag)

        #src doesn't in self module
        flag = False
        try:
            Syntax.PUBLISH("../../conf/a3.conf", "$OUT/conf")
        except Syntax.NotInSelfModuleError as e:
            flag = True
        self.assertTrue(flag)

    def test_SVN_PATH(self):
        """
        test Syntax.SVN_PATH
        """
        self.assertEqual(self._module.root_path, Syntax.SVN_PATH())

    def test_SVN_URL(self):
        """
        test Syntax.SVN_URL
        """
        self.assertEqual(self._module.url, Syntax.SVN_URL())

    def test_SVN_REVISION(self):
        """
        test Syntax.SVN_REVISION
        """
        self.assertEqual(self._module.revision, Syntax.SVN_REVISION())

    def test_SVN_LAST_CHANGED_REV(self):
        """
        test Syntax.LAST_CHANGED_REV
        """
        self.assertEqual(self._module.last_changed_rev, Syntax.SVN_LAST_CHANGED_REV())

    def test_GIT_PATH(self):
        """
        test Syntax.GIT_PATH
        """
        self.assertEqual(self._module.root_path, Syntax.GIT_PATH())

    def test_GIT_URL(self):
        """
        test Syntax.
        """
        self.assertEqual(self._module.url, Syntax.GIT_URL())

    def test_GIT_BRANCH(self):
        """
        test Syntax.GIT_BRANCH
        """
        self.assertEqual(self._module.br_name, Syntax.GIT_BRANCH())

    def test_GIT_TAG(self):
        """
        test Syntax.GIT_TAG
        """
        self.assertEqual(self._module.tag_name, Syntax.GIT_TAG())

if __name__ == "__main__":
    unittest.main()
