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
import Queue

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)

import TaskWorker
from dependency import BrocObject

class TaskMaster(object):
    """
    TaskMaster object is a thread object master
    dispatching build task
    """
    def __init__(self, num, cache_master, changed_list, logger):
        """
        Args:
            num : the number of build threads
            cache_master : the BrocObjectMaster object
            changed_list : the changed file list of BrocObject
            logger : the Log.Log() object
        """
        self._logger = logger
        self._cache_master = cache_master
        self._changed_list = changed_list 
        self._queue = Queue.Queue()             # request queue
        self._response_queue = Queue.Queue()    # response queue
        self._running = True
        self._workers = list()
        self._build_ok = True
        for i in xrange(0, num):
            self._workers.append(TaskWorker.TaskWorker(self, logger))

    def DisableBuildOK(self):
        """
        set build flag as False means fail to build 
        """
        self._build_ok = False

    def BuildOK(self):
        """
        return whether all build tasks have  done successfully
        """
        return self._build_ok

    def Start(self):
        """
        run build thread 
        """
        self._logger.LevPrint("MSG", "%d threads to build ..." % len(self._workers))

        all_tasks = 0
        add_tasks = 0
        degree = dict()              #key is file path,value is number of deps in changed list
        changed_dict = dict()        #key is file path,value is BrocObject
        #get degree of module
        for broc_object in self._changed_list:
            degree[broc_object.Pathname()] = 0
            changed_dict[broc_object.Pathname()] = broc_object

        for broc_object in self._changed_list:
            for redeps in broc_object.reverse_deps:
                if redeps.Pathname() in degree:
                    degree[redeps.Pathname()] += 1
        #add no deps object
        for file_path in degree:
            all_tasks += 1
            broc_object = changed_dict[file_path]
            if degree[file_path] == 0:
                self.AddTask(broc_object)
                add_tasks += 1

        for worker in self._workers:
            worker.start()

        while add_tasks < all_tasks:
            response = self.FetchResponse()
            if response == -1 or not response['result']:
                break
            now = response['object']
            for redeps in now.reverse_deps:
                if redeps.Pathname() in degree:
                    degree[redeps.Pathname()] -= 1
                    if degree[redeps.Pathname()] == 0:
                        self.AddTask(redeps)
                        add_tasks = add_tasks + 1
        self.Wait()
    
    def Wait(self):
        """
        wait all tasks have been done
        """
        self._queue.join()
        for worker in self._workers:
            worker.Stop()
            worker.join()

    def TaskDone(self):
        """
        notity queue the task has been done
        """
        self._queue.task_done()

    def Stop(self):
        """
        stop thread
        """
        self._running = False
        for worker in self._workers:
            worker.Stop()

        # release left task and to release thread blocking at Wait()
        while not self._queue.empty():
            self._queue.get()
            self._queue.task_done()

    def AddTask(self, task):
        """
        add build task to master
        Args:
            task : the BrocObject.BrocObject object
        """
        if self._running:
            self._queue.put(task)

    def AddResponse(self, response):
        """
        add build response to master
        Args:
            response : the response to master
                       response['result'] : fail means build fail, success means build success
                       response['object'] : the BrocObject
        """
        if self._running:
            self._response_queue.put(response)

    def FetchTask(self):
        """
        fetch a build task
        Returns:
            return a task if fetch successfully
            return None if fetch timeout
            return -1 if TaskMaster stop run
        """
        # block 1 second at most
        if not self._running:
            return -1

        task = None
        try:
            task = self._queue.get(True, 0.1)
        except Queue.Empty:
            pass

        return task 
    
    def FetchResponse(self):
        """
        fetch a build response
        Returns:
            return a response if fetch successfully
            return -1 if TaseMaster stop run
        """
        if not self._running:
            return -1

        response = self._response_queue.get(True)
        return response

    def UpdateCache(self, pathname):
        """
        update cache 
        Args:
            pathname : the cvs path of cache
        """
        self._cache_master.UpdateCache(pathname)
