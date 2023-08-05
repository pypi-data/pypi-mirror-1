#!/usr/bin/env python

"""Unit tests for M2Crypto.EC, ECDSA part.

Copyright (c) 2000 Ng Pheng Siong. All rights reserved.
Portions copyright (c) 2005-2006 Vrije Universiteit Amsterdam. All rights reserved.
"""

import unittest
import sha
from M2Crypto import EC, BIO, Rand, m2

class ECDSATestCase(unittest.TestCase):

    errkey = 'rsa.priv.pem'
    privkey = 'ec.priv.pem'
    pubkey = 'ec.pub.pem'

    data = sha.sha('Can you spell subliminal channel?').digest()

    def callback(self, *args):
        pass

    def callback2(self):
        pass

    def check_loadkey_junk(self):
        self.assertRaises(ValueError, EC.load_key, self.errkey)

    def check_loadkey(self):
        ec = EC.load_key(self.privkey)
        assert len(ec) == 233

    def check_loadpubkey(self):
        # XXX more work needed
        ec = EC.load_pub_key(self.pubkey)
        assert len(ec) == 233
        self.assertRaises(EC.ECError, EC.load_pub_key, self.errkey)

    def check_sign_dsa(self):
        ec = EC.load_key(self.privkey)
        r, s = ec.sign_dsa(self.data)
        assert ec.verify_dsa(self.data, r, s)
        assert not ec.verify_dsa(self.data, s, r)

    def check_sign_dsa_asn1(self):
        ec = EC.load_key(self.privkey)
        blob = ec.sign_dsa_asn1(self.data)
        assert ec.verify_dsa_asn1(self.data, blob)
        self.assertRaises(EC.ECError, ec.verify_dsa_asn1, blob, self.data)

    def check_verify_dsa(self):
        ec = EC.load_key(self.privkey)
        r, s = ec.sign_dsa(self.data)
        ec2 = EC.load_pub_key(self.pubkey)
        assert ec2.verify_dsa(self.data, r, s)
        assert not ec2.verify_dsa(self.data, s, r)
        
    def check_genparam(self):
        ec = EC.gen_params(EC.NID_sect233k1)
        assert len(ec) == 233


def suite():
    return unittest.makeSuite(ECDSATestCase, 'check')
    

if __name__ == '__main__':
    Rand.load_file('randpool.dat', -1) 
    unittest.TextTestRunner().run(suite())
    Rand.save_file('randpool.dat')

