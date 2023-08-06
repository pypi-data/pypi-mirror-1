#!/usr/bin/env python
import os
from unittest import TestSuite
from unittest import TextTestRunner
from doctest import DocFileSuite

from utils import findTests, importModule, buildUnittestSuites

from test_doctests import suite as doctestSuite


searchDirs = ['pylispng', 'test']
skipFiles = ['test_doctests.py', 'test_all.py']

suites = buildUnittestSuites(paths=searchDirs, skip=skipFiles)
suites.append(doctestSuite)
suites.append(DocFileSuite('../README'))


if __name__ == '__main__':
    runner = TextTestRunner(verbosity=2)
    runner.run(TestSuite(suites))
