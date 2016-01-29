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
import traceback

broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)

from dependency import BrocConfig
from dependency import Planish
from dependency import PlanishUtil
from dependency import Environment
from dependency import BrocModule_pb2 
from dependency import BrocTree
from dependency import Syntax
from util import Function
from util import Log


class TestBrocLoader(unittest.TestCase):
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
        loader1 = Syntax.BrocLoader()
        loader2 = Syntax.BrocLoader()
        self.assertEqual(loader1.Id(), loader2.Id())

    def test_load_broc(self):
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
        node = BrocTree.BrocNode(root, None, True)
        Syntax.BrocLoader().SetRoot(node)
        Syntax.BrocLoader().LoadBROC()
        if Syntax.BrocLoader().LackBrocModules():
            print(Syntax.BrocLoader().LackBrocModules())

if __name__ == "__main__":
    unittest.main()
