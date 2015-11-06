#!/usr/bin/env python
# -*- coding: utf-8 -*-  
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provide some log function.

Authors: zhousongsong(zhousongsong@baidu.com)
         liruihao(liruihao@baidu.com)
Date:    2015/09/09 15:48:35
"""

import os
import sys
import time
import threading
import pprint
import traceback
import Function

if __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = __file__[:-4] + '.py'
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)

console_lock = threading.Lock()

def currentframe():
    """
    Description : Return the frame object for the caller's stack frame.
    Args : NULL
    Return : stack frame
    """
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back


def colorprint(color, msg, prefix=True):
    """
    Description : color print a msg.
    Args : color : ["RED", "GREEN", "YELLOW", "BLUE"]
           msg : message to print
           prefix : True -> add time information before msg
                    False -> don't add time information
    Return : NULL
    """
    if prefix:
        now = "[" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) \
            + " " + str(threading.current_thread().ident) + "] "
    else:
        now = ""
    global console_lock
    console_lock.acquire()
    try:
        if color == "RED":
            if (sys.__stdout__.isatty()):
                print "\033[31m%s%s\033[0m" % (now, msg)
            else:
                print "%s%s" % (now, msg)
            sys.stdout.flush()
            return

        if color == "GREEN":
            if (sys.__stdout__.isatty()):
                print "\033[32m%s%s\033[0m" % (now, msg)
            else:
                print "%s%s" % (now, msg)
            sys.stdout.flush()
            return

        if color == "YELLOW":
            if (sys.__stdout__.isatty()):
                print "\033[33m%s%s\033[0m" % (now, msg)
            else:
                print "%s%s" % (now, msg)
            sys.stdout.flush()
            return

        if color == "BLUE":
            if (sys.__stdout__.isatty()):
                print "\033[34m%s%s\033[0m" % (now, msg)
            else:
                print "%s%s" % (now, msg)
            sys.stdout.flush()
            return

        print "%s%s" % (now, msg)
        sys.stdout.flush()
    finally:
        console_lock.release()


def colorpprint(color, obj):
    """
    Description : color print an object.
    Args : color : ["RED", "GREEN", "YELLOW", "BLUE"]
           obj : object to print
    Return : NULL
    """
    global console_lock
    console_lock.acquire()
    try:
        if color == "RED":
            print "\033[31m"
            pprint.pprint(obj)
            print "\033[0m"
            sys.stdout.flush()
            return

        if color == "GREEN":
            print "\033[32m"
            pprint.pprint(obj)
            print "\033[0m"
            sys.stdout.flush()
            return

        if color == "YELLOW":
            print "\033[33m"
            pprint.pprint(obj)
            print "\033[0m"
            sys.stdout.flush()
            return

        if color == "BLUE":
            print "\033[34m"
            pprint.pprint(obj)
            print "\033[0m"
            sys.stdout.flush()
            return

        pprint.pprint(obj)
        sys.stdout.flush()
    finally:
        console_lock.release()

#log file handles
g_log_handles = dict()
    

def _getCurFile(base_fname):
    """
    Description : get current log file handle
    Args : base_fname : log file name
    Return : log file handle
    """
    global g_log_handles
    if threading.current_thread().ident not in g_log_handles:
        g_log_handles[threading.current_thread().ident] = dict()
    if base_fname not in g_log_handles[threading.current_thread().ident]:
        g_log_handles[threading.current_thread().ident][base_fname] = None
    return g_log_handles[threading.current_thread().ident][base_fname]


def _setCurFile(base_fname, fname):
    """
    Description : set log file handles
    Args : base_fname : log file name
           fname : base_fname + timestamp
    Return : NULL : success
             None : fail
    """
    global g_log_handles
    if threading.current_thread().ident not in g_log_handles:
        g_log_handles[threading.current_thread().ident] = dict()
    if base_fname not in g_log_handles[threading.current_thread().ident] or \
        g_log_handles[threading.current_thread().ident][base_fname] is None:
        try:
            g_log_handles[threading.current_thread().ident][base_fname] = file(fname, "a")
            return
        except BaseException as e:
            traceback.print_exc()
            print "_setCurFile exception %s" % str(e)
            return None
    else:
        if g_log_handles[threading.current_thread().ident][base_fname].name != fname:
            g_log_handles[threading.current_thread().ident][base_fname].close()
            try:
                g_log_handles[threading.current_thread().ident][base_fname] = file(fname, "a") 
            except BaseException as e:
                traceback.print_exc()
                print "_setCurFile exception %s" % str(e)
                return None


class Log(object):
    """
    Log class
    """
    def __init__(self, logfile=None, prefix=None):
        self.logfile_base = logfile
        if self.logfile_base:
            Function.Mkdir(os.path.dirname(self.logfile_base))
        self.logfile = ""
        self.prefix = prefix
        self._setupLogFile()
        self.levMap = {"ERROR":(0, "\033[31m%s%s\033[0m"), "WARNING":(1, "\033[33m%s%s\033[0m"), \
                        "INFO":(2, "\033[34m%s%s\033[0m"), "MSG":(3, "\033[32m%s%s\033[0m"), \
                        "UNKNOW":(4, "\033[31m%s%s\033[0m")}
        #默认显示所有级别的log
        self.config_level = 5

    def _setupLogFile(self):
        """
        Description : setup log file
        Args : NULL
        Return : NULL
        """
        if self.logfile_base is not None:
            fname = self.logfile_base + time.strftime("_%Y%m%d")
            try:
                if _getCurFile(fname) is None:
                    _setCurFile(self.logfile_base, fname)
                    #TODO:lock?
                    self.logfile = fname
                    return

                if not os.path.exists(fname):
                    print "new file"
                    _setCurFile(self.logfile_base, fname)
                    #TODO:lock?
                    self.logfile = fname
            except BaseException as e:
                print "_setupLogFile fail", str(e)
                sys.stdout.flush()

    def getLogFname(self):
        """
        Description : get log file name
        Args : NULL
        Return : log file name
        """
        return self.logfile

    def writeFile(self, msg):
        """
        Description : write message to log file
        Args : msg : message write to log file
        Return : NULL
        """
        self._setupLogFile()
        fobj = _getCurFile(self.logfile_base)
        fobj.write(msg.encode('utf-8', 'ignore'))
        fobj.write("\n")
        fobj.flush()

    def setLogLevel(self, lev):
        """
        Description : set log file level.The log message lower than this level will not be printed.
        Args : lev : log level will be set.Value is [0-5],0 will not print any log message, 5 will print all log message
        Return : NULL 
        """
        self.config_level = lev

    def setPrefix(self, prefix):
        """
        Description : set log message prefix
        Args : prefix : log message prefix
        Return : NULL
        """
        self.prefix = prefix

    def findCaller(self):
        """
        Description : Find the stack frame of the caller so that we can note the source
                      file name, line number and function name.
        Args : NULL
        Return : (file_name, line_num, function_name) 
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (os.path.basename(co.co_filename), f.f_lineno, co.co_name)
            break
        return rv

    def Print(self, msg):
        """
        Description : Print msg in log file
        Args : msg : message you want to print
        Return : NULL
        """
        try:
            fn, lno, func = self.findCaller()
        except ValueError:
            fn, lno, func = ("unknown file"), 0, "(unknown function)"

        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        tid = str(threading.current_thread().ident)
        if self.prefix is not None:
            msg = "[%s|%s|%s|%s|%d] %s" % (self.prefix, now, tid, fn, lno, msg)
        else:
            msg = "[%s|%s|%s|%d] %s" % (now, tid, fn, lno, msg)

        try:
            if self.logfile_base is not None:
                self.writeFile(msg)
            else:
                print(msg)
                sys.stdout.flush()
        except BaseException as e:
            print(str(e))
            print(traceback.format_exc())
            sys.stdout.flush()
            print(msg)
            sys.stdout.flush()

    def LevPrint(self, level, msg, prefix=True):
        """
        Description :  print log message which has higher level than config level
        Args : level : ["ERROR", "WARNING", "INFO", "MSG", "UNKNOW"]
               msg : string, log message
               prefix : True , print time information
                        False , don't print time information
        Return : None
        """
        if (level in self.levMap) and (self.levMap[level][0] > self.config_level):
            return 

        if prefix:
            now = "[" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) \
                + " " + str(threading.current_thread().ident) + "] "
        else:
            now = ""
        pmsg = ""
        if (level in self.levMap):
            if (self.logfile_base is None):
                pmsg = self.levMap[level][1] % (now, msg)
            else:
                pmsg =  "%s[%s] %s" % (now, level, msg)
        else:
            if (self.logfile_base is None):
                pmsg = "UNKNOW log level(%s)" % level 
                pmsg += self.levMap["UNKNOW"][1] % (now, msg)
            else:
                pmsg = "UNKNOW log level(%s) %s%s" % (level, now, msg) 
            
        try:
            if self.logfile_base is not None:
                self.writeFile(pmsg)
            else:
                print(pmsg)
                sys.stdout.flush()
        except BaseException as e:
            print str(e)
            print(pmsg)
            sys.stdout.flush()
