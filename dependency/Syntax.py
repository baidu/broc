#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module manages the Syntax used in BROC file

Authors: zhousongsong(doublesongsong@gmail.com)
Date:    2015/09/15 10:30:02
"""

import os
import sys
import string
import glob
import traceback
import tempfile
import Queue

broc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_path)

from dependency import SyntaxTag
from dependency import Environment
from dependency import Source
from dependency import Target
from dependency import PlanishUtil
from dependency import BrocTree
from dependency import BrocConfig
from dependency import BrocModule_pb2
from util import Function
from util import Log

class NotInSelfModuleError(Exception):
    """
    In Broc file, if files or directories users specify don't belongs to module itself
    raise NotInSelfModuleError
    """
    def __init__(self, _input, _dir):
        """
        Args:
            _input : the file or directory beneathes directory _dir
            _dir : the directory path
        """
        Exception.__init__(self)
        self._input = _input
        self._dir = _dir

    def __str__(self):
        """
        """
        return "couldn't find (%s) in (%s)" % (self._input, self._dir)


class BrocArgumentIllegalError(Exception):
    """
    when arguments in Broc are illegal, raise BrocArgumentIllegalError
    """
    def __init__(self, msg):
        """
        Args:
            msg : error info
        """
        Exception.__init__(self)
        self._msg = msg

    def __str__(self):
        """
        """
        return self._msg


class BrocProtoError(Exception):
    """
    when handle proto file failed, raise BrocProtoError
    """
    def __init__(self, msg):
        """
        Args:
            msg : error info
        """
        Exception.__init__(self)
        self._msg = msg

    def __str__(self):
        """
        """
        return self._msg


def COMPILER_PATH(k):
    """
    set global path of compiler's directory
    influence main moudle and all dependent modules
    Args:
        k : string object, compiler's directory, for example: if you set k as '/usr/bin',
            we should find 'gcc' and 'g++' in directory /usr/bin
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    env.SetCompilerDir(k)


def CPPFLAGS(d_flags, r_flags):
    """
    set module's global preprocess flags
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    # default build mode is debug, it can be modified by command 'broc' by user
    if env.BuildMode() == "debug":
        env.CppFlags().AddSV(d_flags)
    else:
        env.CppFlags().AddSV(r_flags)


def CppFlags(d_flags, r_flags):
    """
    set local prrprocess flags, override the global CPPFLAGS
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    tag = SyntaxTag.TagCppFlags()
    # default build mode is debug, it can be modified by command 'broc' by user
    if env.BuildMode() == "debug":
        tag.AddSV(d_flags)
    else:
        tag.AddSV(r_flags)
    return tag


def CFLAGS(d_flags, r_flags):
    """
    set the global compile options for c files,
    this influences the all of c files in module
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    # default build mode is debug, it can be modified by command 'broc' by user
    if env.BuildMode() == "debug":
        env.CFlags().AddSV(d_flags)
    else:
        env.CFlags().AddSV(r_flags)


def CFlags(d_flags, r_flags):
    """
    set the local compile options for c files,
    this influences the all of c files in target tag
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    tag = SyntaxTag.TagCFlags()
    if sys.argv[0] == 'PLANISH':
        return tag
    env = Environment.GetCurrent()
    tag = SyntaxTag.TagCFlags()
    if env.BuildMode() == "debug":
        tag.AddSV(d_flags)
    else:
        tag.AddSV(r_flags)
    return tag


