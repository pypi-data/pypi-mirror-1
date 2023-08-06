#!/usr/bin/env python
#
#

import unittest

def suite():
    modules_to_test = ('test_docbook2pageobject', 'test_wrapper', 'test_syncronize', 'test_create', 'test_transformation', 'test_image') # and so on
    alltests = unittest.TestSuite()
    for module in map(__import__, modules_to_test):
        alltests.addTest(unittest.findTestCases(module))
    return alltests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
