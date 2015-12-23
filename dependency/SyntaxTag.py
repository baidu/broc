#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module manage the classes of Syntax

Authors: zhousongsong(doublesongsong@gmail.com)
Date:    2014/09/15 10:36:08
"""

import string
import copy

class TagVector(object):
    """
    tag base class
    """
    def __init__(self):
        """
        """
        self._v = []

    def __str__(self):
        """
        """
        return str(self._v)

    def AddV(self, v):
        """
        add a new value that containing multiple items 
        Args:
            v, a string object sepreated by blank character 
        """
        self._v.extend(string.split(v))

    def AddVs(self, vs):
        """
        add a group of value
        Args:
            vs: list(str1, str2, ..)
        """
        for v in vs:
            self._v.extend(string.split(v))

    # add single v
    def AddSV(self, v):
        """
        add a new item
        Args:
            v, a string object containing just one item
        """
        self._v.append(v)

    def AddSVs(self, vs):
        """
        add a group of items
        """
        for v in vs:
            self._v.append(v)

    def V(self):
        """
        return the value of TagVector
        """
        return self._v

    def __add__(self, other):
        """
        called by operation +
        """
        newtag = copy.copy(self)
        newtag._v = copy.copy(self._v)
        newtag._v.extend(other.V())
        return newtag

    def __sub__(self, other):
        """
        called by operation -
        """
        left_v = []        
        newtag = copy.copy(self)
        for x in self._v:
            if x not in other.V():
                left_v.append(x)
        newtag._v = left_v
        return newtag


class TagScalar(object):
    """
    tag base class    
    """
    def __init__(self):
        """
        """
        self._v = None

    def __str__(self):
        """
        """
        return str(self._v)

    def SetV(self, v):
        """
        set the value of TagSources
        """
        self._v = v

    def V(self):
        """
        return the value of TagSources
        """
        return self._v
    

class TagINCLUDE(TagVector):
    """
    tag INCLUDE
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagCPPFLAGS(TagVector):
    """
    tag CPPFLAGS
    """
    def __init__(self):
        """
        """ 
        TagVector.__init__(self)


class TagCFLAGS(TagVector):
    """
    tag CFLAGS
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagCXXFLAGS(TagVector):
    """
    tag CXXFLAGS
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagLDFLAGS(TagVector):
    """
    tag LINK FLAGS
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagInclude(TagVector):
    """
    tag Include
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagCppFlags(TagVector):
    """
    tag CppFlags
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagCxxFlags(TagVector):
    """
    tag CxxFlags
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagCFlags(TagVector):
    """
    tag CFlags
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagLDFlags(TagVector):
    """
    tag LDFlags
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagProtoFlags(TagVector):
    """
    tag LDFlags
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagLibs(TagVector):
    """
    tag Libs
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)


class TagSources(TagVector):
    """
    tag Sources
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)
        

class TagUTArgs(TagVector):
    """
    the argument tag for running ut test
    """
    def __init__(self):
        """
        """
        TagVector.__init__(self)
