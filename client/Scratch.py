#!/usr/bin/env python
# -*- coding: gbk -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module create a Broc template
Authors: zhousongsong
Date:    2015/09/23 09:44:05
"""
import os
import sys
broc_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
sys.path.insert(0, broc_dir)
from util import Log

BROC_TEMPLATE='''#edit-mode: -*- python -*-
#coding:utf-8

#set the search path of compiler comamnd
COMPILER_PATH("/usr/bin")

#Preprocessor flags.
CPPFLAGS('debug flags', 'release flags')

#C flags.
CFLAGS('debug flags', 'release flags')

#C++ flags.
CXXFLAGS('debug flags', 'release flags')

#-I path
INCLUDE('./include $WORKSPACE/a/b/c/include')

#link flags
LDFLAGS('-lpthread -lcrypto -lrt')

#trunk dependent module in svn 
CONFIGS("app/foo/sky@trunk")
CONFIGS("app/foo/sky@trunk@12345")

#branch dependent module in svn 
CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH")
CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH@12345")

#tag dependent module in svn
CONFIGS("app/foo/sky@sky_1-0-0-1_PD_BL")

#master dependent module in git
CONFIGS("sky@master@branch")

#branch dependent module in git
CONFIGS("sky@dev@branch")

#tag dependent module in git
CONFIGS("sky@v1.0.0@tag")

#mv file or dirctory to $OUT
PUBLISH("relative path to BROC", "$OUT")

#bin
APPLICATION('name',
            Sources("src/*.cpp"),
            LinkFlags("link flags"),
            Libs("$OUT_ROOT/a/b/c/output/lib/libutil.a"))

#ut bin
UT_APPLICATION('name',
               Sources("src/*.cpp"),
               LinkFlags("link flags"),
               Libs("$OUT_ROOT/a/b/c/output/lib/libutil.a"),
               UTArgs(""))

#static library file .a
#STATIC_LIBRARY('name',
               Sources("src/*.cpp"),
               Libs("$OUT_ROOT/a/b/c/output/lib/libutil.a"))

#proto static library file .a
#PROTO_LIBRARY('name',
              'proto/*.proto',
               Proto_Flags(""),
               include(""),
               CppFlags("debug flags", "release flags"),
               CxxFlags("debug falgs","release flas"),
               Libs("$OUT_ROOT/a/b/c/output/lib/libutil.a"))'''

def scratch(target_dir):
    """
    create a BCLOUD template
    Args:
        target_dir : the directory of BROC file
    """
    broc_file = os.path.join(target_dir, 'BROC') 
    if os.path.exists(broc_file):
        Log.Log().LevPrint("ERROR", "BROC already existed in %s, couldn't create it" % target_dir)
        return -1

    with open(broc_file, 'w') as f:
        f.write(BROC_TEMPLATE)
    Log.Log().LevPrint("MSG", 'create %s ...... ok!' % broc_file)
    return 0

