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

BROC_TEMPLATE="""#edit-mode: -*- python -*-
#coding:utf-8

#set the search path of compiler comamnd
#COMPILER("/usr/bin")

#Preprocessor flags.
#CPP_FLAGS('debug flags', 'release flags')

#C flags.
#C_FLAGS('debug flags', 'release flags')

#C++ flags.
#CXX_FLAGS('debug flags', 'release flags')

#-I path
#INCLUDE('./include $WORKSPACE/a/b/c/include')
#INCLUDE(CONVERT_OUT('./proto')

#link flags
#LINK_FLAGS('-lpthread -lcrypto -lrt')

#svn example
#CONFIGS("app/foo/sky@trunk")
#CONFIGS("app/foo/sky@trunk@12345") 
#CONFIGS("app/foo/sky@trunk@12346")
    
#CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH")
#CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH@12345")
#CONFIGS("app/foo/sky@sky_1-0-0-0_BRANCH@12346")

#CONFIGS("app/foo/sky@sky_1-0-0-1_BRANCH")
#CONFIGS("app/foo/sky@sky_1-0-0-1_BRANCH@1234")
    
#CONFIGS("app/foo/sky@sky_1-0-0-0_PD_BL")
#CONFIGS("app/foo/sky@sky_1-0-0-1_PD_BL")

#git example
#CONFIGS("sky@master")
#CONFIGS("sky@master@v1.0.0")

#CONFIGS("sky@dev")
#CONFIGS("sky@dev@v1.0.1")

#mv file or dirctory to $OUT
#PUBLISH("relative path of file", "$OUT")

#bin
#APPLICATION('name', 
#            Sources("src/*.cpp"), 
#            LinkFlags("link flags"), 
#            Libs("$OUT/a/b/c/output/lib/libutil.a"))

#UT
#UT_APPLICATION('name', 
#               Sources("src/*.cpp"),
#               LinkFlags("link flags"),
#               Libs("$OUT_ROOT/a/b/c/output/lib/libutil.a"),
#               UTArgs(""))

#.a
#STATIC_LIBRARY('name', 
#               Sources("src/*.cpp"), 
#               Libs("$OUT_ROOT/a/b/c/output/lib/libutil.a"))

#proto
#PROTO_LIBRARY('name', 
#              "proto/*.proto",
#              Proto_Flags(""), 
#              include(""), 
#              CppFlags("debug flags", "release flags"), 
#              CxxFlags("debug falgs","release flas"), 
#              Libs("$OUT_ROOT/a/b/c/output/lib/libutil.a"))

#sub directory
#Directory('demo')
"""

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

