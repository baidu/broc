#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
test case for UTMaster
"""

import os
import sys
import Queue
import unittest

broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)
from dependency import UTMaster
from util import Log

class TestUTMaster(unittest.TestCase):
    """
    unit test for UTMaster
    """
    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    def test_UTMaster(self):
        """
        test UTMaster
        """
        queue = Queue.Queue()
        queue.put("ls -al")
        queue.put("whoami")
        queue.put("gcc --version")
        queue.put("gcc --watch out")
        queue.put("echo 'broc is great'")
        log = Log.Log()
        master = UTMaster.UTMaster(queue, log)
        master.Start()
        self.assertEqual(1, len(master.Errors()))

if __name__ == "__main__":
    unittest.main()
