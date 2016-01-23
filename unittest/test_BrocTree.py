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
import tempfile
import unittest
import pprint

broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)

from dependency import Planish
from dependency import PlanishUtil
from dependency import Environment
from dependency import BrocModule_pb2 
from dependency import BrocTree
from dependency.Syntax import *
from util import Function
from util import Log


class TestBrocTree(unittest.TestCase):
    """
    """
    def test_singleton(self):
        """
        Test singleton interface 
        """
        logger = Log.Log()
        repo_domain = 'https://github.com'
        postfix = ['trunk', 'BRANCH', 'PD_BL']
        root = PlanishUtil.CreateBrocModuleFromDir("..",
                                                         repo_domain,
                                                         postfix[1],
                                                         postfix[2],
                                                         logger)
        tree = BrocTree.BrocTree()
        tree.SetRoot(root)
        tree1 = BrocTree.BrocTree()
        tree2 = BrocTree.BrocTree()
        self.assertEqual(tree.Id(), tree1.Id())
        self.assertEqual(tree.Id(), tree2.Id())

    def test_git_module(self):
        """
        """
        logger = Log.Log()
        repo_domain = 'https://github.com'
        postfix = ['trunk', 'BRANCH', 'PD_BL']
        root = PlanishUtil.CreateBrocModuleFromDir("..",
                                                         repo_domain,
                                                         postfix[1],
                                                         postfix[2],
                                                         logger)
        
        self.assertTrue(root.is_main)
        self.assertFalse(root.tag_name)
        self.assertTrue(root.br_name)
        self.assertEqual(root.name, 'broc')
        self.assertEqual(root.dep_level, 0)
        self.assertEqual(root.repo_kind, 2)
        self.assertEqual(root.br_kind, 3)
        broc_file = os.path.join(root.root_path, 'BROC')
        root_env = Environment.Environment(root)
        Environment.SetCurrent(root_env)
        sys.argv = ['PLANISH']
        try:
            execfile(broc_file)
        except BaseException as ex:
            logger.LevPrint("ERROR", "run BROC %s" % ex)

if __name__ == "__main__":
    unittest.main()
