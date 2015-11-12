#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
test case for Builder
"""

import os
import sys
import unittest

broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)
from dependency import Builder
from util import Function

class TestBuilder(unittest.TestCase):
    """
    unit test for Builder
    """
    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    def test_BinBuilder(self):
        """
        test BinBuilder
        """
        obj = 'broc_out/a/b/c/test'
        dep_objs = ['a/b/c/fun.o', 'a/b/c/util.o']
        dep_libs = ['broc_out/a/b/d/output/lib/libfun.a', 'broc_out/a/b/d/output/lib/libutil.a']
        dep_links = ['-DBROC', '-Werror', '-Wpublick=private']
        compiler = '/usr/bin/g++'
        right_cmd = "mkdir -p broc_out/a/b/c && /usr/bin/g++ \\\n\t-DBROC \\\n\t-o \
\\\n\tbroc_out/a/b/c/test \\\n\ta/b/c/fun.o \\\n\ta/b/c/util.o \\\n\t-DBROC \\\n\t-Werror \
\\\n\t-Wpublick=private \\\n\t-Xlinker \\\n\t\"-(\" \\\n\t\tbroc_out/a/b/d/output/lib/libfun.a \
\\\n\t\tbroc_out/a/b/d/output/lib/libutil.a \\\n\t-Xlinker \\\n\t\"-)\""
        builder = Builder.BinBuilder(obj, dep_objs, dep_libs, dep_links, compiler, '.')          
        self.assertEqual(right_cmd, builder.GetBuildCmd()) 

    def test_LibBiilder(self):
        """
        test LibBuilder
        """
        obj = 'broc_out/a/b/c/test'
        dep_objs = ['a/b/c/fun.o', 'a/b/c/util.o']
        dep_libs = ['broc_out/a/b/d/output/lib/libfun.a', 'broc_out/a/b/d/output/lib/libutil.a']
        compiler = 'ar'
        right_cmd = "mkdir -p broc_out/a/b/c && ar \\\n\trcs \\\n\tbroc_out/a/b/c/test \
\\\n\ta/b/c/fun.o \\\n\ta/b/c/util.o \\\n\tbroc_out/a/b/d/output/lib/libfun.a \
\\\n\tbroc_out/a/b/d/output/lib/libutil.a"
        builder = Builder.LibBuilder(obj, dep_objs, dep_libs, compiler, '.')          

        self.assertEqual(right_cmd, builder.GetBuildCmd()) 
    def test_ObjBuilder(self):
        """
        test ObjBuilder
        """
        now_dir = os.getcwd()
        obj = "broc_out/a/b/c/test.o"
        infile = 'a/b/c/test.cpp'
        includes = ['/usr/include', '/usr/local/include', 'a/b/c']
        opts = ['-DBROC', '-DVERSION=1.0.0']
        compiler = '/usr/bin/g++'
        builder = Builder.ObjBuilder(obj, infile, includes, opts, compiler, now_dir)
        right_cmd = "mkdir -p broc_out/a/b/c && /usr/bin/g++ \\\n\t-c \
\\\n\t-DBROC \\\n\t-DVERSION=1.0.0 \\\n\t-I. \\\n\t-I/usr/include \\\n\t-I/usr/local/include \
\\\n\t-Ia/b/c \\\n\t-o \\\n\tbroc_out/a/b/c/test.o \\\n\ta/b/c/test.cpp"
        self.assertEqual(right_cmd, builder.GetBuildCmd())
        builder.CalcHeaderFiles()

    def test_GetHeaderFiles(self):
        """
        test GetHeaderFiles
        """
        now_dir = os.getcwd()
        obj = 'get_header_files.o'
        infile = 'get_header_files.cpp'
        include = ['/usr/include', '/usr/local/include']
        compiler = '/usr/bin/g++'
        builder = Builder.ObjBuilder(obj, infile, include, None, compiler, now_dir)
        right_header_cmd = "/usr/bin/g++ \\\n\t-MM \\\n\t-I. \\\n\t-I/usr/include \
\\\n\t-I/usr/local/include \\\n\tget_header_files.cpp"
        self.assertEqual(right_header_cmd, builder.GetHeaderCmd())
        with open('hello.h', 'wb') as f:
            f.write("#include <stdio.h>\n\
void hello()\n\
{\n\
    print(\"hello - hello\");\n\
}\n")
        with open('world.h', 'wb') as f:
            f.write("#include <stdio.h>\n\
void world()\n\
{\n\
    print(\"hello - world\");\n\
}\n")
        with open('get_header_files.cpp', 'wb') as f:
            f.write("#include <stdio.h>\n\
#include <pthread.h>\n\
#include \"hello.h\"\n\
#include \"world.h\"\n\
int main()\n\
{\n\
    hello();\n\
    world();\n\
    return 0;\n\
}\n")
        ret = builder.CalcHeaderFiles()
        self.assertEqual(True, ret['ret'])
        self.assertEqual(sorted(["hello.h", 'world.h']), sorted(builder.GetHeaderFiles()))

        Function.DelFiles('get_header_files.cpp')
        Function.DelFiles('hello.h')
        Function.DelFiles('world.h')
        

if __name__ == "__main__":
    unittest.main()
