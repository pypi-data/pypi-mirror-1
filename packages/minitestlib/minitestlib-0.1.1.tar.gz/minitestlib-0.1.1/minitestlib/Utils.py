# -*- coding: UTF-8 -*-
# vim: ts=4 sw=4 et:

"""
File and directory operations wrappers
"""

__author__ = "Andy Shevchenko <andy.shevchenko@gmail.com>"
__revision__ = "$Id$"

__all__ = [
    'copy_dir',
    'make_dir',
    'multi_replace',
    'multi_replace_file',
    'list_dir',
    'remove_dir',
]

import os
import shutil

from minitestlib.Log import logger

def copy_dir(src, dst):
    """ Copy tree """
    shutil.copytree(src, dst, True)

def list_dir(src):
    """ Find all files in the given directory recursively """
    logger.debug("list_dir(): %s" % src)
    listing = []
    for path, dummy, files in os.walk(src):
        for filename in files:
            listing.append(os.path.abspath(os.path.join(path, filename)))
    return listing

def make_dir(src, permissions=0755):
    """ Create directory tree """
    if not os.path.isdir(src):
        try:
            os.makedirs(src, permissions)
            logger.debug("make_dir(): Created path: %s" % src)
        except OSError, err:
            logger.debug("make_dir(): %s" % str(err))
            return False
    return True

def multi_replace(data, pattern):
    """ Replace text by pattern set """
    for key in pattern.keys():
        data = data.replace(key, pattern[key])
    return data

def multi_replace_file(src, dst, pattern):
    """ Replace file content by pattern set """
    try:
        src_content = open(src, "r").read()
        src_content = multi_replace(src_content, pattern)
        open(dst, "w").write(src_content)
    except IOError, err:
        logger.error("multi_replace_file(): %s" % str(err))
        return False
    return True

def remove_dir(src, ignore=None):
    """ Remove directory content recursively """
    if not os.path.isdir(src) or os.path.islink(src):
        logger.warning("remove_dir(): Can't remove non-directory object %s" % src)
        return
    content = os.listdir(src)
    if ignore is not None:
        exclude = ignore(src, content)
        for element in exclude:
            try:
                content.remove(element)
            except ValueError, err:
                logger.warning("remove_dir(): %s" % str(err))
    for element in content:
        leaf = os.path.join(src, element)
        if os.path.isdir(leaf) and not os.path.islink(leaf):
            remove_dir(leaf)    # it's a directory, remove it
        else:
            try:
                os.unlink(leaf) # it's a file, delete it
            except OSError, err:
                logger.warning("remove_dir(): %s" % str(err))
    try:
        os.rmdir(src)   # delete the directory here
    except OSError, err:
        logger.debug("remove_dir(): %s" % str(err))

