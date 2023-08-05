#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import doctest
import glob
import os.path

def test_doctests():
	dir = os.path.dirname(__file__)
	suite = unittest.TestSuite()
	for f in glob.glob(dir + "/*.txt"):
		suite.addTest(doctest.DocFileSuite(os.path.basename(f)))
	for f in glob.glob(dir + "/*.rst"):
		suite.addTest(doctest.DocFileSuite(os.path.basename(f)))
	runner = unittest.TextTestRunner()
	return runner.run(suite)


if __name__ == "__main__" :
	test_doctests()
