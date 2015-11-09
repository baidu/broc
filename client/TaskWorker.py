#!/usr/bin/env python
# -*- coding: utf-8 -*-  

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Authors: zhousongsong(zhousongsong@baidu.com)
Date:    2015/10/26 10:50:06
"""

import os
import sys
import threading
import Queue

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)

from util import Function
from dependency import BrocObject

class TaskWorker(threading.Thread):
    """
    to run build task
    """
    def __init__(self, master, logger):
        """
        Args:
            master : the TaskMaster object
            logger : the Log.Log() object 
        """
        threading.Thread.__init__(self)
        self._master = master
        self._logger = logger
        self._running = True

    def Stop(self):
        """
        to stop build thread 
        """
        self._running = False

    def run(self):
        """
        fetch one task and handle it
        """
        while self._running:
            task = self._master.FetchTask()
            if isinstance(task, int) and task == -1:
                # master encounter error, break
                break
 
            if not task:
                #TODO no task to deal, sleep for a while
                continue
            if task.build_cmd is None:
                result = dict()
                result['ret'] = True
            else:
                # Log.Log().LevPrint("INFO", "%s" % task.BuildCmd())
                result = task.DoBuild() 
            self._master.TaskDone()
            response = dict()
            response['result'] = False
            response['object'] = task
            if not result['ret']:
                self._master.AddResponse(response)
                self._logger.LevPrint("ERROR", "%s" % result['msg'])
                self._master.Stop()
                break
            else:
                response['result'] = True
                self._logger.LevPrint("MSG", "[OK] %s" % task.BuildCmd())
                self._master.UpdateCache(task.Pathname())
                self._master.AddResponse(response)

