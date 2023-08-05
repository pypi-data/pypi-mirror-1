"""M2Crypto Version Info"""

RCS_id='$Id: _version.py 312 2005-08-17 23:09:21Z heikki $'

import string
version_info = (0, 15)
version = string.join(map(lambda x: "%s" % x, version_info), ".")

