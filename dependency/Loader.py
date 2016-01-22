#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2016 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: Loader.py
Author: zhousongsong(zhousongsong@baidu.com)
Date: 2016/01/22 11:32:37
"""
import os
import sys
import threading
import Queue

broc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_path)

from dependency import Environment
from dependency.Syntax import *
from util import Function
from util import Log

class Loader(object):
    """
    This class parses all BROC file and creates Environment object for each BROC
    """
    def __init__(self, node, module_queue, logger, mode='build', wokers=5):
        """
        Args:
            env : the Environment of main module
            module_queue : the queue object storing BrocModule_pb2.Module objectes
            logger : the Log.Log object
            mode : the mode of build, mode can be 'build' or 'release', the default is 'build'
            workers: the number of thread object loading BROC 
        """
        self._main_module = node
        self._queue = module_queue
        self._logger = logger
        self._build_mode = mode
        self._workers = wokers
        self._lock_env_cache = threading.Lock()
        self._env_cache = dict() # { module cvs path : Environment }
        self._load_done = False
        self._load_ok = True
        self._main_env = None

    def LoadBroc(self):
        """
        initialize loading thread, main process waits for all BROC done
        """
        if not self._load_main_broc():
            self._load_done = False
            self._load_ok = False
            return 

        for i in range(0, self._workers):
            t = threading.Thread(target=self._load_all_broc)
            t.daemon = True
            t.start()
        
        # waiting for all BROC files have been deal
        self._queue.join()
        self._load_done = True

    def _load_main_broc(self):
        """
        load main module's BROC file
        Returns:
            return False if fail to load BROC file
            return True if load BROC file successfully
        """
        # BROC file

        f = os.path.join(self._main_module.root_path, 'BROC')
        self._main_env = Environment.Environment(self._main_module)
        if self._build_mode == "release":
            self._main_env.DisableDebug()

        Environment.SetCurrent(self._main_env)
        try:
            execfile(f)
        except BaseException as ex:
            self._logger.LevPrint("ERROR", 'parsing %s failed(%s)' \
                                 % (self._main_module.broc_cvspath, ex))
            return False

        self._main_env.Action()
        self._add_env(self._main_module.module_cvspath, self._main_env)
        
        return True

    def MainEnv(self):
        """
        return main envirionment object
        """
        return self._main_env

    def LoadOK(self):
        """
        whether load all modules ok
        """
        return self._load_ok

    def _add_env(self, module_cvspath, env):
        """
        add env object
        Args:
            module_cvspath : the cvs pat of module
            env : the Environment object
        """
        self._lock_env_cache.acquire()
        self._env_cache[module_cvspath] = env
        self._lock_env_cache.release()

    def _load_all_broc(self):
        """
        thread function loading all BROC files, each thread object fetches one module(BrocModule_pb2.Module object) 
        from queue, runs the BROC file of the module and creates one Environment object
        if execfile(BROC) throw exception, stop all thread objects
        """
        while not self._load_done:
            module = None
            try:
                module = self._queue.get(True, 1)
            except Queue.Empty:
                continue
            # BROC file
            f = os.path.join(module.root_path, 'BROC')
            env = Environment.Environment(module)
            if self._build_mode == "release":
                env.DisableDebug()
            Environment.SetCurrent(env)
            try:
                execfile(f)
            except BaseException as ex:
                self._queue.task_done()
                self._logger.LevPrint("ERROR", 'parsing %s failed(%s)' % (module.broc_cvspath, ex))
                self._load_done = True
                self._load_ok = False
                # discard all BROC in queue
                while not self._queue.empty():
                    self._queue.get()
                    self._queue.task_done()
                break

            env.SetCompilerDir(self._main_env.CompilerDir())
            env.Action()

            self._add_env(module.module_cvspath, env)
            self._queue.task_done()

    def Envs(self):
        """
        return a list containning all environment object
        """ 
        return map(lambda x: self._env_cache[x], self._env_cache)

