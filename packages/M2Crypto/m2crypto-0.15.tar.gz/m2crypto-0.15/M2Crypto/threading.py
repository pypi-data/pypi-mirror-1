"""M2Crypto threading support. 

Copyright (c) 1999-2003 Ng Pheng Siong. All rights reserved."""

RCS_id='$Id: threading.py 299 2005-06-09 17:32:28Z heikki $'

# M2Crypto
import m2

def init():
    m2.threading_init()

def cleanup():
    m2.threading_cleanup()

