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

    def GetCompileCmd(self, workspace, cvspath):
        """
        Get compile command.
        If there is Makefile, compile command is 'make clean && make'
        Else if there is build.sh, compile command is 'sh build.sh'
        Else it will be ignored.
        """
        if os.path.exists(os.path.join(workspace, cvspath, 'Makefile')):
            return 'cd %s && make clean && make' % os.path.join(workspace, cvspath)
        elif os.path.exists(os.path.join(workspace, cvspath, 'build.sh')):
            return 'cd %s && sh build.sh' % os.path.join(workspace, cvspath)
        else:
            return ''

    def CompileModule(self, task):
        """
        Compile a dependency module.
        """
        if os.path.exists(os.path.join(task.module.workspace, task.module.module_cvspath, '.BUILDED_TAG')):
            self._logger.LevPrint("MSG", "%s has built before." % task.module.module_cvspath)
            return 0
        compile_cmd = self.GetCompileCmd(task.module.workspace, task.module.module_cvspath)
        if compile_cmd == '':
            self._logger.LevPrint("INFO", "Can't find Makefile or build.sh in %s, don't build it." % task.module.module_cvspath)
            return 0
        else:
            self._logger.LevPrint("MSG", \
                    "Start to build %s. Build command is %s" % (task.module.module_cvspath, compile_cmd))
            ret, msg = Function.RunCommand(compile_cmd)
            if ret != 0:
                self._logger.LevPrint("ERROR", "Compile %s failed : %s. Command is %s" % (task.module.module_cvspath, msg, compile_cmd))
            else:
                self._logger.LevPrint("MSG", "Compile %s success." % task.module.module_cvspath)
                cmd = 'touch %s' % (os.path.join(task.module.workspace, task.module.module_cvspath, '.BUILDED_TAG'))
                Function.RunCommand(cmd)
            return ret
        return 0

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
            response['module_cvspath'] = task.module.module_cvspath
            ret = self.CompileModule(task)
            self._master.TaskDone()
            if ret != 0:
                response['result'] = False
                self._master.AddResponse(response)
                self._master.DisableBuildOK()
                self._master.Stop()
                break
            self._master.AddResponse(response)
