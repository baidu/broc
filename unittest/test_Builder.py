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
        builder = Builder.BinBuilder(obj, dep_objs, dep_libs, dep_links, compiler)          
        print('\n%s' % builder.GetBuildCmd()) 

    def test_LibBiilder(self):
        """
        test LibBuilder
        """
        obj = 'broc_out/a/b/c/test'
        dep_objs = ['a/b/c/fun.o', 'a/b/c/util.o']
        dep_libs = ['broc_out/a/b/d/output/lib/libfun.a', 'broc_out/a/b/d/output/lib/libutil.a']
        compiler = '/usr/bin/g++'
        builder = Builder.LibBuilder(obj, dep_objs, dep_libs, compiler)          
        print('\n%s' % builder.GetBuildCmd()) 

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
        print('\n%s' % builder.GetBuildCmd()) 
        builder.CalcHeaderFiles()

    def test_GetHeaderFiles(self):
        """
        test GetHeaderFiles
        """
        now_dir = os.getcwd()
        obj = 'get_header_files.o'
        infile = 'get_header_files.cpp'
        compiler = '/usr/bin/g++'
        builder = Builder.ObjBuilder(obj, infile, None, None, compiler, now_dir)
        with open('get_header_files.cpp', 'wb') as f:
            f.write("#include <stdio.h>\n\
#include <pthread.h>\n\
int main()\n\
{\n\
    print(\"hello world\");\n\
    return 0;\n\
}\n")
        print(builder.GetHeaderCmd())
        ret = builder.CalcHeaderFiles()
        if not ret['ret']:
            print('get header failed(%s)' % ret['msg'])
        else:
            print(builder.GetHeaderFiles())

        Function.DelFiles('get_header_files.cpp')
        

if __name__ == "__main__":
    unittest.main()
