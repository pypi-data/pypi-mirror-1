# -*- coding: UTF-8 -*-
# vim: ts=4 sw=4 et:

"""
TestObject is a basic class for all objects in journal file
"""

__author__ = "Andy Shevchenko <andy.shevchenko@gmail.com>"
__revision__ = "$Id$"

__all__ = [
    'TestObject',
    'diff',
    'diff_keys_by_result',
    'get_keys_by_result',
    'get_objects_by_result',
]

import copy

from minitestlib.Log import logger
from minitestlib.OrderedDict import OrderedDict

class TestObject:
    """ Basement for each journal object """
    def __init__(self, parent, key):
        self.parent = parent         # links to parent object
        self.key = key               # key
        self.lines = []              # journal excerpt related to this object
        self.objects = OrderedDict() # container of childs
        self.results = {}            # results of childs or self results
        self.amount = 0              # overall amount of collected results
        self.collected = False       # Protect results from overflow
        self.name = 'noname'         # Object name

    def dbg(self, msg):
        """ Internal debbuging """
        logger.debug("%s: %s" % (self.__class__.__name__, msg))

    def append(self, line):
        """ Append line to object """
        self.lines.append(line)

    def __len__(self):
        """ Represent length of object as length of its container """
        return len(self.objects)

    def __getitem__(self, key, result=None):
        """ Get item from container by key """
        return self.objects.get(key, result)

    def keys(self):
        """ Get container's keys """
        return self.objects.keys()

    def get_keys(self):
        """ Get keys as a list of parent's keylist and self key """
        if self.parent is None:
            return [self.key, ]
        keys = self.parent.get_keys()
        keys.append(self.key)
        return keys

    def get_results(self):
        """ Return collected results """
        return self.results

    def get_amount(self):
        """ Return overall amount of collected results """
        return self.amount

    def summarize(self):
        """ Summarize results of childs """
        if self.collected or len(self.objects) == 0:
            return
        # Collect info from childs
        for obj_key in self.objects.keys():
            self.objects[obj_key].summarize()
            results = self.objects[obj_key].get_results()
            for result_key in results.keys():
                if self.results.has_key(result_key):
                    self.results[result_key] += results[result_key]
                else:
                    self.results[result_key] = results[result_key]
            self.amount += self.objects[obj_key].get_amount()
        # Set protection flag
        self.collected = True

def diff(old, new, removed, added, changed):
    """ Get difference between two objects """
    if len(old) == 0 and len(new) == 0:
        # Got a leaf
        results_old = old.get_results()
        results_new = new.get_results()
        results_set = set(results_old.keys() + results_new.keys())
        # Empty objects
        if len(results_set) == 0:
            return
        # Check the result equivalency
        if len(results_set) == 1:
            if len(results_old) == 1 and len(results_new) == 1:
                return
        # Have a difference
        changed.append([old, new])
    else:
        # Get object keys for both old and new
        keys_old = old.keys()
        keys_new = new.keys()
        # Calculate difference
        for key in set(keys_old + keys_new):
            if key not in keys_new:
                removed.append(old[key])
            elif key not in keys_old:
                added.append(new[key])
            else:
                diff(old[key], new[key], removed, added, changed)

def diff_keys_by_result(old, new, start_depth=0):
    """ Get difference between objects key traces """
    old_keys = get_keys_by_result(old, start_depth)
    new_keys = get_keys_by_result(new, start_depth)
    for name in old_keys.keys():
        if name not in new_keys.keys():
            continue
        # FIXME: Looks like O(n^2) in worst case
        keys_copy = copy.copy(old_keys[name])
        for keys in keys_copy:
            if keys in new_keys[name]:
                old_keys[name].remove(keys)
                new_keys[name].remove(keys)
        if len(old_keys[name]) == 0:
            del old_keys[name]
        if len(new_keys[name]) == 0:
            del new_keys[name]
    return old_keys, new_keys

def get_keys_by_result(starter, start_depth=0):
    """ Fill structure by key traces of given objects """
    objects = {}
    get_objects_by_result(starter, objects)
    keys = {}
    for name in objects.keys():
        keys[name] = []
        for obj in objects[name]:
            keys[name].append(obj.get_keys()[start_depth:])
    return keys

def get_objects_by_result(starter, objects):
    """ Collect objects in the dependency of their result recursively """
    if len(starter) == 0:
        for result in starter.get_results():
            if result not in objects.keys():
                objects[result] = []
            objects[result].append(starter)
    else:
        for key in starter.keys():
            get_objects_by_result(starter[key], objects)