def CXXFLAGS(d_flags, r_flags):
    """
    set the global compile options for c++ files,
    this influences the all of cxx files in module
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    if sys.argv[0] == 'PLANISH':
        return

    env = Environment.GetCurrent()
    if env.BuildMode() == "debug":
        env.CxxFlags().AddSV(d_flags)
    else:
        env.CxxFlags().AddSV(r_flags)


def CxxFlags(d_flags, r_flags):
    """
    set the local compile option for cxx files,
    this influences the all of cxx files in target tag
    Args:
       d_flags : debug mode preprocess flags
       r_flags : release mode preprocess flags
    """
    tag = SyntaxTag.TagCxxFlags()
    if sys.argv[0] == 'PLANISH':
        return tag
    env = Environment.GetCurrent()
    if env.BuildMode() == "debug":
        tag.AddSV(d_flags)
    else:
        tag.AddSV(r_flags)
    return tag


def CONVERT_OUT(s):
    """
    convert a directory of module into a reponsed output directory
    if s doesn't beneath the module, raise NotInSelfModuleError
    Args:
        s : a relative directory beneathed the module
    Returns:
        return the relative path of responsed output directory
    """
    if sys.argv[0] == 'PLANISH':
        return ""
    env = Environment.GetCurrent()
    _s = os.path.normpath(os.path.join(env.BrocDir(), s))
    # to check whether _s beneathes directory of module
    if env.ModulePath() not in _s:
        raise NotInSelfModuleError(env.BrocDir(), _s)
    return os.path.normpath(os.path.join('broc_out', env.BrocCVSDir(), s))


def INCLUDE(*ss):
    """
    set the global head file search path
    Default head files search path includes $WORKSPACE and $OUT_ROOT
    Args:
       ss : a variable number of string objects
            ss may contain multiple string objects, each object can contain multiple paths
            1. if path does not beneath module, in other words, if user want to specified other modules' path,  should start with $WORKSPACE,
            2. if path couldn't be founed in module itself and path does not start with $WORKSPACE rasie NotInSelfModuleError
            3. if path is output directory, it must start with 'broc_out/'
            for example: ss can be "./include ./include/foo", "$WORKSPACE/include", "broc_out/test/include"
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    tag = env.IncludePaths()
    broc_dir = env.BrocDir()
    for s in ss:
        ps = s.split()
        for x in ps:
            if x.startswith("$WORKSPACE"):
                tag.AddSV(x.replace("$WORKSPACE/", ''))
                continue
            elif x.startswith("broc_out/") or os.path.isabs(x):
                tag.AddSV(x)
                continue
            elif x.startswith("$OUT_ROOT"):
                tag.AddSV(x.replace("$OUT_ROOT", 'broc_out'))
                continue
            elif x.startswith("$OUT"):
                out = os.path.join('broc_out', env.ModuleCVSPath(), 'output')
                tag.AddSV(x.replace("$OUT", out))
            else:
                _x = os.path.normpath(os.path.join(broc_dir, x))
                if env.ModulePath() not in _x:
                    raise NotInSelfModuleError(_x, env.ModulePath())
                else:
                    tag.AddSV(_x)


def Include(*ss):
    """
    set the local file search path
    Args:
       ss : a variable number of string objects
            ss may contain multiple string objects, each object can contain multiple paths
            1. if path does not beneath module, in other words, if user want to specified other modules' path,  should start with $WORKSPACE,
            2. if path couldn't be founed in module itself and path does not start with $WORKSPACE rasie NotInSelfModuleError
            3. if path is output directory, it must start with 'broc_out/'
            for example: ss can be "./include ./include/foo", "$WORKSPACE/include", "broc_out/test/include"
    """
    tag = SyntaxTag.TagInclude()
    if sys.argv[0] == 'PLANISH':
        return tag
    env = Environment.GetCurrent()
    broc_abs_dir = env.BrocDir()
    broc_cvs_dir = env.BrocCVSDir()
    for s in ss:
        ps = string.split(s)
        for x in ps:
            if x.startswith("$WORKSPACE"):
                tag.AddSV(x.replace("$WORKSPACE/", ""))
                continue
            elif x.startswith('broc_out') or os.path.isabs(x):
                tag.AddSV(x)
                continue
            elif x.startswith("$OUT_ROOT"):
                tag.AddSV(x.replace("$OUT_ROOT/", 'broc_out'))
                continue
            elif x.startswith("$OUT"):
                out = os.path.join('broc_out', env.ModuleCVSPath(), 'output')
                tag.AddSV(x.replace("$OUT", out))
                continue
            else:
                _x = os.path.normpath(os.path.join(broc_abs_dir, x))
                if env.ModulePath() not in _x:
                    raise NotInSelfModuleError(_x, env.ModulePath())
                else:
                    tag.AddSV(os.path.normpath(os.path.join(broc_cvs_dir, x)))
    return tag


