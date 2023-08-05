"""Copyright (c) 1999-2003 Ng Pheng Siong. All rights reserved."""

RCS_id='$Id: Cipher.py 299 2005-06-09 17:32:28Z heikki $'

from M2Crypto import m2

class Cipher:
    def __init__(self, cipher):
        self.cipher=cipher

    def __len__(self):
        return m2.ssl_cipher_get_bits(self.cipher)

    def __repr__(self):
        return "%s-%s" % (self.name(), len(self))

    def __str__(self):
        return "%s-%s" % (self.name(), len(self))

    def version(self):
        return m2.ssl_cipher_get_version(self.cipher)

    def name(self):
        return m2.ssl_cipher_get_name(self.cipher)


class Cipher_Stack:
    def __init__(self, stack):
        self.stack=stack

    def __len__(self):
        return m2.sk_ssl_cipher_num(self.stack)

    def __getitem__(self, idx):
        if idx < 0 or idx >= m2.sk_ssl_cipher_num(self.stack):
            raise IndexError, 'index out of range'
        v=m2.sk_ssl_cipher_value(self.stack, idx)
        return Cipher(v)

