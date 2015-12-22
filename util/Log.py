#!/usr/bin/env python
# -*- coding: utf-8 -*-  
################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
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
import traceback
import pprint
import Function

console_lock = threading.Lock()

def colorprint(color, msg, prefix=True):
    """
    print message with color
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
    print message with color
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


class Log(object):
    """
    Log class
    """
    def __init__(self, prefix=None):
        """
        Args:
            prefix : wether print time prefix in log message
        """
        self.prefix = prefix
        self.levMap = {"ERROR":(0, "\033[31m%s%s\033[0m"), "WARNING":(1, "\033[33m%s%s\033[0m"), \
                        "INFO":(2, "\033[34m%s%s\033[0m"), "MSG":(3, "\033[32m%s%s\033[0m"), \
                        "UNKNOW":(4, "\033[31m%s%s\033[0m")}
        self.config_level = 5

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

    def LevPrint(self, level, msg, prefix=True):
        """
        Description :  print log message which has higher level than config level
        Args: 
            level : ["ERROR", "WARNING", "INFO", "MSG", "UNKNOW"]
            msg : string, log message
            prefix : True , print time information
                     False , don't print time information
        Return : None
        """
        if level in self.levMap and self.levMap[level][0] > self.config_level:
            return 

        now = ""
        pmsg = ""
        if prefix:
            now = "[" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) \
                + " " + str(threading.current_thread().ident) + "] "
        if (level in self.levMap):
                pmsg = self.levMap[level][1] % (now, msg)
        else:
                pmsg = "UNKNOW log level(%s)" % level 
                pmsg += self.levMap["UNKNOW"][1] % (now, msg)
            
        print(pmsg)
        sys.stdout.flush()