def Libs(*ss):
    """
    add .a files to target tag, such as APPLICATION, UT_APPLICATION, STATIC_LIBRARY
    ss may contain multiple arguments, each argument can contain muitiple lib's path,
    each lib's path should start with $OUT_ROOT
    for example Libs("$ROOT_OUT/test/output/lib/libutil.a", "$ROOT_OUT/foo/output/lib/libcommon.a")
    Args:
        ss : a variable number of string objects
    Returns:
        SyntaxTag.TagLibs()
    """
    tag = SyntaxTag.TagLibs()
    if sys.argv[0] == 'PLANISH':
        return tag
    for s in ss:
        if not isinstance(s, str):
            raise BrocArgumentIllegalError("argument %s is illegal in tag Libs" % s)
        if os.path.isabs(s):
            tag.AddSV(s)
            continue
        elif s.startswith("$OUT_ROOT"):
            tag.AddSV(os.path.normpath(s.replace("$OUT_ROOT", "broc_out")))
            continue
        elif s.startswith('$WORKSPACE'):
            tag.AddSV(os.path.normpath(s.replace("$WORKSPACE/", "")))
            continue
        elif s.startswith("$OUT"):
            env = Environment.GetCurrent()
            out = os.path.join('broc_out', env.ModuleCVSPath(), 'output')
            tag.AddSV(os.path.normpath(s.replace("$OUT", out)))
            continue
        else:
            raise BrocArgumentIllegalError("args(%s) should be a abs path or startswith $WORKSPACE|$OUT|$OUT_ROOT in tag Libs" % s)

    return tag


