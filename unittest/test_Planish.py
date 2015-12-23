#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
    test case for Planish
    Authors: liruihao(liruihao01@gmail.com)
    Date:   2015/11/05 17:26:42
"""
import os
import sys
import tempfile
import unittest

broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)

from dependency import Planish
from util import Function
from dependency import BrocModule_pb2 
from dependency import BrocTree
from util import Log

class TestPlanish(unittest.TestCase):
    """
    unit test for Planish
    """
    def test_svn_FilterDepNodes(self):
        """
        test Plansh._filter_dep_nodes
        """
        #init
        logger = Log.Log()
        root_node = BrocModule_pb2.Module()
        repo_domain = 'https://github.com'
        postfix = ["trunk", "_BRANCH", "_PD_BL"]
        planish = Planish.Planish(root_node, repo_domain, logger, postfix)
        reserved = BrocModule_pb2.Module()
        coming = BrocModule_pb2.Module()
        first_node = BrocTree.BrocNode(reserved, root_node, False)
        second_node = BrocTree.BrocNode(coming, root_node, False)
        #dep_Level is 1 VS dep_level is 1
        first_node.module.dep_level = 1
        first_node.module.dep_level = 1
        #tags VS BRANCH
        first_node.module.br_kind = BrocModule_pb2.Module.TAG
        second_node.module.br_kind = BrocModule_pb2.Module.BRANCH
        first_node.module.tag_name = 'ub_1-1-1-1_PD_BL'
        second_node.module.br_name = 'ub_1-0-0_BRANCH'
        self.assertEqual(-1, planish._filter_dep_nodes(first_node, second_node))
        #dep_level is 1 VS dep_level is 2 or more
        first_node.module.dep_level = 1
        second_node.module.dep_level = 2
        #tags VS tags
        first_node.module.br_kind = BrocModule_pb2.Module.TAG
        second_node.module.br_kind = BrocModule_pb2.Module.TAG
        #1-1-1-1 VS 2-2-2-2
        first_node.module.tag_name = 'ub_1-1-1-1_PD_BL'
        second_node.module.tag_name = 'ub_2-2-2-2_PD_BL'
        self.assertEqual(0, planish._filter_dep_nodes(first_node, second_node))
        #1-10-0-0 VS 1-9-0-0
        first_node.module.tag_name = 'ub_1-10-0-0_PD_BL'
        second_node.module.tag_name = 'ub_1-9-0-0_PD_BL'
        self.assertEqual(0, planish._filter_dep_nodes(first_node, second_node))
        #BRANCH VS BRANCH
        first_node.module.br_kind = BrocModule_pb2.Module.BRANCH
        second_node.module.br_kind = BrocModule_pb2.Module.BRANCH
        #1-0-0_BRANCH VS 1-0-1_BRANCH
        first_node.module.br_name = 'ub_1-0-0_BRANCH'
        second_node.module.br_name = 'ub_1-0-1_BRANCH'
        self.assertEqual(0, planish._filter_dep_nodes(first_node, second_node))
        #1-0-0_BRANCH@12345 VS 1-0-0_BRANCH@12346
        first_node.module.br_name = 'ub_1-0-0_BRANCH'
        second_node.module.br_name = 'ub_1-0-0_BRANCH'
        first_node.module.revision = '12345'
        second_node.module.revision = '12346'
        self.assertEqual(0, planish._filter_dep_nodes(first_node, second_node))
        #1-0-0_BRANCH@12345 VS 1-0-0_BRANCH@234
        second_node.module.revision = '234'
        self.assertEqual(0, planish._filter_dep_nodes(first_node, second_node))
        #tags VS BRANCH
        first_node.module.br_kind = BrocModule_pb2.Module.TAG
        second_node.module.br_kind = BrocModule_pb2.Module.BRANCH
        first_node.module.tag_name = 'ub_1-1-1-1_PD_BL'
        second_node.module.br_name = 'ub_1-0-0_BRANCH'
        self.assertEqual(0, planish._filter_dep_nodes(first_node, second_node))
        #dep_level is 2 or more VS dep_level is 2 or more
        first_node.module.dep_level = 2
        second_node.module.dep_level = 2
        #tags VS tags
        first_node.module.br_kind = BrocModule_pb2.Module.TAG
        second_node.module.br_kind = BrocModule_pb2.Module.TAG
        #1-1-1-1 VS 2-2-2-2
        first_node.module.tag_name = 'ub_1-1-1-1_PD_BL'
        second_node.module.tag_name = 'ub_2-2-2-2_PD_BL'
        self.assertEqual(1, planish._filter_dep_nodes(first_node, second_node))
        #1-10-0-0 VS 1-9-0-0
        first_node.module.tag_name = 'ub_1-10-0-0_PD_BL'
        second_node.module.tag_name = 'ub_1-9-0-0_PD_BL'
        self.assertEqual(1, planish._filter_dep_nodes(first_node, second_node))
        #BRANCH VS BRANCH
        first_node.module.br_kind = BrocModule_pb2.Module.BRANCH
        second_node.module.br_kind = BrocModule_pb2.Module.BRANCH
        #1-0-0_BRANCH VS 1-0-1_BRANCH
        first_node.module.br_name = 'ub_1-0-0_BRANCH'
        second_node.module.br_name = 'ub_1-0-1_BRANCH'
        self.assertEqual(-1, planish._filter_dep_nodes(first_node, second_node))
        #1-0-0_BRANCH@12345 VS 1-0-0_BRANCH@12346
        first_node.module.br_name = 'ub_1-0-0_BRANCH'
        second_node.module.br_name = 'ub_1-0-0_BRANCH'
        first_node.module.revision = '12345'
        second_node.module.revision = '12346'
        self.assertEqual(1, planish._filter_dep_nodes(first_node, second_node))
        #1-0-0_BRANCH@12345 VS 1-0-0_BRANCH@234
        second_node.module.revision = '234'
        self.assertEqual(0, planish._filter_dep_nodes(first_node, second_node))
        #tags VS BRANCH
        first_node.module.br_kind = BrocModule_pb2.Module.TAG
        second_node.module.br_kind = BrocModule_pb2.Module.BRANCH
        first_node.module.tag_name = 'ub_1-1-1-1_PD_BL'
        second_node.module.br_name = 'ub_1-0-0_BRANCH'
        self.assertEqual(-1, planish._filter_dep_nodes(first_node, second_node))

if __name__ == "__main__":
    unittest.main()
