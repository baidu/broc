#!/usr/bin/env python
# -*- coding: utf-8 -*-  

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Authors: zhousongsong(zhousongsong@baidu.com)
Date:    2015/10/13 14:50:06
"""

import os
import sys
import threading
import Queue
import cPickle

import Source
import Target
import BrocObject

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)
from util import Function


class BrocObjectMaster(threading.Thread):
    """
    cache Manager class
    BrocObjectMaster object is a thread object
    """
    def __init__(self, cache_file, root, logger):
        """
        Args:
            cache_file : the path of cache file
            root : the root path of main module
            logger : the Log.Log() object
        """
        threading.Thread.__init__(self)
        self._cache_file = cache_file
        self._root = root
        self._logger = logger
        self._queue = Queue.Queue()  # request queue
        self._version = 0.1
        self._cache = dict()     # {cvs path : BrocObject} 
        self._changed_cache = set() # set(BrocObject)
        self._event = threading.Event()
        self._dumped_str = ""
    
    def WaitCheckDone(self):
        """
        wait all cache has been check
        """
        self._queue.put(('check_done', None))
        self._event.wait()
        self._event.clear()

    def Stop(self):
        """
        stop thread
        """
        self._queue.put(('stop', None))

    def run(self):
        """
        Returns:
        """
        while True:
            action, obj = self._queue.get()
            if action == 'check':
                self._handle_check(obj)
                continue
            elif action == 'update':
                self._handle_update(obj)
                continue
            elif action == 'check_done':     
                self._handle_check_done()
                continue
            elif action == 'stop':
                break

    def _handle_check(self, obj):
        """
        used by BrocObjectMaster thread
        to check whether cache(cvspath) is changed
        Args:
            obj : target.Target object
        """
        self._check_target(obj)

    def _check_head_cache(self, pathname, source_cache):
        """
        to check whether head file changed
        if head cache does not exist, create a new head cache
        Args:
            pathname : the cvs path of head file
            source_cache : the BrocObject.SourceCache
        Returns:
            return True if head cache changed or create a new head cache
            return False if head cache didn't change
        """
        if pathname not in self._cache:
            self._add_head_cache(pathname, source_cache)
            return True

        if self._cache[pathname].IsChanged(None):
            self._cache[pathname].EnableBuild()
            return True
        else:
            return False

    def _check_source_cache(self, source, target_cache):
        """
        to check source object's cache
        Args:
            source : the Source.Source object
            target_cache : the BrocObject.TargetCache object
        """
        # source infile no exists in cache
        if source.InFile() not in self._cache:
            self._add_source_cache(source, target_cache)
            return True

        # check header files
        # remove useless dependent cache
        source_cache = self._cache[source.InFile()]
        last_headers = set(map(lambda x: x.Pathname(), source_cache.Deps()))
        now_headers = source.builder.GetHeaderFiles()
        missing_headers = last_headers - now_headers
        for f in missing_headers:
            source_cache.DelDep(f)
            self._cache[f].DelReverseDep(source_cache.Pathname())
        # check head files source object depended
        ret = False
        for f in source.builder.GetHeaderFiles():
            if self._check_head_cache(f, source_cache):
                ret = True

        # head files changed
        if ret:
            self._cache[source.InFile()].EnableBuild()
            return ret

        # head files no changed, check itself
        if self._cache[source.InFile()].IsChanged(source):
            self._cache[source.InFile()].EnableBuild()
            return True

        return False

    def _check_target(self, target):
        """
        to check target cache
        Args:
            target : can be Application, StaticLibrary, UT_Application, ProtoLibrary
        """
        ret = False
        # self._logger.LevPrint("MSG", "check target %s" % target.OutFile())
        #1. check whether target cache exists
        if target.OutFile() not in self._cache:
            self._add_target_cache(target)
            return True
        #2. check whether target cache is a empty cache, empty cache was created by target depended on it
        target_cache = self._cache[target.OutFile()]
        if not target_cache.initialized:
            #self._logger.LevPrint("MSG", "Initialize target %s" % target.OutFile())
            target_cache.Initialize(target)
            target_cache.EnableBuild()

        #3. check all source object, remove uesless source cache
        last_sources = set()
        for x in target_cache.Deps():
            if x.TYPE is BrocObject.BrocObjectType.BROC_SOURCE:
                last_sources.add(x.Pathname())
        now_sources = target.InFiles()
        missing_sources = last_sources - now_sources
        for missing in missing_sources:
            target_cache.DelDep(missing)
            self._cache[missing].DelReverseDep(target.OutFile())
        # check source objets contained in trget object
        for source in target.Sources():
            if self._check_source_cache(source, self._cache[target.OutFile()]):
                ret = True

        #4. check all .a files, remove useless .a cache first
        last_libs = set()
        for x in target_cache.Deps():
            if x.TYPE is BrocObject.BrocObjectType.BROC_LIB:
                last_libs.add(x.Pathname())
        now_lib_files = target.Libs()
        missing_libs = last_libs - now_lib_files
        for missing in missing_libs:
            target_cache.DelDep(missing)
            self._cache[missing].DelReverseDep(target.OutFile())
        # check .a files contained in target object
        for lib_file in target.Libs():
            # self._logger.LevPrint("MSG", "check dep lib %s for target %s" % (lib_file, target.OutFile()))
            if self._check_lib_cache(lib_file, target_cache):
                ret = True

        # if there is source or .a has changed, tareget need to rebuild
        if ret:
            target_cache.EnableBuild()
            return True

        #5. check target file itself
        if self._cache[target.OutFile()].IsChanged(target):
            self._cache[target.OutFile()].EnableBuild()
            return True

        return False

    def _check_lib_cache(self, pathname, target_cache):
        """
        check lib cache, target(.exe, .a) can depend on .a
        when add target object's cache, there is just the cvs path of .a file,
        so here just creates a empty target cache and save the dependent relation,
        and when handle the true dependent object will initiailze it 
        Args:
            pathname: the cvs path of .a file
            target_cache : the target object's reversed dependent target cache 
        """
        if pathname not in self._cache:
            self._add_lib_cache(pathname, target_cache)
            return True
        # BrocObject object will check whether dep or reverse dep existed already,
        # there is no need to check, just add it, it will ok
        self._cache[pathname].AddReverseDep(target_cache)
        target_cache.AddDep(self._cache[pathname]) 

    def _add_source_cache(self, source, target_cache):
        """
        add a new source cache, and create header cache
        Args:
            source : the Source.Source object
            target_cache : the BrocObject object that depended on source cache
        """
        source_cache = BrocObject.SourceCache(source.InFile(), source)
        self._cache[source.InFile()] = source_cache
        source_cache.AddReverseDep(target_cache)
        target_cache.AddDep(source_cache)

        # add header cache for source cache
        header_files = source.builder.GetHeaderFiles()
        for f in header_files:
            if f in self._cache:
                source_cache.AddDep(self._cache[f])
                self._cache[f].AddReverseDep(source_cache)
            else:
                self._add_head_cache(f, source_cache)

    def _add_target_cache(self, target):
        """
        add a new target cache(lib cache, (ut)app cache)
        Args:
            target : Target.Target object
        """
        # self._logger.LevPrint("MSG", "add target cache(%s)" % target.OutFile())
        target_cache = None
        if isinstance(target, Target.StaticLibrary):
            target_cache = BrocObject.LibCache(target.OutFile(), target)
        elif isinstance(target, Target.Application):
            target_cache = BrocObject.AppCache(target.OutFile(), target)
        elif isinstance(target, Target.ProtoLibrary):
            target_cache = BrocObject.LibCache(target.OutFile(), target)

        self._cache[target.OutFile()] = target_cache
        # handle source object
        for source in target.Sources():
            if source.InFile() in self._cache:
                self._cache[source.InFile()].AddReverseDep(target_cache)
                target_cache.AddDep(self._cache[source.InFile()])
            else:
                self._add_source_cache(source, target_cache)

        # handle dependent lib cache
        for lib in target.Libs():
            if lib in self._cache:
                self._cache[lib].AddReverseDep(target_cache)
                target_cache.AddDep(self._cache[lib])
            else:
                # add empty dependent lib cache object
                # this cache object need to be initialized 
                self._add_lib_cache(lib, target_cache)

    def _add_lib_cache(self, pathname, target_cache):
        """
        add empty lib cache
        Args:
            pathname : the cvspath of .a file
            target_cache : the cache of target depending on .a file
        """
        depend_cache = BrocObject.LibCache(pathname, target_cache, False)
        self._cache[pathname] = depend_cache 
        depend_cache.AddReverseDep(target_cache)
        target_cache.AddDep(depend_cache)

    def _add_head_cache(self, pathname, source_cache):
        """
        add head file cache
        Args:
            pathname : the cvs path of head file
            source_cache : the BrocObject.SourceCache object
        """
        cache = BrocObject.HeaderCache(pathname)
        self._cache[pathname] = cache
        source_cache.AddDep(cache)
        cache.AddReverseDep(source_cache)
        
    def CheckCache(self, obj):
        """
        to check whether cache(cvspath) is changed
        Args:
            obj : can be target, source object
        """
        self._queue.put(('check', obj))

    def _handle_check_done(self):
        """
        filter all changed files
        """
        for k, cache in self._cache.iteritems():
            if not cache.IsBuilt() and cache.TYPE in [BrocObject.BrocObjectType.BROC_SOURCE,
                                                      BrocObject.BrocObjectType.BROC_LIB,
                                                      BrocObject.BrocObjectType.BROC_APP]:
                self._changed_cache.add(cache)
        self._event.set()

    def UpdateCache(self, pathname):
        """
        update cache whose key is pathname, this method is used after build
        Args:
           pathname : the cvs path of file 
        """
        self._queue.put(('update', pathname))

    def _handle_update(self, pathname):
        """
        update cache whose key is pathname, this method is used after build
        Args:
           pathname : the cvs path of file 
        """
        # self._logger.LevPrint("MSG", "save cache %s" % pathname)
        if pathname not in self._cache:
            self._logger.LevPrint("INFO", "%s not in cache, could not update" % pathname)
            return 
        cache = self._cache[pathname]
        cache.DisableBuild()
        if cache.TYPE == BrocObject.BrocObjectType.BROC_HEADER:
            return
        cache.Update()
        # save cache into file 
        self._save_cache()

    def GetChangedCache(self):
        """
        return the list of changed file
        Returns:
            return a list object composed of cvspath
        """
        return self._changed_cache 

    def LoadCache(self):
        """
        load cache
        """
        # no cache file
        if not os.path.exists(self._cache_file):
            self._logger.LevPrint("MSG", "no broc cache and create a empty one")
            return 
        # try to load cache file
        try:
            with open(self._cache_file, 'rb') as f:
                caches = cPickle.load(f)
                if caches[0] != self._version:
                    self._logger.LevPrint("MSG", "cache version(%s) no match system(%s)" 
                                          % (caches[0], self._version))
                else:
                    for cache in caches[1:]:
                        self._cache[cache.Pathname()] = cache
                        #self._logger.LevPrint("MSG", 'cache %s build is %s' % (cache.Pathname(), cache.build))
        except BaseException as err:
            self._logger.LevPrint("MSG", "load broc cache(%s) faild(%s), create a empty cache"
                                 % (self._cache_file, str(err)))

    def _save_cache(self):
        """
        save cache
        """
        dir_name = os.path.dirname(self._cache_file)
        Function.Mkdir(dir_name)
        try:
            caches = [self._version]
            caches.extend(map(lambda x: self._cache[x], self._cache))
            with open(self._cache_file, 'wb') as f:
                cPickle.dump(caches, f)
        except Exception as err:
            self._logger.LevPrint("ERROR", "save cache(%s) failed(%s)" 
                                  % (self._cache_file, str(err)))

    def _dump(self, pathname, level):
        """
        dump dependecy, DFS
        """
        if self._cache[pathname].build is True:
            infos = "\t" * level + "[" + pathname + "]\n"          #need to build
        else:
            infos = "\t" * level + pathname + "\n"
        self._dumped_str += infos
        for deps_pathname in self._cache[pathname].deps:
            self._dump(deps_pathname.Pathname(), level + 1)

    def Dump(self):
        """
        dump dependency relation of files
        """
        dumped_file = os.path.join(self._root, ".BROC.FILE.DEPS")
        for pathname in self._cache:
            # the length of reverse deps is 0 means it is application or libs of main module
            if len(self._cache[pathname].reverse_deps) <= 0:
                self._dump(pathname, 0)
        try:
            dir_name = os.path.dirname(dumped_file)
            Function.Mkdir(dir_name)
            with open(dumped_file, "w") as f:
                f.write("" + self._dumped_str)
        except IOError as err:
            self._logger.LevPrint("ERROR", "save file dependency failed(%s)" % err)