def LDFLAGS(d_flags, r_flags):
    """
    add global link flags
    Args:
        d_flags : link flags in debug mode
        r_flags : link flags in release mode
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    if env.BuildMode() == "debug":
        env.LDFlags().AddSV(d_flags)
    else:
        env.LDFlags().AddSV(r_flags)


def LDFlags(d_flags, r_flags):
    """
    add local link flags
    Args:
        d_flags : link flags in debug mode
        r_flags : link flags in release mode
    """
    tag = SyntaxTag.TagLDFlags()
    if sys.argv[0] == 'PLANISH':
        return tag
    env = Environment.GetCurrent()
    if env.BuildMode() == "debug":
        tag.AddSV(d_flags)
    else:
        tag.AddSV(r_flags)
    return tag


def GLOB(*ss):
    """
    gather all files belonging to module, if argument specified in ss does not beneath
    the directory of module, raise BrocArgumentIllegalError
    Args:
        ss : a variable number of string objects, support regrex
    Returns:
        string containing the relative path of files or directories, each path separeated by blank character
    """
    if sys.argv[0] == 'PLANISH':
        return ""
    env = Environment.GetCurrent()
    strs=[]
    for s in ss:
        ps = string.split(s)
        for p in ps:
            if p.startswith(os.path.join("broc_out", env.ModuleCVSPath())):
                norm_path = os.path.normpath(os.path.join(env.Workspace(), p))
                len_abandon = len(os.path.normpath(env.Workspace()))
            else:
                norm_path = os.path.normpath(os.path.join(env.BrocDir(), p))
                len_abandon = len(os.path.normpath(env.BrocDir()))
            if env.ModuleCVSPath() not in norm_path:
                raise NotInSelfModuleError(norm_path, env.ModuleCVSPath())
            else:
                gs = glob.glob(norm_path)
                gs.sort()
                file_list = list()
                for file_name in gs:
                    # remove workspace path from file path
                    file_list.append(file_name[len_abandon + 1:])
                strs.extend(file_list)
    if not strs:
        raise BrocArgumentIllegalError("GLOB(%s) is empty" % str(ss))

    return str(' '.join(strs))


def _ParseNameAndArgs(*ss):
    """
    parse a variable number of arguments, all string arguments in ss will be regarded as source file,
    and the rest of arguments will be regarded as compile options
    Args:
        ss : a variable number of arguments
    Return:
        a tuple object composed of two iterms: first one is a group of source files, and second are the TagVector objects
    """
    files = []
    args = []
    for s in ss:
        if isinstance(s, str) or isinstance(s, unicode):
            files.extend(string.split(string.strip(s)))
        else:
            args.append(s)
    return (files, args)


def CONFIGS(s):
    """
    gather dependency modules
    """
    if sys.argv[0] == 'PLANISH':
        broc_loader = BrocLoader()
        broc_loader.handle_configs(s.strip(), sys.argv[1])

def Sources(*ss):
    """
    create a group of Sources object
    all source file should beneathes the directory of module, if not will raise NotInSelfModuleError
    avoid containing wildcard in ss, so you can use GLOB gathering files firstly, and take the result of GLOB as ss
    Args:
        ss : a variable number of artuments, all string arguments in ss will be regarded as
             source file, the file can be .c, .cpp and so on, and the reset arguments are
             regarded as compile flags
    Returns:
        TagSources Object
    """
    tag = SyntaxTag.TagSources()
    if sys.argv[0] == 'PLANISH':
        return tag
    # FIX ME: you can extend wildcard
    files, args = _ParseNameAndArgs(*ss)
    env = Environment.GetCurrent()
    all_files = GLOB(" ".join(files)).split(' ')
    for f in all_files:
        if not f.startswith(os.path.join("broc_out", env.ModuleCVSPath())):
            f = os.path.join(os.path.dirname(env.BrocCVSPath()), f)
        src = _CreateSources(f, args)
        tag.AddSV(src)

    return tag


def _CreateSources(_file, *args):
    """
    create a Source object
    Args:
        _file : the cvs path of source code file
        _args : a variable number of TagVector object
    Return:
        the Source object
    """
    src = None
    env = Environment.GetCurrent()
    _, ext = os.path.splitext(_file)
    if ext in Source.CSource.EXTS:
        src = Source.CSource(_file, env, args)
    elif ext in Source.CXXSource.EXTS:
        src = Source.CXXSource(_file, env, args)
    else:
        raise BrocArgumentIllegalError("don't support file(%s) whose ext is(%s)" % (_file, ext))
    env.AppendSource(src)
    return src


def APPLICATION(name, sources, *args):
    """
    create one Application object
    Args:
        name : the name of target
        sources : the SyntaxTag.TagSource object
        args: a variable number of SyntaxTag.TagLDFlags and SyntaxTag.TagLibs
    """
    if sys.argv[0] == 'PLANISH':
        return
    # to check name of result file
    if not Function.CheckName(name):
        raise BrocArgumentIllegalError("name(%s) in APPLICATION is illegal" % name)

    tag_links = SyntaxTag.TagLDFlags()
    tag_libs = SyntaxTag.TagLibs()
    for arg in args:
        if isinstance(arg, SyntaxTag.TagLDFlags):
            tag_links.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagLibs):
            tag_libs.AddSVs(arg.V())
        else:
            raise BrocArgumentIllegalError("In APPLICATION(%s) don't support %s" % (name, arg))

    env = Environment.GetCurrent()
    app = Target.Application(name, env, sources, tag_links, tag_libs)
    if not env.AppendTarget(app):
        raise BrocArgumentIllegalError("APPLICATION(%s) exists already" % name)


def STATIC_LIBRARY(name, *args):
    """
    create one StaticLibrary object
    Args:
        name : the name of .a file
        args : the variable number of SyntagTag.TagSources, SyntaxTag.TagLibs object
    """
    if sys.argv[0] == 'PLANISH':
        return
    # to check name of result file
    if not Function.CheckName(name):
        raise BrocArgumentIllegalError("name(%s) in STATIC_LIBRARY is illegal" % name)

    tag_libs = SyntaxTag.TagLibs()
    tag_sources = SyntaxTag.TagSources()
    for arg in args:
        if isinstance(arg, SyntaxTag.TagSources):
            tag_sources.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagLibs):
            tag_libs.AddSVs(arg.V())
        else:
            raise BrocArgumentIllegalError("arguments (%s) in STATIC_LIBRARY is illegal" % \
                                          type(arg))
    env = Environment.GetCurrent()
    lib = Target.StaticLibrary(name, env, tag_sources, tag_libs)
    if len(tag_sources.V()):
        if not env.AppendTarget(lib):
            raise BrocArgumentIllegalError("STATIC_LIBRARY(%s) exists already" % name)
    else:
        # .a file has been built already, just copy it from code directory to output directory
        lib.DoCopy()


def UT_APPLICATION(name, sources, *args):
    """
    create one UT Application object
    Args:
        name : the name of target
        sources : the SyntaxTag.TagSource object
        args : a variable number of SyntaxTag.TagLinkLDFlags, SyntaxTag.TagLibs, SyntaxTag.TagUTArgs
    """
    if sys.argv[0] == 'PLANISH':
        return
    # to check name of result file
    if not Function.CheckName(name):
        raise BrocArgumentIllegalError("name(%s) in UT_APPLICATION is illegal")

    tag_links = SyntaxTag.TagLDFlags()
    tag_libs = SyntaxTag.TagLibs()
    tag_utargs = SyntaxTag.TagUTArgs()
    for arg in args:
        if isinstance(arg, SyntaxTag.TagLDFlags):
            tag_links.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagLibs):
            tag_libs.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagUTArgs):
            tag_utargs.AddSVs(arg.V())
        else:
            raise BrocArgumentIllegalError("In UT_APPLICATION(%s) don't support %s" % (name, arg))
    env = Environment.GetCurrent()
    app = Target.UTApplication(name, env, sources, tag_links, tag_libs, tag_utargs)
    if not env.AppendTarget(app):
        raise BrocArgumentIllegalError("UT_APPLICATION(%s) exists already" % name)


def ProtoFlags(*ss):
    """
    add the command options for protoc
    Args:
       ss : a variable number of string objects
            ss may contain multiple string objects, each object can contain multiple options
            one option may be:
            1. option may contains $WORKSPACE, $OUT Macros value
    Returns:
        return a
    """
    tag = SyntaxTag.TagProtoFlags()
    if sys.argv[0] == 'PLANISH':
        return tag
    env = Environment.GetCurrent()
    for s in ss:
        ps = s.split()
        for x in ps:
            if "$WORKSPACE" in x:
                tag.AddSV(x.replace("$WORKSPACE/", ''))
            elif "$OUT" in x:
                tag.AddSV(x.replace("$OUT", env.OutputPath()))
            elif "$OUT_ROOT" in x:
                tag.AddSV(x.replace("$OUT_ROOT", env.OutputRoot()))
            else:
                tag.AddSV(x)
    return tag


def PROTO_LIBRARY(name, files, *args):
    """
    compile proto files into a static library .a
    when parse proto files failed, raise Exception BrocProtoError
    Args:
        name: the name of proto static library
        files: a string sperearated by blank character, representing the relative path of proto files
        args: a variable number of SyntaxTag.TagProtoFlags, SyntaxTag.TagInclude, SyntaxTag.CppFlags, SyntaxTag.CXXFlags, SyntaxTag.TagLibs
    """
    if sys.argv[0] == 'PLANISH':
        return
    # check validity of name
    if not Function.CheckName(name):
        raise BrocArgumentIllegalError("name(%s) PROTO_LIBRARY is illegal" % name)

    # check proto file whether belongs to  module
    proto_files = files.split()
    env = Environment.GetCurrent()
    for _file in proto_files:
        abs_path = os.path.normpath(os.path.join(env.BrocDir(), _file))
        if not env.ModulePath() in abs_path:
            raise NotInSelfModuleError(abs_path, env.ModulePath())

    # to check args
    tag_protoflags = SyntaxTag.TagProtoFlags()
    tag_cppflags = SyntaxTag.TagCppFlags()
    tag_cxxflags = SyntaxTag.TagCxxFlags()
    tag_libs = SyntaxTag.TagLibs()
    tag_include = SyntaxTag.TagInclude()
    for arg in args:
        if isinstance(arg, SyntaxTag.TagProtoFlags):
            tag_protoflags.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagCppFlags):
            tag_cppflags.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagCxxFlags):
            tag_cxxflags.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagLibs):
            tag_libs.AddSVs(arg.V())
        elif isinstance(arg, SyntaxTag.TagInclude):
            tag_include.AddSVs(arg.V())
        else:
            raise BrocArgumentIllegalError("don't support tag(%s) in PROTO_LIBRARY in %s" \
                                             % (str(arg), env.BrocPath()))

    include = set()
    source = set()
    for f in proto_files:
        root, _ = os.path.splitext(f)
        result_file = os.path.join(os.path.join('broc_out', env.BrocCVSDir()), \
                "%s.pb.cc" % root)
        include.add(os.path.dirname(result_file))
        if os.path.dirname(f):
            tag_include.AddV(os.path.join(env.ModuleCVSPath(), os.path.dirname(f)))
        source.add(result_file)
    protolib = Target.ProtoLibrary(env, files, tag_include, tag_protoflags)
    ret, msg = protolib.PreAction()
    if not ret:
        raise BrocProtoError(msg)

    tag_include.AddSVs(include)
    broc_out = os.path.join("broc_out", env.BrocCVSDir())
    if broc_out not in tag_include.V():
        tag_include.AddV(os.path.join("broc_out", env.BrocCVSDir()))
    tag_sources = Sources(" ".join(list(source)), tag_include, tag_cppflags, tag_cxxflags)
    if not env.AppendTarget(Target.StaticLibrary(name, env, tag_sources, tag_libs)):
        raise BrocArgumentIllegalError("PROTO_LIBRARY(%s) name exists already" % name)
    return protolib


def UTArgs(v):
    """
    tag UTArgs
    """
    tag = SyntaxTag.TagUTArgs()
    if sys.argv[0] == 'PLANISH':
        return tag
    tag.AddV(v)
    return tag

def DIRECTORY(v):
    """
    Add sub directory
    Args:
       v : the name of subdirectory, v is relative path
    """
    # gather all dependent module
    env = Environment.GetCurrent()
    child_broc_dir = os.path.abspath(os.path.join(env.ModulePath(), v))
    if env.ModulePath() not in child_broc_dir:
            raise BrocArgumentIllegalError("DIRECTORY(%s) is wrong: %s not in %s" % \
                                          (child_broc_dir, env.ModulePath()))

    child_broc_file = os.path.join(parent.module.root_path, v, 'BROC')
    if sys.argv[0] == 'PLANISH':
        parent = sys.argv[1]
        if not os.path.exists(child_broc_file):
            raise BrocArgumentIllegalError('Not found %s in Tag Directory(%s)' % (child_broc_file, v))
        try:
            execfile(child_broc_file)
        except BaseException as err:
            traceback.print_exc()
            raise BrocArgumentIllegalError(err)
    else: # find all targets to build
        if not os.path.exists(child_broc_file):
            raise BrocArgumentIllegalError('Not found %s in Tag Directory(%s)' % (child_broc_file, v))
        # Log.Log().LevPrint("INFO", 'add sub directory (%s) for module %s' % (v, env._module.module_cvspath))
        env.AddSubDir(v)

def PUBLISH(srcs, out_dir):
    """
    copy srcs to out_dir
    Args:
        srcs: the files needed to move should belongs to the module
        out_dir: the destination directory that must start with $OUT
        if argument is illeagl, raise BrocArgumentIllegalError
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    if not out_dir.strip().startswith('$OUT'):
        raise BrocArgumentIllegalError("PUBLISH argument dst(%s) must start with $OUT \
                                         in %s " % (out_dir, env.BrocPath()))
    src_lists = srcs.split()
    for s in src_lists:
        abs_s = os.path.normpath(os.path.join(env.BrocDir(), s))
        if env.ModulePath() not in abs_s:
            raise NotInSelfModuleError(abs_s, env.ModulePath())

    env.AddPublish(srcs, out_dir)


