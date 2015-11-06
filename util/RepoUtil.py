#!/usr/bin/env python
# -*- coding: utf-8 -*-  

################################################################################
#
# Copyright (c) 2015 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Description : svn and git basic functions
Authors     : zhongsongsong(zhousongsong@baidu.com)
              liruihao(liruihao@baidu.com)
Date        : 2015-09-22 12:29:51
"""
import os
import re
import xml.dom.minidom

import Function
import Log

def GetSvnRoot(target_dir, logger):
    """
    find svn root directory in module's code directory
    svn root directory is a directory that containing a .svn subdirectory 
    but its parent directory dones not contain
    Args: 
        target_dir : the path of code directory
        logger : the object of Log.Log()
    Returns: 
        return the svn root directory
        return None if not find
    """
    root_dir = os.path.realpath(target_dir)
    if root_dir.endswith('/'):
        root_dir = root_dir[:-1]
    while root_dir and root_dir != '/':
        if os.path.isdir(os.path.join(root_dir, '.svn')) and \
                not os.path.isdir(os.path.join(os.path.dirname(root_dir), '.svn')):
            break
        root_dir = os.path.dirname(root_dir)
    if not root_dir or root_dir == '/': 
        logger.LevPrint("ERROR", \
                "Can't find the file '.svn' in %s or any upper directory." % (target_dir), False)
        return None

    return root_dir


def GetGitRoot(target_dir, logger):
    """
    find git root directory of module's code directory
    git root directory is a directory that including a .git subdirectory 
    but its parent directory does not include the .git subdirectory
    Args: 
        target_dir : the abs path of directory
        logger : the object of Log.Log()
    Returns: 
        return the git root directory
        return None if not find
    """
    root_dir = os.path.realpath(target_dir)
    if root_dir.endswith('/'):
        root_dir = root_dir[:-1]
    while root_dir and root_dir != '/':
        if os.path.isdir(os.path.join(root_dir, '.git')) and \
                not os.path.isdir(os.path.join(os.path.dirname(root_dir), '.git')):
            break
        root_dir = os.path.dirname(root_dir)
    if not root_dir or root_dir == '/':
        logger.LevPrint("ERROR", \
                "Can't find the file '.git' in %s or any upper directory" % target_dir, False)
        return None

    return root_dir


def IsUnderSvnControl(target_dir):
    """
    to check whether a directory is a svn working copy
    Args : 
        target_dir : the abs path of directory
    Returns: 
        True : target path is svn working copy
        False : target path is not svn working copy
    """
    cmd = 'cd %s && svn info' % (target_dir)
    (status, msg) = Function.RunCommand(cmd)
    if status != 0:
        return False
    else:
        return True
    

def IsUnderGitControl(target_dir):
    """
    check a directory is a git woring copy or not
    Args :
        target_dir : abs directory path
    Returns :
        True : target path is git working copy
        False : target path is not git working copy
    """
    cmd = 'cd %s && git status' % (target_dir)
    (status, msg) = Function.RunCommand(cmd)
    if status != 0:
        return False
    else:
        return True


def GetSvnDiffFiles(target_dir, logger):
    """
    get diff files in a directory that is under control of svn 
    Args:
        target_dir : the abs path of directory
        logger : the object of Log.Log()
    Returns : 
        return a dict object containing the changed file 
        result = dict()
        result['has_diff'] = True or False
        result['add_list'] = list()
        result['del_list'] = list()
        result['unsvn_list'] = list()   
    """
    result = dict()
    result['has_diff'] = False 
    result['add_list'] = list()
    result['del_list'] = list()
    result['unsvn_list'] = list()

    if not target_dir:
        target_dir = "."

    command = "svn status --xml --non-interactive %s " % target_dir
    (status, msg) = Function.RunCommand(command)
    if status != 0:
        logger.LevPrint("ERROR", "Get svn stat failed: %s" % msg, False)
        return result

    try: 
        dom = xml.dom.minidom.parseString(msg)
        entries = dom.getElementsByTagName('entry')
        for entry in entries:
            # path = entry.getAttribute('path')
            item = entry.getElementsByTagName('wc-status')[0].getAttribute('item')
            if item == "unversioned":
                result['unsvn_list'].append(target_dir)
            elif item == "added" or item == "modified":
                result['add_list'].append(target_dir)
            elif item == "deleted":
                result['del_list'].append(target_dir)

        if result['add_list']  or result['del_list']:
            result['has_diff'] = True
    except BaseException as ex:
        logger.LevPrint("ERROR", "get svn diff files error: %s" % (ex), False)
        return result

    version = GetSvnLastChangeRev(target_dir, logger)
    command = "svn diff --diff-cmd /usr/bin/diff -r%s %s" % (version, target_dir)
    (status, msg) = Function.RunCommand(command)
    for line in re.split("\n", msg):
        if not line.startswith("Index: "):
            continue
        column = re.split(": ", line)
        if len(column) != 2:
            continue
        if os.path.exists(column[1]):
            if column[1] not in result["add_list"]:
                result["add_list"].append(column[1])
                result['has_diff'] = True
        else:
            if column[1] not in result["del_list"]:
                result["del_list"].append(column[1])
                result['has_diff'] = True

    return result


def GetGitDiffFiles(git_dir, logger):
    """
    get diff files in a directory that is under contorl of git
    Args:
        git_dir : the abs directory path
        logger : the object of Log.Log()
    Returns :
        return a dict object containing the changed file
        result = dict()
        result['has_diff'] = True or False
        result['add_list'] = list()
        result['del_list'] = list()
        result['unsvn_list'] = list()
    """
    result = dict()
    result['has_diff'] = False
    result['add_list'] = list()
    result['del_list'] = list()
    result['unsvn_list'] = list()
    
    try:
        cmd = 'cd %s && git status --short' % (git_dir)
        (status, msg) = Function.RunCommand(cmd, ignore_stderr_when_ok=True)
        if status != 0:
            logger.LevPrint("ERROR", "run command %s error!" % (cmd), False)
            return None

        file_list = msg.split('\n')
        for file_stat in file_list:
            tmp_list = file_stat.split()
            if len(tmp_list) <= 1:
                continue
            file_status = tmp_list[0]
            file_name = tmp_list[-1]
            if file_status == 'M':
                result['add_list'].append(file_name)
                result['has_diff'] = True
            elif file_status == "D":
                result['del_list'].append(file_name)
                result['has_diff'] = True
            else:
                result['unsvn_list'].append(file_name)
    except BaseException as ex:
        logger.LevPrint("ERROR", "get git diff file error, ex : %s!" % (str(ex)), False)
        return None
    result['result'] = 0
    return result


def _get_svn_xml(target_dir, logger):
    """
    get svn info in xml format
    Args: 
        target_dir : the abs path of a directory
        logger : the object of Log.Log()
    Returns :
        return dom object if get successfully
        return  None if enconters some errors
    """ 
    command = "svn info --xml %s" % target_dir
    (status, stdout) = Function.RunCommand(command)
    if status != 0:
        logger.LevPrint("ERROR", "Get svn info failed : %s" % (stdout), False)
        return None
    dom = None
    try: 
        dom = xml.dom.minidom.parseString(stdout)
    except:
        return None

    return dom


def GetSvnLastChangeRev(target_dir, logger):
    """
    get last changed revision of direcotry
    Args : 
        target_dir : the abs path of directory
        logger : the object of Log.Log
    Returns : 
        return the last changed reversion, if enconters some errors return None
    """
    svn_dom = _get_svn_xml(target_dir, logger)
    if svn_dom is not None:
        version = svn_dom.getElementsByTagName('commit')[0].getAttribute('revision')
        if version is None:
            logger.LevPrint('ERROR',
                    'svn info of %s doesn\'t contains last changed rev!' % target_path, False)
        return version

    return None


def GetSvnUrl(target_dir, logger):
    """
    get svn url of module
    Args:
        target_dir : the abs path of a directory
        logger : the object of Log.Log
    Returns: 
        return the svn url of module, if enconters some errors return None
    """
    svn_dom = _get_svn_xml(target_dir, logger)
    if svn_dom is not None:
        url = svn_dom.getElementsByTagName('url')[0].lastChild.data
        if url is None:
            logger.LevPrint('ERROR', 'svn info of %s doesn\'t contain url!' % target_path, False)
        return url

    return None


def GetGitUrl(target_dir, logger):
    """
    get git url of module
    Args :
        target_dir : the abs path of a directory
        logger : the object of Log.Log()
    Returns :
        return the git url of module, if enconters some errors return None
    """
    cmd = 'cd %s && git remote -v' % (target_dir)
    (status, msg) = Function.RunCommand(cmd)
    if status != 0:
        logger.LevPrint("ERROR", "get git url error! %s" % (msg), False)
        return None
    remote_infos = msg.split('\n')[0]
    url = remote_infos.split()[1]
    if url.endswith(".git"):
        url = url[0:-4]
    return url


def GetSvnRevision(target_dir, logger):
    """
    get svn revision of module
    Args :
        target_dir : the abs path of a directory
        logger : the object of Log.Log
    Returns :
        return svn revision of module,if enconters some errors return None
    """
    svn_dom = _get_svn_xml(target_dir, logger)
    if svn_dom is not None:
        revision = svn_dom.getElementsByTagName('entry')[0].getAttribute('revision')
        if revision is None:
            logger.LevPrint('ERROR', 'svn info of %s doesn\'t contains revision!' % target_path,
                    False)
        return revision
    return None


def GetSvnUrlRevision(target_dir, logger):
    """
    get svn url and revision of module
    Args :
        target_dir : the abs path of a directory
        logger : the object of Log.Log
    Returns :
        return tuple composed of svn url and revision of module, if enconters some errors return None
    """
    svn_dom = _get_svn_xml(target_dir, logger)
    url = None
    revision = None
    if svn_dom is not None:
        url = svn_dom.getElementsByTagName('url')[0].lastChild.data
        if url is None:
            logger.LevPrint('ERROR', 'svn info of %s doesn\'t contain url!' % target_path, False)
            return None
        revision = svn_dom.getElementsByTagName('entry')[0].getAttribute('revision')
        if revision is None:
            logger.LevPrint('ERROR', 'svn info of %s doesn\'t contains revision!' % target_path,
                            False)
            return None

    return (url, revision)


def GetSvnBranchKind(url, postfix_trunk, postfix_branch, postfix_tag, logger):
    """
    get svn branch kind using it's url
    Args :
        url : svn url of module
        postfix_trunk : postfix of trunk
        postfix_branch : postfix of branch
        postfix_tag : postfix of tag
        logger : the object of Log.Log
    Returns :
        return svn branch kind of module,if enconters some errors return None
        svn branch kind in ["BRANCH", "TAG"]
    """
    if url.endswith(postfix_tag):
        return "TAG"
    elif url.endswith(postfix_branch):
        return "BRANCH"
    elif url.find(postfix_trunk) != -1:
        return "BRANCH"
    else:
        logger.LevPrint('ERROR', 'Unknow type of branch!!Check the url %s' % (url), False)
        return None


def GetSvnBranchName(url, postfix_trunk, postfix_branch, logger):
    """
    get svn branch name using it's url
    Args :
        url : svn url of module
        postfix_trunk : postfix of trunk
        postfix_branch : postfix of branch
        logger : the object of Log.Log
    Returns :
        return svn branch name of module, if enconters some errors return None
    """
    if url.endswith(postfix_branch):
        br_name = url.split('/')[-1]
        return br_name
    elif url.find(postfix_trunk) != -1:
        return "trunk"
    else:
        logger.LevPrint('ERROR', 'Unknow name of branch!!Check the url %s' % (url), False)
        return None


def GetSvnTagName(url, postfix_tag, logger):
    """
    get svn tag name using it's url
    Args:
        url : svn url of module
        postfix_tag : postfix of tags
        logger : the object of Log.Log
    Returns :
        return svn tag name of module, if enconters some errors return None
    """
    if url.endswith(postfix_tag):
        tag_name = url.split('/')[-1]
        return tag_name
    else:
        logger.LevPrint('ERROR', 'Unknow name of tag!!Check the url %s' % (url), False)
        return None


def GetSvnCvspath(url, postfix_trunk, postfix_branch, postfix_tag, \
        svn_dir_types, svn_domain, logger):
    """
    get svn cvspath using it's url.
    Args :
        url : svn url of module
        postfix_trunk : the postfix of trunk in svn url
        postfix_branch : the postfix of branches in svn url
        postfix_tag : the postfix of tags in svn url
        svn_dir_types : list of directory types of svn.
                        For example: svn_dir_types = ['trunk', 'branches', 'tags']
        svn_domain : domain name of svn url
        logger : the object of Log.Log
    Returns :
        return cvspath of module, if enconters some errors return None
    """
    cvspath = ""
    if not url.startswith(svn_domain):
        return None
    if svn_domain.endswith('/'):
        svn_domain = svn_domain[0:-1]
    url_without_domain = url[len(svn_domain):]
    splited_urls = url_without_domain.split('/')[1:]
    if url.endswith(postfix_branch) or url.endswith(postfix_tag) or url.find(postfix_trunk) != -1:
        for item in splited_urls:
            if item in svn_dir_types:
                continue
            if item.endswith(postfix_branch) or item.endswith(postfix_tag):
                continue
            cvspath = os.path.join(cvspath, item)
        if cvspath.endswith('/'):
            cvspath =  cvspath[:-1]
        return cvspath
    else:
        logger.LevPrint('ERROR', 'Can\'t check the url %s is trunk, branches or tags' % url, False)
        return None


def GetModuleName(cvspath):
    """
    get module name from it's cvspath
    Args :
        cvspath : module's cvspath
    Returns :
        module name
    """
    if cvspath.endswith('/'):
        cvspath = cvspath[:-1]
    module_name = cvspath.split('/')[-1]
    return module_name


def GetBrocCvspath(cvspath):
    """
    get broc cvspath of module.
    Args :
        cvspath : module's cvspath
    Returns :
        broc cvspath
    """
    broc_cvspath = os.path.join(cvspath, 'BROC')
    return broc_cvspath


def GetWorkSpace(target_path, cvspath, logger):
    """
    get work space dir for module
    Args :
        target_path : local path of module
        cvspath : module's cvspath
        logger : the object of Log.Log
    Returns :
        return svn work space of module,if enconters some errors return None
    """
    local_path = os.path.realpath(target_path)
    if local_path.endswith('/'):
        local_path = local_path[0:-1]
    if local_path.endswith(cvspath):
        work_space = local_path[0:-len(cvspath)]
        if work_space.endswith('/'):
            return work_space[0:-1]
        else:
            return work_space
    else:
        logger.LevPrint('ERROR', 'local path is %s, must end with %s!!' % (target_path, cvspath), \
                False)
        return None


def GetSvnUrlInfos(target_dir, postfix_trunk, postfix_branch, postfix_tag, \
        svn_dir_types, svn_domain, logger):
    """
    Description : get svn info from a abs path of directory
    Args :
        path : the abs path of directory
        postfix_trunk : the postfix of trunk in svn rul
        postfix_branch : the postfix of branches in svn url
        postfix_tag : the postfix of tags in svn url
        svn_dir_types : list of directory types of svn
                        For example: svn_dir_types = ['trunk', 'branches', 'tags']
        logger : the object of Log.Log
    Returns :
        result['result'] : False(fail) or True(success)
        result['root_path'] : svn root path
        result['url'] : module svn url
        result['br_kind'] : module branch kind
        result['revision'] : module revision
        result['last_changed_rev'] : module last changed revision
        result['br_name'] : module branches name
        result['tag_name'] : module tags name
        result['module_cvspath'] : module cvspath
        result['name'] : module name
        result['broc_cvspath'] : cvspath of BROC file
        restul['workspace'] : module work space
    """
    result = {}
    result['result'] = False
    result['root_path'] = ''
    result['url'] = ''
    result['br_kind'] = ''
    result['revision'] = ''
    result['last_changed_rev'] = ''
    result['br_name'] = ''
    result['tag_name'] = ''
    result['module_cvspath'] = ''
    result['name'] = ''
    result['broc_cvspath'] = ''
    result['workspace'] = ''

    result['root_path'] = GetSvnRoot(target_dir, logger)
    if result['root_path'] is None:
        return result

    result['url'] = GetSvnUrl(target_dir, logger)
    if result['url'] is None:
        return result

    result['br_kind'] = GetSvnBranchKind(result['url'], postfix_trunk, \
            postfix_branch, postfix_tag, logger)
    if result['br_kind'] is None:
        return result

    result['revision'] = GetSvnRevision(target_dir, logger)
    if result['revision'] is None:
        return result
    
    result['last_changed_rev'] = GetSvnLastChangeRev(target_dir, logger)
    if result['last_changed_rev'] is None:
        return result

    if result['br_kind'] == 'BRANCH':
        result['br_name'] = GetSvnBranchName(result['url'], postfix_trunk, postfix_branch, logger)
        if result['br_name'] is None:
            return result

    if result['br_kind'] == 'TAG':
        result['tag_name'] = GetSvnTagName(result['url'], postfix_tag, logger)
        if result['tag_name'] is None:
            return result

    result['module_cvspath'] = GetSvnCvspath(result['url'],
            postfix_trunk, postfix_branch, postfix_tag, svn_dir_types, svn_domain, logger)
    if result['module_cvspath'] is None:
        return result
    
    result['name'] = GetModuleName(result['module_cvspath'])
    result['broc_cvspath'] = GetBrocCvspath(result['module_cvspath'])
    result['workspace'] = GetWorkSpace(target_dir, result['module_cvspath'], logger)
    if result['workspace'] is None:
        return result

    result['result'] = True
    return result


def GetGitBranchKind(target_dir, logger):
    """
    get git branch kind from it's local path
    Args :
        path : local path of module
        logger : the object of Log.Log
    Returns :
        return git branch kind of module,if enconters some errors return None
    """
    pass


def GetGitBranchName(target_dir, logger):
    """
    get git branch name from it's local path
    Args :
        path : local path of module
        logger : the object of Log.Log
    Returns :
        return git branch name of module,if enconters some errors return None
    """
    pass


def GetGitTagName(target_dir, logger):
    """
    get git tag name from it's local path
    Args :
        path : local path of module
        logger : the object of Log.Log
    Returns :
        return git tag name of module,if enconters some errors return None
    """
    pass


def GetGitCommitId(target_dir, logger):
    """
    get git commid id from it's local path
    Args:
        target_dir : the abs path of a directory
        logger : the object of Log.Log 
    Returns:
        return git cimmit id of module,if enconters some errors return None
    """
    cmd = 'cd %s && git log --format=%%H -1' % (target_dir)
    (status, msg) = Function.RunCommand(cmd)
    if status != 0:
        logger.LevPrint("ERROR", "Get git commit id error: %s" % (msg), False)
        return None
    return msg.strip()


def GetGitCvspath(url, git_domain, logger):
    """
    get module git cvspath from it's git url
    Args :
        url : module's git url
        git_domain : git domain name
        logger : the object of Log.Log
    Returns :
        return git cvspath of module,if enconters some errors return None
    """
    if not url.startswith(git_domain):
        logger.LevPrint('ERROR', 'Git url does not start with %s!!' % git_domain, False)
        return None
    cvspath = url[len(git_domain):]
    if cvspath.endswith('/'):
        cvspath = cvspath[:-1]
    return cvspath


def GetGitUrlInfos(target_dir, git_domain, logger):
    """
    get git info from the abs path of a directory 
    Args :
        target_dir: the abs path of a directory
        git_domain : git domain name
        logger : the object of Log.Log
    Returns :
        result['result'] : True(fail) or False(success)
        result['root_path'] : svn root path
        result['url'] : module svn url
        result['br_kind'] : module branch kind
        result['commit_id'] : module commit id
        result['br_name'] : module branches name
        result['tag_name'] : module tags name
        result['module_cvspath'] : module cvspath
        resutl['name'] : module name
        result['broc_cvspath'] : module broc cvspath
        result['workspace'] : module workspace cvspath
    """
    result = dict()
    result['result'] = False
    result['root_path'] = ''
    result['url'] = ''
    result['br_kind'] = ''
    result['br_name'] = ''
    result['commit_id'] = ''
    result['tag_name'] = ''
    result['module_cvspath'] = ''
    result['name'] = ''
    result['broc_cvspath'] = ''
    result['workspace'] = ''

    result['root_path'] = GetGitRoot(target_dir, logger)
    if result['root_path'] is None:
        return result

    result['url'] = GetGitUrl(target_dir, logger)
    if result['url'] is None:
        return result

    result['br_kind'] = GetGitBranchKind(target_dir, logger)
    if result['br_kind'] is None:
        return result

    result['br_name'] = GetGitBranchName(target_dir, logger)
    if result['br_name'] is None:
        return result

    result['tag_name'] = GetGitTagName(target_dir, logger)
    if result['tag_name'] is None:
        return result

    result['commit_id'] = GetGitCommitId(target_dir, logger)
    if result['commit_id'] is None:
        return result
    
    result['module_cvspath'] = GetGitCvspath(result['url'], git_domain, logger)
    if result['module_cvspath'] is None:
        return result

    result['name'] = GetModuleName(result['module_cvspath'])
    result['broc_cvspath'] = GetBrocCvspath(result['module_cvspath'])

    result['workspace'] = GetWorkSpace(target_dir, result['module_cvspath'])
    if result['workspace'] is None:
        return result

    result['result'] = True
    return result


