#!/usr/bin/env python
"""Callbacks for log entry results.

$Id: actions.py 179 2005-12-20 20:04:00Z drew $
"""

import sys

from xix.utils.python import CurriedCallable

__author__ = 'Drew Smathers'
__copyright__ = 'Copyright 2005, Drew Smathers'
__revision__ = '$Revision: 179 $'


class Action:

    def __init__(self):
        self.__level_callbacks = {}
        self.__category_callbacks = {}

    def addLevelCallback(self, level, func, *pargs, **kwargs):
        """Add callback for entry with level given in 
        log entry header.
        """
        lcs = self.__level_callbacks
        if level not in lcs.keys():
            lcs[level] = []
        lcs[level].append(CurriedCallable(func, *pargs, **kwargs))
        
    def addMessageCategoryCallback(self, cat, func, *pargs, **kwargs):
        """Add callback for entry of the given category.
        """
        mcs = self.__category_callbacks
        if cat not in mcs.keys():
            mcs[cat] = []
        mcs[cat].append(CurriedCallable(func, *pargs, **kwargs))

    def __call__(self, entry):
        if hasattr(entry.header, 'level'):
            lcs = self.__level_callbacks
            for func in lcs.get(entry.header.level, []):
                func(entry)
        mcs = self.__category_callbacks
        for func in mcs.get(entry.message.category, []):
            func(entry)
    
