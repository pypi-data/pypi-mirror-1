#!/usr/bin/env python

###############################################################################
#
# $Id: runtests.py 264 2006-08-28 21:42:56Z djfroofy $
#
###############################################################################

import unittest
import loggrok.log
import sys, os
from glob import glob
from xix.utils.config import configFactory
from xix.utils.test import doctest, DocFileSuiteBuilder

__author__ = 'Drew Smathers'
__copyright__ = 'Copyright (c) 2005 Drew Smathers'
__version__ = '$Revision: 264 $'[11:-2]

abspath = os.path.abspath
sepj = os.path.sep.join
pj = os.path.join

configFactory.addResource('loggrok-unittest.cfg', 'unittest.cfg')

ftestdir = abspath(sepj(('tests','functional',)))

functionaltests = (
    #(ftestdir, ('python collisions.py','python dragging.py')),
)

import test
    
if __name__ == '__main__':
    
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(loggrok.log))
    doctest_builder = DocFileSuiteBuilder(test, ['test'], recursive=False)
    doctest_builder.addToSuite(suite)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    if len(sys.argv) > 1 and sys.argv[1] == '-f':
        print '=' * 80
        print '== Beginning functional tests'
        print '=' * 80
        import commands
        for wd, cmds in functionaltests:
            os.chdir(wd)
            for cmd in cmds:
                output = commands.getoutput(cmd)
                print output
        

