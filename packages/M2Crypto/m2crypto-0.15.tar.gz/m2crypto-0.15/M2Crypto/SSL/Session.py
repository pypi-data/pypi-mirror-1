"""Copyright (c) 1999-2003 Ng Pheng Siong. All rights reserved."""

RCS_id='$Id: Session.py 299 2005-06-09 17:32:28Z heikki $'

from M2Crypto import BIO, Err, m2

class Session:
    def __init__(self, session, _pyfree=0):
        assert session is not None
        self.session = session
        self._pyfree = _pyfree

    def __del__(self):
        if self._pyfree:
            m2.ssl_session_free(self.session)

    def _ptr(self):
        return self.session

    def as_text(self):
        buf = BIO.MemoryBuffer()
        m2.ssl_session_print(buf.bio_ptr(), self.session)
        return buf.read_all()

    def as_der(self):
        buf = BIO.MemoryBuffer()
        m2.i2d_ssl_session(buf.bio_ptr(), self.session)
        return buf.read_all()

    def write_bio(self, bio):
        return m2.ssl_session_write_bio(bio.bio_ptr(), self.session)

    def get_time(self):
        return m2.ssl_session_get_time(self.session)

    def set_time(self, t):
        return m2.ssl_session_set_time(self.session, t)

    def get_timeout(self):
        return m2.ssl_session_get_timeout(self.session)

    def set_timeout(self, t):
        return m2.ssl_session_set_timeout(self.session, t)


def load_session(pemfile):
    f = BIO.openfile(pemfile)
    cptr = m2.ssl_session_read_pem(f.bio_ptr())
    f.close()
    if cptr is None:
        raise Err.get_error()
    return Session(cptr, 1)


