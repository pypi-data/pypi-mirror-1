#!/usr/bin/env python

"""Unit tests for M2Crypto.DH.

Copyright (c) 2000-2001 Ng Pheng Siong. All rights reserved."""

RCS_id='$Id: test_util.py 299 2005-06-09 17:32:28Z heikki $'

import unittest
from M2Crypto import util
import sys

class UtilTestCase(unittest.TestCase):

    def check_hex_to_string(self):


def suite():
    return unittest.makeSuite(UtilTestCase, 'check_')


if __name__=='__main__':
    Rand.load_file('randpool.dat', -1) 
    unittest.TextTestRunner().run(suite())
    Rand.save_file('randpool.dat')

