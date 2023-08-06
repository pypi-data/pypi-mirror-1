#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009, Mathieu PASQUET <mpa@makina-corpus.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import unittest
import doctest
import os.path
from Globals import package_home
from Testing import ZopeTestCase as ztc
from Products.CMFCore.utils import getToolByName

from collective.z3cform.grok.tests.base import collective_z3cform_grok_PolicyFunctionalTestCase

#######################################################################################
# IMPORT/DEFINE VARIABLES OR MODULES THERE
# THEY WILL BE AVAILABLE AS GLOBALS INSIDE YOUR DOCTESTS
#######################################################################################
# example:
# from for import bar
# and in your doctests, you can do:
# >>> bar.something
from collective.z3cform.grok.tests.globals import *
#######################################################################################

#You can even launch doctests from others packages with the policy setup with embedding this test suite
#You can even add others globals in those tests.
#Example : This snippet will launch all txt doctests in the other package directory
# cat someother/package/src/package/tests/tests_docs.py
#from nmd.sugar.policy.tests.test_setup import test_doctests_suite as ts
#def test_suite():
#    globs = globals()
#    return ts(__file__, globs)


# if you have plone.reload out there add an helper to use in doctests while programming
# just use reload(module) in pdb :)
# it would be neccessary for you to precise each module to reload, this method is also not recursive.

# eg: (pdb) from foo import bar;preload(bar)

try:
    def preload(modules_or_module, excludelist=None):
        modules = modules_or_module
        if not isinstance(modules_or_module, list):
            modules = [modules_or_module]
        if not excludelist:
            excludelist = []
        import sys
        if not modules:
            modules = sys.modules
        from plone.reload.xreload import Reloader
        for module in modules:
            if not module in excludelist:
                try:
                    Reloader(module).reload()
                except Exception, e:
                    pass
except Exception, e:
    pass

# stolen from five.grok.tests.doctest
def doctestToPython(filenameInput, filenameOutput):
    assert os.path.exists(filenameInput)
    docFileR = open(filenameInput, 'r')
    newLines = []
    originalLines = []
    for line in docFileR.readlines():
        originalLines.append(line)
        if '<<<' in line:
            match = re.match(re.compile('(\s+<<<\s)(.*)'), line)
            if match:
                grokCodeFlag = True
                newLines.append("%s\n" % match.groups()[1])
        elif '...' in line and grokCodeFlag == True:
            match = re.match(re.compile('(\s+\.\.\.\s)(.*)'), line)
            if match:
                newLines.append("%s\n" % match.groups()[1])
        elif '<<<' not in line or '...' not in line: # handle comments
            grokCodeFlag = False
            newLines.append('#%s' % line)

    docFileR.close()

    docFileW = open(filenameOutput, 'w')
    for newLine in newLines:
        if newLine.strip() != '#':
            docFileW.write('%s' % newLine)
        else:
            docFileW.write('\n')
    docFileW.close()

class DocTestCase(collective_z3cform_grok_PolicyFunctionalTestCase):

    # if you use sparse files, just set the base module from where are the txt files
    # otherwise it will be the 'tests' module parent from your classfile
    tested_module = None

    def setUp(self):
        testFile = self.testref
        testFileDirName, testFullFileName = os.path.split(testFile)
        testFileName, testFileExt = os.path.splitext(testFullFileName)
        pythonTestFile = os.path.join(testFileDirName, testFileName + '.py')
        doctestToPython(testFile, pythonTestFile)
        zope.component.eventtesting.setUp()
        def filescleanup(files, *args, **kwargs):
            [os.remove(f)
             for f in files
             if os.path.exists(f)]
        # the first inherited method will win the right to configure the plone site :)
        # good for subclassing
        self.setUp_hook()
        zope.testing.cleanup.addCleanUp(filescleanup,
                                        ([pythonTestFile, pythonTestFile+"c"],)
                                       )
        module_dotted_name = self.tested_module
        if not self.tested_module:
            module_dotted_name =  '.'.join(self.__module__.split('.')[:-1])
        dotted_name = "%s.%s" % (
            module_dotted_name,
            os.path.split(pythonTestFile)[1].replace('.py', ''))
        fgrok(dotted_name)
        #XXX this should be done by the GrokDocFileSuite
        from zope.traversing.adapters import DefaultTraversable
        zope.component.provideAdapter(DefaultTraversable, [None])
        self.portal.getSiteManager().registerAdapter(
            DefaultTraversable, [None]
        )

    def tearDown(self):
        # the first inherited method will win the right to tearDown the plone site :)
        # good for subclassing
        self.tearDown_hook()
        zope.testing.cleanup.cleanUp()

    def setUp_hook(self):
        collective_z3cform_grok_PolicyFunctionalTestCase.setUp(self)

    def tearDown_hook(self):
        collective_z3cform_grok_PolicyFunctionalTestCase.tearDown(self)

def test_doctests_suite(directory=None, globs=None, suite=None, testklass=DocTestCase):
    if not directory:
        dir, _f = os.path.split(os.path.abspath(__file__))
    elif os.path.isfile(directory):
        dir = os.path.dirname(directory)
    files = [os.path.join(dir, f) for f in os.listdir(dir)
                                  if f.endswith('.txt')]

    if not globs:
        globs={}
    g = globals()
    for key in g:
        globs.setdefault(key, g[key])
    dir = directory

    if not suite:
        suite = unittest.TestSuite()
    if files:
        # give a reference to the doctest to the underlying testcase
        options = doctest.REPORT_ONLY_FIRST_FAILURE |\
                  doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
        for test in files:
            klass = deepcopy(testklass)
            klass.testref = test
            ft = ztc.ZopeDocFileSuite(
                    test,
                    test_class=klass,
                    optionflags=options,
                    globs=globs,
                    module_relative = False,
                )
            suite.addTest(ft)
    return suite

def test_suite():
    """."""
    return test_doctests_suite()

