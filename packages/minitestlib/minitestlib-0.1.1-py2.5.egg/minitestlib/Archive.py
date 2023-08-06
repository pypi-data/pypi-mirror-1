# -*- coding: UTF-8 -*-
# vim: ts=4 sw=4 et:

"""
Archive maker and DB support
"""

__author__ = "Andy Shevchenko <andy.shevchenko@gmail.com>"
__revision__ = "$Id$"

__all__ = [
    'ArcFile',
    'ArchiveDB',
    'Archive',
    'get_stat_from_files',
    'names_to_files',
]

import os
import shutil
import re

from minitestlib.Log import logger
from minitestlib.Utils import make_dir

ARCHIVE_FILE_SEPARATOR = '-'
ARCHIVE_DB_PAIR_SEPARATOR = '  '

class ArcFile(dict):
    """ Represent archive file object """
    def __init__(self, tc_name, journal="journal", mtime=0.0):
        dict.__init__(self)

        self['path']  = tc_name
        self['file']  = journal
        self['mtime'] = mtime

    def __cmp__(self, obj):
        """ Compare two file objects """
        result = cmp(self['path'], obj['path'])
        if result == 0:
            result = cmp(self['file'], obj['file'])
            if result == 0:
                return cmp(self['mtime'], obj['mtime'])
        return result

    def __str__(self):
        """ String representation of this object """
        return os.path.join(self['path'], self['file'])

    def key(self):
        """ Get key as path and number part of filename """
        return os.path.join(self['path'],
                            self['file'].split(ARCHIVE_FILE_SEPARATOR)[1])

def names_to_files(arc_dir, names):
    """ Convert files in form tc_name/journal to file object """
    files = []
    for name in names:
        tc_name, journal = os.path.split(name)
        mtime = os.path.getmtime(os.path.join(arc_dir, name))
        files.append(ArcFile(tc_name, journal, mtime))
    return files

class ArchiveDB:
    """ Handle DB for our archive """
    def __init__(self, arc_dir, db_name):
        self.arc_dir = arc_dir
        self.db_name = os.path.join(arc_dir, db_name)
        self.files = {}     # timestamp FILES tc_name1 journal1  [tc_name2 journal2  [...]]
        self.results = {}   # timestamp RESULTS RES1 num1  [RES2 num2  [...]]
        self.pairs_sep = ARCHIVE_DB_PAIR_SEPARATOR
        self.result_re = re.compile("(?P<result>.+)\s(?P<amount>\d+)", re.U)

    def dbg(self, msg):
        """ Internal debbuging """
        logger.debug("%s: %s" % (self.__class__.__name__, msg))

    def read(self):
        """ Read and parse DB file """
        try:
            db_file_content = open(self.db_name, "r").read()
        except IOError, err:
            logger.warning(str(err))
            return

        line_num = 0
        for line in db_file_content.splitlines():
            line_num += 1
            try:
                timestamp, xtype, data = line.split(None, 2)
            except ValueError:
                logger.warning("Wrong line %d in DB" % line_num)
                continue
            gm_time = float(timestamp)
            pairs = data.split(self.pairs_sep)
            if len(pairs) == 0:
                logger.warning("No data in line %d in DB" % line_num)
                continue
            if xtype == 'FILES':
                self.files[gm_time] = []
                for pair in pairs:
                    tc_name, journal = pair.strip().split()
                    tc_file = os.path.join(self.arc_dir, tc_name, journal)
                    try:
                        mtime = os.path.getmtime(tc_file)
                    except OSError:
                        # Skip obsoleted record
                        continue
                    self.files[gm_time].append(ArcFile(tc_name, journal,
                                                       mtime))
            elif xtype == 'RESULTS':
                self.results[gm_time] = {}
                for pair in pairs:
                    match = self.result_re.match(pair)
                    if match:
                        amount = int(match.group('amount'))
                        self.results[gm_time][match.group('result')] = amount
            else:
                logger.warning("Unknown mode '%s' in line %d in DB" % (xtype, line_num))

    def keys(self):
        """ Get common keys in sorted order """
        result = []
        for key in self.files.keys():
            # Check key presence in result storage
            # TODO: Should it go to read() ?
            if key in self.results.keys():
                result.append(key)
        result.sort()
        return result

    def get_last_key(self):
        """ Get the most recent timestamp in DB """
        keys = self.keys()
        try:
            return keys[-1]
        except IndexError:
            return None

    def get_files(self, gm_time, result=None):
        """ Get files by timestamp """
        return self.files.get(gm_time, result)

    def get_results(self, gm_time, result=None):
        """ Get results by timestamp """
        return self.results.get(gm_time, result)

    def update(self, gm_time, files, results):
        """ Add new record to DB """
        if len(files) == 0 or len(results) == 0:
            logger.warning("Could not update DB by empty data")
            return
        self.files[gm_time] = files
        self.results[gm_time] = results
        db_file = open(self.db_name, "a")
        # FILES
        db_file.write("%s FILES" % str(gm_time))
        for file_obj in files:
            db_file.write(self.pairs_sep)
            db_file.write("%(path)s %(file)s" % file_obj)
        db_file.write("\n")
        # RESULTS
        db_file.write("%s RESULTS" % str(gm_time))
        for key in results.keys():
            db_file.write(self.pairs_sep)
            db_file.write("%s %s" % (key, results[key]))
        db_file.write("\n")
        db_file.close()

    def regen(self):
        """ TODO: Regenerate DB from actual files """
        pass

