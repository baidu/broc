#!/usr/bin/env python
# !/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Authors: zhousongsong(doublesongsong@gmail.com)
Date:    2015/09/09 17:23:06
"""
import os
import shutil
import hashlib
import subprocess

# for target's naming 
DIGITS = [str(x) for x in xrange(0, 10)] 
ALPHABETS = []
ALPHABETS.extend(DIGITS)
ALPHABETS.extend([chr(x) for x in xrange(97, 123)])
ALPHABETS.append("_")
ALPHABETS.extend([chr(x) for x in xrange(65, 91)])

def CheckName(v):
    """
    do name's validity check
    Only Alphabets, Digits and Undersores are permitted
    Name cannot start with a digit, and  Upper case and low case letters are distinct
    Args:
        v, a string object
    Return:
        True if name is valid,otherwise False
    """
    if not isinstance(v, str) or v[0] in DIGITS:
        return False

    for c in v:
        if c not in ALPHABETS:
            return False

    return True 


def DelFiles(path):
    """
    rm files or directories
    """
    try:
        if os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except BaseException:
        pass


def MoveFiles(src, dst):
    """
    move file or directory src to dst
    Args:
        src : the source files or directory
        dst : the destination
    Returns:
        return (True, '') if move successfully
        return (False, error msg) if move failed
    """
    try:
        shutil.move(src, dst)
    except BaseException as err:
        return (False, err)

    return (True, '')


def Mkdir(target_dir):
    """
    try to create a directory
    """
    if os.path.exists(target_dir):
        return True
    try:
        os.makedirs(target_dir)
    except BaseException:
        pass
    # check again after mkdir
    if os.path.exists(target_dir):
        return True
    else:
        return False


def CalcMd5(data):
    """
    calculate the md5 of data
    Args: 
        data : the data to calculate
    Returns:
        return md5 of data, if fail to calculate return None 
    """
    try:
        md5 = hashlib.md5()
        md5.update(data)
        return md5.hexdigest()
    except BaseException:
        return None


def GetFileMd5(path):
    """
    calculate the md5 of file
    Args: 
        path : the path of file to calculate
    Return:
        return md5 of file, if fail to calculate return None
    """
    try:
        if not os.path.exists(path):
            return None

        h = open(path, "rb")
        data = h.read()
        h.close()
        return CalcMd5(data)
    except BaseException:
        return None


def RunCommand(cmd, ignore_stderr_when_ok=False):
    """
    run shell command in subprocess
    Args: 
        cmd : shell command
        ignore_stderr_when_ok : when ignore_stderr_when_ok is True, 
                                ignoring the msg from stderr if run successfully
    Return : 
        (shell_cmd_retcode, shell_cmd_msg)
        (-1, shell_cmd_msg) or (0, shell_cmd_msg)
    """
    try:
        if not ignore_stderr_when_ok:
            # stdout and stderr mix together, t.communicate() return the first one
            t = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 shell=True
                                )
        else:
            t = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True
                                )
        msg, err = t.communicate()
        retcode = t.wait()
        if retcode != 0 and ignore_stderr_when_ok:
            msg += '\n' + str(err)
    except BaseException as e:
        retcode = -1
        msg = 'run_shell_cmd_in_subprocess Exception for %s: %s' % (str(cmd), e)

    return (retcode, msg)


def RunCommand_tty(cmd):
    """
    run shell command in tty 
    Args:
        cmd : shell command
    Returns:
        return True if run successfully, otherwise return False
    """
    try:
        t = subprocess.Popen(cmd, shell=True)
        t.communicate()
        if t.wait() == 0:
            return True
        return False
    except BaseException as e:
        # TO FIX ME
        print "run %s error" % str(e)
        return False
