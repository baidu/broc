#!/usr/bin/env python
# -*- coding: utf-8 -*-  

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Authors: zhousongsong(zhousongsong@baidu.com)
Date:    2015/11/16 14:07:06
"""

import os
import sys
import Queue
import threading
broc_path = os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..'))
sys.path.insert(0, broc_path)
from util import Function

class UTMaster(object):
    """
    UTMaster dispatches ut command to ut threads
    """
    def __init__(self, queue, logger):
        """
        Args:
            queue : the ut command queue
            logger : the Log.Log() object
        """
        self._queue =  queue
        self._logger = logger
        self._errors = list()

    def Run(self):
        """
        thread entrence function
        """
        while not self._queue.empty():
            try:
                cmd = self._queue.get(True, 1)
            except Queue.Empty:
                break
            ret, msg = Function.RunCommand(cmd, True)
            if ret != 0:
                self._logger.LevPrint("ERROR", "run ut cmd(%s) failed: %s" % (cmd, msg))
                self._errors.append(msg)
            else:
                self._logger.LevPrint("MSG", "run ut cmd(%s) OK\n%s" % (cmd, msg))
            self._queue.task_done()
        
    def Start(self):
        """
        run all ut threads
        """
        num = 4

        if self._queue.qsize() < 4:
            num = self._queue.qsize()

        workers = list()
        for i in xrange(0, num):
            t = threading.Thread(target=self.Run)
            workers.append(t)
            t.start()
        # wait all ut comands done
        self._queue.join()
        # wait all ut threads exit
        for worker in workers:
            worker.join()

    def Errors(self):
        """
        return all error msg
        """
        return self._errors
