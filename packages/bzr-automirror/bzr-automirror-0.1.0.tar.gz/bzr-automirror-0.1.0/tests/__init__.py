# Copyright 2008 Neil Martinsen-Burrell

# This software is licensed under the MIT license.  See README for
# details.

from unittest import TestLoader, TestSuite

import test_update

def test_suite():
    r = TestSuite()
    r.addTests(TestLoader().loadTestsFromModule(test_update))
    return r
