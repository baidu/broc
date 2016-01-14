
################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Authors: zhousongsong(doublesongsong@gmail.com)
Date:    2015/10/13 14:50:06
"""

import os
import sys

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)
from util import Function
from util import Log
        
class BrocObjectType(object):
    """
    cache type enum
    """
    BROC_UNKNOW = 0
    BROC_HEADER = 1 # head file
    BROC_SOURCE = 2 # souce file
    BROC_LIB = 3    # .a
    BROC_APP = 4    # exe


class BrocObject(object):
    """
    base cache class
    """
    TYPE = BrocObjectType.BROC_UNKNOW
    def __init__(self, pathname, initialized=True):
        """
        Args:
            pathname : the cvs path of object file
            initialized : to mark whether BrocObject need initialized, default is True,
                          if initialized is False, create a empty BrocObject object
        """
        self.pathname = pathname
        self.initialized = initialized # initialized flag
        self.deps = set()              # dependent BrocObject
        self.reverse_deps = set()      # reversed dependent BrocObject
        self.hash = None               # hash value of content
        self.modify_time = 0           # the last modify time of BrocObject file
        self.build_cmd = ""            # the commond of BrocObject to build
        if self.initialized:
            try:
                self.hash = Function.GetFileHash(pathname)
                if self.hash:
                    self.modify_time = os.stat(self.pathname.st_mtime) 
            except BaseException:
                pass
        self.build = True             # build flag, if build is True, the BrocObject need to compiled

    def __eq__(self, other):
        """
        """
        if self.pathname == other.pathname:
            return True
        else:
            return False

    def __str__(self):
        """
        return build_cmd
        """
        return self.build_cmd
        
    def Initialize(self, target):
        """
        initialize BrocObject with target, overwited by child class
        """
        pass

    def Pathname(self):
        """
        return cache file name
        """
        return self.pathname

    def BuildCmd(self):
        """
        return build cmd
        """
        return self.build_cmd

    def UpdateBuildCmd(self, cmd):
       '''
       update bulild cmd
       '''
       self.build_cmd = cmd

    def Hash(self):
        """
        return the hash value
        """
        return self.hash

    def Deps(self):
        """
        return all dependent caches 
        """
        return self.deps

    def ReverseDeps(self):
        """
        return all reverse dependent cache
        """
        return self.reverse_deps

    def AddReverseDep(self, obj):
        """
        add reverse dependent BrocObject
        Args:
            obj : the BrocObject object
        """
        for item in self.reverse_deps:
            # obj has existed already
            if item == obj:
                return

        self.reverse_deps.add(obj)

    def DelReverseDep(self, pathname):
        """
        delete reversed dependent cache
        Args:
            pathname : the name of reversed dependent cache 
        """
        for item in self.reverse_deps:
            if item.Pathname() == pathname:
                self.reverse_deps.remove(item)
                return

    def AddDep(self, obj):
        """
        add dep file
        Args:
            obj : the BrocObject object
        """
        for item in self.deps:
            # obj has exist already
            if item == obj:
                return
        self.deps.add(obj)

    def DelDep(self, pathname):
        """
        delete dependent cache
        Args:
            pathname : the name of dependent cache 
        """
        for item in self.deps:
            if item.Pathname() == pathname:
                self.deps.remove(item)
                return

    def EnableBuild(self):
        """
        enable build flag
        """
        self.build = True
        # set all reversed dependent BrocObject to build
        self.NotifyReverseDeps()

    def EnableBuildNoReverse(self):
        '''
        enable build flag, but not notify reversed cache
        '''
        self.build = True

    def Build(self):
        '''
        return build flag
        '''
        return self.build

    def IsBuilt(self):
        """
        check whether BrocObject has been built already
        Returns:
            return True if BrocObject has been built,
            return False if BrocObject has not been built
        """
        return not self.build

    def IsReady(self):
        """
        to check whether BrocObject can be built 
        if all dependent caches is built, the BrocObject object can be built 
        Returns:
            return 1 if all dependent caches have been built and it is still not been built
            return 0 if there is one dependent cache has not been build
            return -1 if all dependent caches have been build and it has been built already
        """
        if not self.build:
            return -1

        for dep in self.deps:
            if not dep.IsBuilt():
                return 0

        return 1

    def DoBuild(self):
        """
        to run build cmd
        Returns:
            return (True, '') if build successfully
            return (False, 'error msg') if fail to build   
        """
        result = dict()
        ret, msg = Function.RunCommand(self.build_cmd, ignore_stderr_when_ok = False)
        if ret != 0:
            result['ret'] = False
            result['msg'] = "%s\n%s" % (str(self.build_cmd), msg)
        else:
            self.build = False
            result['ret'] = True
            result['msg'] = msg
        return result

    def NotifyReverseDeps(self):
        """
        to notify all reversed dependent BrocObject objects to build
        """
        for obj in self.reverse_deps:
            #Log.Log().LevPrint("MSG", "%s nofity reverse cache dep(%s) build" \
#% (self.pathname, obj.Pathname()))
            obj.EnableBuild()

    def IsChanged(self, target=None):
        """
        to check whether cache is changed
        Args:
            target : the target that compared to 
        Returns:
            if file is modified, return True
            if file is not modified, return False
        """
        # if build flag is True, means it has changed 
        if self.build:
            #Log.Log().LevPrint('MSG', 'cache %s build mark is true' % self.pathname)
            return True
        # check mtime
        modify_time = None
        try:
            modify_time = os.stat(self.pathname).st_mtime
        except BaseException:
            Log.Log().LevPrint('MSG', 'get %s modify_time failed' % self.pathname)
            self.build = True
            self.modify_time = 0
            return True

        if modify_time == self.modify_time:
            return False
        else:
            self.modify_time = modify_time
            ret = False
            # check hash
            _hash = Function.GetFileHash(self.pathname)
            if _hash != self.hash:
                self.hash = _hash
                Log.Log().LevPrint('MSG', '%s content changed' % self.pathname)
                self.build = True
                ret = True
            return ret

    def IsSelfChanged(self):
        '''
        to check whether object self changed
        Returns:
            -1 : the file that cacahe representing is missing
            0 : not changed
            1 : changed
        '''
        if not os.path.exists(self.pathname):
            return -1

        # check mtime
        modify_time = None
        try:
            modify_time = os.stat(self.pathname).st_mtime
        except BaseException:
            Log.Log().LevPrint('MSG', 'get %s modify_time failed' % self.pathname)
            self.modify_time = 0
            return 1

        if modify_time == self.modify_time:
            return 0
        else:
            self.modify_time = modify_time
            ret = 0
            # check hash
            _hash = Function.GetFileHash(self.pathname)
            if _hash != self.hash:
                self.hash = _hash
                ret = 1
                Log.Log().LevPrint('MSG', '%s content changed' % self.pathname)
            return ret


    def Update(self):
        """
        Update modify time and hash value of cache object
        """
        # update modify time
        modify_time = None
        try:
            modify_time = os.stat(self.pathname).st_mtime
        except BaseException as err:
            Log.Log().LevPrint("ERROR", "update cache(%s) failed: %s" % (self.pathname, err))
            return 

        if self.modify_time == modify_time:
            self.build = False
            return 
        
        self.modify_time = modify_time
        # update hash
        _hash = Function.GetFileHash(self.pathname)
        # Log.Log().LevPrint("MSG", "update %s hash id(%s) %s --> %s" % (self.pathname, id(self), self.hash, _hash))
        self.hash = _hash 
        self.build = False

    def DisableBuild(self):
        """
        disable build flag
        """
        self.build = False


class HeaderCache(BrocObject):
    """
    .h cache
    """
    TYPE = BrocObjectType.BROC_HEADER

    
class SourceCache(BrocObject):
    """
    .cpp .c cache
    """
    TYPE = BrocObjectType.BROC_SOURCE
    def __init__(self, source):
        """
        Args:
            source  : the Souce.Source object
        """
        BrocObject.__init__(self, source.OutFile(), False)
        self.build_cmd = source.GetBuildCmd()
        self.src_obj = BrocObject(source.InFile())
            
    def IsChanged(self, target):
        """"
        to check whether source file changed
        because need to check whether build option change, we have to take target as argument
        Args:
            target  : the Souce.Source object
        Returns:
            if file is modified, return True
            if file is not modified, return False
        """
        # to check source file 
        if self.src_obj.IsChanged(None):
            #Log.Log().LevPrint('MSG', "%s changed" % self.pathname)
            self.build_cmd = target.GetBuildCmd()
            self.build = True
            return True

        # to check build option
        if self.build_cmd != target.GetBuildCmd():
            #Log.Log().LevPrint('INFO', "cache(%s, type:%s) build cmd changed" % (self.pathname, self.TYPE))
            #Log.Log().LevPrint('MSG', "%s -- > %s" % (self.build_cmd, target.GetBuildCmd()))
            self.build_cmd = target.GetBuildCmd()
            self.build = True
            return True

        # to check obj file
        if BrocObject.IsChanged(self, target.InFile()):
            #Log.Log().LevPrint('MSG', "obj %s changed" % targetg.InFile())
            self.build_cmd = target.GetBuildCmd()
            self.build = True
            return True

        return False

    def IsSelfChanged(self):
        '''
        to check whether source file and obj file changed
        Returns:
            0 : not changed
            1 : changed
            -1: the source file is missing
        '''
        # check source file itself
        ret = self.src_obj.IsSelfChanged()
        # source file changed or missed
        if ret != 0:
            return ret
        # source file not change, to check object file
        else:
            ret = BrocObject.IsSelfChanged(self)
            return 0 if ret == 0 else 1

    def Update(self):
        """
        update source cache, this function update object file's cache
        source file's modify time and hash value are updated in IsChanged()
        """
        # update head files
        for head_cache in self.deps:
            head_cache.DisableBuild()
        # update source file
        self.src_obj.Update() 
        BrocObject.Update(self)
        

        
class LibCache(BrocObject):
    """
    .a cache
    """
    TYPE = BrocObjectType.BROC_LIB
    def __init__(self, pathname, target, initialized=True):
        """
        Args:
            pathname : the cvs path of lib file
            target : the Target.STATIC_LIBRARY object
            initialized : whether initialize LibCache object
        """
        BrocObject.__init__(self, pathname, initialized)
        if initialized:
            self.build_cmd = target.GetBuildCmd()
        else:
            self.build_cmd = None

    def Initialize(self, target):
        """
        to initialize LibCache
        Args:
            target : the Target.Target object
        """
        if not self.initialized:
            try:
                self.hash = Function.GetFileHash(self.pathname)
                if self.hash:
                    self.modify_time = os.stat(self.pathname.st_mtime) 
            except BaseException:
                pass
            self.build_cmd = target.GetBuildCmd()
            self.initialized = True

    def IsChanged(self, target):
        """
        to check whether Libcache change
        because need to check whether build option, we have to take a target as argument
        Args:
            target  : the Target.Target object
        Returns:
            if file is modified, return True
            if file is not modified, return False
        """
        # to check build option
        if self.build_cmd != target.GetBuildCmd():
            self.build_cmd = target.GetBuildCmd()
            Log.Log.LevPrint("MSG", "%s build cmd changed" % self.pathname)
            self.build = True
            return True
        else:
            return BrocObject.IsChanged(self, target.OutFile())


class AppCache(BrocObject):
    """
    bin file cache
    """
    TYPE = BrocObjectType.BROC_APP
    def __init__(self, target):
        """
            target : the Target.Target object
        """
        BrocObject.__init__(self, target.OutFile())
        self.build_cmd = target.GetBuildCmd()

    def IsChanged(self, target):
        """
        to check whether source file changed
        Args:
            target  : the Souce.Source object
        Returns:
            if file is modified, return True
            if file is not modified, return False
        """
        # to check build option
        if self.build_cmd != target.GetBuildCmd():
            self.build_cmd = target.GetBuildCmd()
            self.build = True
            return True
        elif BrocObject.IsChanged(self, target):
            self.build = True
            return True
        else:
            return False