def SVN_PATH():
    """
    return local path of module
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.SvnPath()


def SVN_URL():
    """
    return url of module
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.SvnUrl()


def SVN_REVISION():
    """
    return revision of module
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.SvnRevision()


def SVN_LAST_CHANGED_REV():
    """
    return last changed rev
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.SvnLastChangedRev()


def GIT_PATH():
    """
    return local path of module
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitPath()


def GIT_URL():
    """
    return url of module
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitUrl()


def GIT_BRANCH():
    """
    return the branch name of module
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitBranch()


def GIT_COMMIT_ID():
    """
    return the commit id of module
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitCommitID()


def GIT_TAG():
    """
    return the tag of module
    """
    if sys.argv[0] == 'PLANISH':
        return
    env = Environment.GetCurrent()
    return env.GitTag()

class BrocLoader(object):
    """
    the class loading BROC file
    """
    class __impl(object):
        """
        the implementation of singleton interface
        """
        def __init__(self):
            """
            """
            self._root = None
            self._nodes = dict()                   # module
            self._checked_configs = set()          # storing content of tag CONFIGS
            self._broc_dir = tempfile.mkdtemp()    # the temporary directory storing all BROC files
            self._queue = Queue.Queue()
            self._lack_broc = set()                # the set of module who lack BROC file

        def Id(self):
            """
            test method, return singleton id
            """
            return id(self)

        def SetRoot(self, root):
            """
            Args:
                root : the BrocNode object
            """
            if not self._root:
                self._root = root
                BrocTree.BrocTree().SetRoot(root)
                self._queue.put(root)

        def AddNode(self, node):
            """
            add new node
            Args:
                node : the object of BrocNode
            """
            if node.module.module_cvspath not in self._nodes:
                self._nodes[node.module.module_cvspath] = []

            self._nodes[node.module.module_cvspath].append(node)

        def AllNodes(self):
            """
            """
            return self._nodes

        def LackBrocModules(self):
            """
            return the set object containing the modules that lack BROC file
            """
            return self._lack_broc

        def LoadBROC(self):
            """
            to run main module BROC file
            """
            # main thread to load BROC
            # first node is root node representing main module
            while not self._queue.empty():
                parent = self._queue.get()
                sys.argv = ['PLANISH', parent]
                broc_file = self._download_broc(parent)
                if not broc_file:
                    self._lack_broc.add(parent.module.origin_config)
                    continue
                try:
                    execfile(broc_file)
                except BaseException as err:
                    traceback.print_exc()
            # print dependent tree
            BrocTree.BrocTree().Dump()

        def handle_configs(self, s, parent):
            """
            Args:
                s : xx@xx@xx set at tag CONFIGS
                parent : the BrocNode object
            """
            if s in self._checked_configs:
                return
            tree = BrocTree.BrocTree()
            repo_domain = BrocConfig.BrocConfig().RepoDomain(parent.module.repo_kind)
            postfix_branch = BrocConfig.BrocConfig().SVNPostfixBranch()
            postfix_tag = BrocConfig.BrocConfig().SVNPostfixTag()
            child_module = PlanishUtil.ParseConfig(s,
                                           parent.module.workspace,
                                           parent.module.dep_level + 1,
                                           parent.module.repo_kind,
                                           repo_domain,
                                           postfix_branch,
                                           postfix_tag)
            # Log.Log().LevPrint("MSG", 'create node(%s), level %d' % (s, child_module.dep_level))
            child_node = BrocTree.BrocNode(child_module, parent, False)
            parent.AddChild(child_node)
            self.AddNode(child_node)
            self._queue.put(child_node)
            self._checked_configs.add(s)

        def _download_broc(self, node):
            """
            download BROC file from repository
            Args:
                node : the BrocNode object
            Returns:
                return abs path of BROC file if download success
                return None if download failed
            """
            broc_path = None
            cmd = None
            # for svn
            # Log.Log().LevPrint("MSG", 'download BROC %s' % node.module.url)
            if node.module.repo_kind == BrocModule_pb2.Module.SVN:
                hash_value = Function.CalcHash(node.module.url)
                broc_url = os.path.join(node.module.url, 'BROC')
                broc_path = os.path.join(self._broc_dir, "%s_BROC" % hash_value)
                if node.module.revision:
                    broc_url = "%s -r %s" % (broc_url, node.module.revision)
                cmd = "svn export %s %s" % (broc_url, broc_path)
            else:
                # for GIT
                cmd = ""
                broc_path = os.path.join(node.module.workspace, node.module.module_cvspath, 'BROC')
                broc_dir = os.path.dirname(broc_path)
                if not os.path.exists(broc_path):
                    cmd += "git clone %s %s" \
                          % ("%s.git" % node.module.url, "%s" % broc_dir)

                    if node.module.br_name and node.module.br_name != 'master':
                        br_name = node.module.br_name
                        cmd += " && cd %s && (git checkout %s || (git fetch origin %s:%s && git checkout %s))" \
                               % (broc_dir, br_name, br_name, br_name, br_name)
                    elif node.module.tag_name:
                        tag_name = node.module.tag_name
                        cmd += " && cd %s && (git checkout %s || (git fetch origin %s:%s && git checkout %s))" \
                               % (broc_dir, tag_name, tag_name, tag_name, tag_name)

            if cmd:
                Log.Log().LevPrint("MSG", "Getting BROC(%s) ..." % cmd)
                ret, msg = Function.RunCommand(cmd)
                if ret != 0:
                    Log.Log().LevPrint("ERROR", msg)
                    return None

            return broc_path

    # class BrocLoader
    __instance = None
    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if BrocLoader.__instance is None:
            # Create and remember instance
            BrocLoader.__instance = BrocLoader.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_BrocLoader__instance'] = BrocLoader.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
