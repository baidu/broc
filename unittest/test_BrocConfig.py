#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
    test case for create dependent tree of modules
    Authors: zhousongsong(doublesongsong@gmail.com)
    Date:   2016/01/22 17:26:42
"""
import os
import sys
import unittest
import pprint

broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)

from dependency import BrocConfig


class TestBrocConfig(unittest.TestCase):
    """
    """
    def test_singleton(self):
        """
        """
        config1 = BrocConfig.BrocConfig()
        config2 = BrocConfig.BrocConfig()
        self.assertEqual(config1.Id(), config2.Id())

if __name__ == "__main__":
    unittest.main()
