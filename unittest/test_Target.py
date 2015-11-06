#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
    test case for target
    Authors: zhousongsong(zhousongsong@baidu.com)
    Date:   2015/09/16 10:44:24
"""
import os
import sys
import tempfile
import unittest

broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)
import util

class TestProtoLibrary(unittest.TestCase):
    """
    unit test for ProtoLibrary
    """
    def setUp(self):
        """
        """
        self._tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """
        """
        util.Function.DelFiles(self._tmp_dir)

    def test_PreAction(self):
        """
        test preprocess of ProtoLibrary
        """
        util.Function.Mkdir(os.path.join(self._tmp_dir, 'proto'))
        util.Function.Mkdir(os.path.join(self._tmp_dir, 'proto', 'test'))

if __name__ == "__main__":
    unittest.main()