def get_stat_from_files(files):
    """ Prepare simple structure to keep stat info """
    arc_stat = {}
    if files is None:
        return arc_stat
    for arc_file in files:
        path = arc_file['path']
        mtime = arc_file['mtime']
        if path in arc_stat.keys():
            if mtime > arc_stat[path]:
                arc_stat[path] = mtime
        else:
            arc_stat[path] = mtime
    return arc_stat

class Archive:
    """ Archive maker """
    def __init__(self, arc_stat, arc_dir, tc_root_dir, gm_time,
                 journal="journal"):
        self.arc_stat = arc_stat
        self.arc_dir = arc_dir
        self.tc_root_dir = tc_root_dir
        self.gm_time = gm_time
        self.journal = journal
        self.sep = ARCHIVE_FILE_SEPARATOR

    def dbg(self, msg):
        """ Internal debbuging """
        logger.debug("%s: %s" % (self.__class__.__name__, msg))

    def _resultsdir(self, tc_name):
        """ Get directory with results """
        return os.path.join(self.tc_root_dir, tc_name, "results")

    def _copylogs(self, tc_name):
        """ Copy only recent log files """
        fromdir = self._resultsdir(tc_name)
        newmtime = lastmtime = self.arc_stat.get(tc_name, 0.0)
        dirs = []
        for xdir in os.listdir(fromdir):
            logdir = os.path.join(fromdir, xdir)
            if not os.path.isdir(logdir):
                continue
            mtime = os.path.getmtime(logdir)
            if mtime > lastmtime:
                dirs.append(xdir)
                newmtime = max(mtime, newmtime)
        files = []
        for xdir in dirs:
            # Filename in archive like: timestampRun-dirname
            fromfile = os.path.join(fromdir, xdir, self.journal)
            tofile_name = str(self.gm_time) + self.sep + xdir
            tofile = os.path.join(self.arc_dir, tc_name, tofile_name)
            shutil.copyfile(fromfile, tofile)
            self.dbg("Copied file %s from %s" % (tofile, fromfile))
            mtime = os.path.getmtime(fromfile)
            os.utime(tofile, (mtime, mtime))
            files.append(ArcFile(tc_name, tofile_name, mtime))
        return files

    def archive(self):
        """ Traverse through test root directory and copy logs in archive """
        if not os.path.isdir(self.tc_root_dir):
            return []
        files = []
        for xdir in os.listdir(self.tc_root_dir):
            resdir = self._resultsdir(xdir)
            if not os.path.isdir(resdir):
                continue
            make_dir(os.path.join(self.arc_dir, xdir))
            files.extend(self._copylogs(xdir))
        return files

