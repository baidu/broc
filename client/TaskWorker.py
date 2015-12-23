#!/usr/bin/env python
# -*- coding: utf-8 -*-  

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Authors: zhousongsong(doublesongsong@gmail.com)
Date:    2015/10/26 10:50:06
"""

import os
import sys
import threading

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)

from util import Function
from dependency import BrocObject

class TaskWorker(threading.Thread):
    """
    to run build task
    """
    def __init__(self, master, all_log, logger):
        """
        Args:
            master : the TaskMaster object
            all_log : show all build log
            logger : the Log.Log() object 
        """
        threading.Thread.__init__(self)
        self._master = master
        self._all_log = all_log
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
            response = dict()
            response['result'] = True
            response['object'] = task
            # task whose type is LibCache and build cmd is empty, the lib is specified in Libs
            if task.TYPE == BrocObject.BrocObjectType.BROC_LIB and task.BuildCmd() is None:
                self._master.UpdateCache(task.Pathname())
                self._master.AddResponse(response)
                self._master.TaskDone()
                continue
            else:
                result = task.DoBuild() 

            self._master.TaskDone()
            if not result['ret']:
                response['result'] = False
                self._master.AddResponse(response)
                self._logger.LevPrint("ERROR", "%s" % result['msg'])
                self._master.DisableBuildOK()
                self._master.Stop()
                break
            else:
                info = "compile %s" % (task.pathname)
                log_level = "MSG"
                if len(result['msg']) > 0:
                    info += " [WARNING]"
                    log_level = "WARNING"
                else:
                    info += " [OK]"
                if self._all_log:
                    info += "%s\n" % task.BuildCmd()
                info += result['msg']
                self._logger.LevPrint(log_level, info)
                self._master.UpdateCache(task.Pathname())
                self._master.AddResponse(response)

