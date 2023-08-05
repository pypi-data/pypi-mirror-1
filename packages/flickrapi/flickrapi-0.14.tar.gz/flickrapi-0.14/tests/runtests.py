#!/usr/bin/env python

import unittest
import sys

import test_flicrkapi
import test_multipart
import test_tokencache

load = unittest.TestLoader().loadTestsFromModule
suites = [
          load(test_flicrkapi),
          load(test_multipart),
          load(test_tokencache)
        ]

for suite in suites:
    testRunner = unittest.TextTestRunner()
    result = testRunner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
